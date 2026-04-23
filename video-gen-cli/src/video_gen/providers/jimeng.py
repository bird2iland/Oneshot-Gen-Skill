import asyncio
import json
import re
import shutil
from pathlib import Path
from typing import Any, Optional

from video_gen.core.errors import (
    InvalidParameterError,
    JimengNotInstalledError,
    JimengNotLoggedInError,
    NetworkError,
    TaskTimeoutError,
)
from video_gen.core.types import GenerationResult

from .base import BaseProvider, GenerationConfig, ProviderInfo, TaskStatus
from .jimeng_status import JimengStatusChecker


SUPPORTED_RATIOS = ["1:1", "3:4", "16:9", "4:3", "9:16", "21:9"]
SUPPORTED_MODELS = [
    "seedance2.0",
    "seedance2.0fast",
    "seedance2.0_vip",
    "seedance2.0fast_vip",
]
MIN_DURATION = 4
MAX_DURATION = 15
MAX_IMAGES = 9


class JimengProvider(BaseProvider):
    def __init__(self, cli_path: Optional[str] = None):
        self._cli_path = cli_path
        self._status_checker = JimengStatusChecker(cli_path)

    @property
    def name(self) -> str:
        return "jimeng"

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="jimeng",
            display_name="Jimeng Video Generator",
            description="Video generation using Jimeng CLI tool",
            supported_ratios=SUPPORTED_RATIOS.copy(),
            supported_models=SUPPORTED_MODELS.copy(),
            min_duration=MIN_DURATION,
            max_duration=MAX_DURATION,
            max_images=MAX_IMAGES,
        )

    def _find_jimeng_cli(self) -> Optional[str]:
        if self._cli_path:
            return self._cli_path
        # dreamina 是即梦 CLI 的实际名称
        return shutil.which("dreamina") or shutil.which("jimeng")

    def _validate_config(self, config: GenerationConfig) -> None:
        if len(config.images) > MAX_IMAGES:
            raise InvalidParameterError(
                "images",
                str(len(config.images)),
                f"Maximum {MAX_IMAGES} images allowed",
            )

        if config.duration < MIN_DURATION or config.duration > MAX_DURATION:
            raise InvalidParameterError(
                "duration",
                str(config.duration),
                f"Duration must be between {MIN_DURATION} and {MAX_DURATION} seconds",
            )

        if config.ratio not in SUPPORTED_RATIOS:
            raise InvalidParameterError(
                "ratio",
                config.ratio,
                f"Supported ratios: {', '.join(SUPPORTED_RATIOS)}",
            )

        if config.model not in SUPPORTED_MODELS:
            raise InvalidParameterError(
                "model",
                config.model,
                f"Supported models: {', '.join(SUPPORTED_MODELS)}",
            )

    def _build_cli_args(self, config: GenerationConfig) -> list[str]:
        args = ["multimodal2video"]

        for image in config.images:
            args.extend(["--image", str(image)])

        if config.prompt:
            args.extend(["--prompt", config.prompt])

        args.extend(["--duration", str(config.duration)])
        args.extend(["--ratio", config.ratio])
        args.extend(["--model_version", config.model])
        
        # 添加轮询等待
        args.extend(["--poll", "120"])

        return args

    def _parse_cli_output(self, output: str) -> dict[str, Any]:
        output = output.strip()

        json_match = re.search(r"\{[\s\S]*\}", output)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        result: dict[str, Any] = {}

        task_id_match = re.search(r"task[_-]?id[:\s]+([a-zA-Z0-9-]+)", output, re.IGNORECASE)
        if task_id_match:
            result["task_id"] = task_id_match.group(1)

        status_match = re.search(r"status[:\s]+(\w+)", output, re.IGNORECASE)
        if status_match:
            result["status"] = status_match.group(1).lower()

        video_match = re.search(r"(?:video|url)[:\s]+(https?://[^\s]+)", output, re.IGNORECASE)
        if video_match:
            result["video_url"] = video_match.group(1)

        error_match = re.search(r"error[:\s]+(.+?)(?:\n|$)", output, re.IGNORECASE)
        if error_match:
            result["error"] = error_match.group(1).strip()

        return result

    async def is_available(self) -> bool:
        status = await self._status_checker.check_full_status()
        return status.installed and status.logged_in

    async def generate(self, config: GenerationConfig) -> GenerationResult:
        self._validate_config(config)

        cli_path = self._find_jimeng_cli()
        if not cli_path:
            return GenerationResult(
                success=False,
                error="Jimeng CLI not found",
                error_code="JIMENG_NOT_INSTALLED",
                suggestion=self._status_checker.get_install_guide(),
            )

        status = await self._status_checker.check_full_status()
        if not status.installed:
            return GenerationResult(
                success=False,
                error="Jimeng CLI not installed",
                error_code="JIMENG_NOT_INSTALLED",
                suggestion=self._status_checker.get_install_guide(),
            )

        if not status.logged_in:
            return GenerationResult(
                success=False,
                error="User not logged in to Jimeng",
                error_code="JIMENG_NOT_LOGGED_IN",
                suggestion="Please run 'jimeng auth login' to authenticate",
            )

        args = self._build_cli_args(config)

        try:
            process = await asyncio.create_subprocess_exec(
                cli_path,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()
            output = stdout.decode("utf-8", errors="ignore")
            error_output = stderr.decode("utf-8", errors="ignore")

            if process.returncode != 0:
                return GenerationResult(
                    success=False,
                    error=error_output or output or "Unknown error",
                    error_code="GENERATION_FAILED",
                    suggestion="Please check your input parameters and try again",
                )

            parsed = self._parse_cli_output(output)

            if parsed.get("error"):
                return GenerationResult(
                    success=False,
                    error=parsed.get("error", "Unknown error"),
                    error_code="GENERATION_FAILED",
                    suggestion="Please check the error message and try again",
                )

            return GenerationResult(
                success=True,
                task_id=parsed.get("task_id"),
                video_path=parsed.get("video_url"),
            )

        except FileNotFoundError:
            raise JimengNotInstalledError()
        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e),
                error_code="GENERATION_ERROR",
                suggestion="An unexpected error occurred during video generation",
            )

    async def check_status(self, task_id: str) -> TaskStatus:
        cli_path = self._find_jimeng_cli()
        if not cli_path:
            raise JimengNotInstalledError()

        try:
            process = await asyncio.create_subprocess_exec(
                cli_path,
                "task",
                "status",
                task_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()
            output = stdout.decode("utf-8", errors="ignore").lower()

            if "succeeded" in output or "completed" in output or "success" in output:
                return TaskStatus.SUCCEEDED
            elif "failed" in output or "error" in output:
                return TaskStatus.FAILED
            elif "running" in output or "processing" in output:
                return TaskStatus.RUNNING
            elif "pending" in output or "queued" in output:
                return TaskStatus.PENDING
            else:
                return TaskStatus.UNKNOWN

        except FileNotFoundError:
            raise JimengNotInstalledError()
        except Exception as e:
            raise NetworkError(str(e))

    async def download_video(self, url: str, output_path: Path) -> Path:
        import httpx

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(response.content)

            return output_path

        except httpx.HTTPStatusError as e:
            raise NetworkError(f"Failed to download video: HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            raise NetworkError(f"Download failed: {str(e)}")