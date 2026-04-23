import asyncio
import os
from pathlib import Path
from typing import Any, Optional

import httpx

from video_gen.core.errors import NetworkError
from video_gen.core.types import GenerationResult

from .base import BaseProvider, GenerationConfig, ProviderInfo, TaskStatus


SUPPORTED_RATIOS = ["16:9", "9:16", "1:1"]
SUPPORTED_MODELS = [
    "kling/kling-v3-video-generation",
    "kling/kling-v3-omni-video-generation",
]
MIN_DURATION = 3
MAX_DURATION = 15
MAX_IMAGES = 7
API_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"


class KlingProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def name(self) -> str:
        return "kling"

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="kling",
            display_name="Kling Video Generator",
            description="Video generation using Kling API via Alibaba Cloud Bailian",
            supported_ratios=SUPPORTED_RATIOS.copy(),
            supported_models=SUPPORTED_MODELS.copy(),
            min_duration=MIN_DURATION,
            max_duration=MAX_DURATION,
            max_images=MAX_IMAGES,
        )

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=300.0)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _validate_config(self, config: GenerationConfig) -> None:
        if len(config.images) > MAX_IMAGES:
            raise ValueError(f"Maximum {MAX_IMAGES} images allowed, got {len(config.images)}")

        if config.duration < MIN_DURATION or config.duration > MAX_DURATION:
            raise ValueError(
                f"Duration must be between {MIN_DURATION} and {MAX_DURATION} seconds, got {config.duration}"
            )

        if config.ratio not in SUPPORTED_RATIOS:
            raise ValueError(
                f"Unsupported ratio: {config.ratio}. Supported: {', '.join(SUPPORTED_RATIOS)}"
            )

    def _map_task_status(self, status: str) -> TaskStatus:
        status_map = {
            "PENDING": TaskStatus.PENDING,
            "RUNNING": TaskStatus.RUNNING,
            "SUCCEEDED": TaskStatus.SUCCEEDED,
            "FAILED": TaskStatus.FAILED,
            "CANCELED": TaskStatus.FAILED,
            "UNKNOWN": TaskStatus.UNKNOWN,
        }
        return status_map.get(status.upper(), TaskStatus.UNKNOWN)

    def _build_request_payload(self, config: GenerationConfig) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": config.model or "kling/kling-v3-video-generation",
            "input": {},
            "parameters": {
                "mode": "std",
                "duration": config.duration,
                "audio": False,
                "watermark": False,
            },
        }

        if config.prompt:
            payload["input"]["prompt"] = config.prompt

        if config.images:
            media = []
            for i, img_url in enumerate(config.images):
                if i == 0:
                    media.append({"type": "first_frame", "url": img_url})
                elif i == 1:
                    media.append({"type": "last_frame", "url": img_url})
                else:
                    media.append({"type": "refer", "url": img_url})
            payload["input"]["media"] = media
        else:
            payload["parameters"]["aspect_ratio"] = config.ratio

        return payload

    async def is_available(self) -> bool:
        return self._api_key is not None and len(self._api_key) > 0

    async def generate(self, config: GenerationConfig) -> GenerationResult:
        if not self._api_key:
            return GenerationResult(
                success=False,
                error="DASHSCOPE_API_KEY not configured",
                error_code="API_KEY_MISSING",
                suggestion="Set DASHSCOPE_API_KEY environment variable or pass api_key to KlingProvider",
            )

        try:
            self._validate_config(config)
        except ValueError as e:
            return GenerationResult(
                success=False,
                error=str(e),
                error_code="INVALID_PARAMETER",
                suggestion="Check your generation parameters",
            )

        client = self._get_client()
        url = f"{API_BASE_URL}/services/aigc/video-generation/video-synthesis"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "X-DashScope-Async": "enable",
            "Content-Type": "application/json",
        }
        payload = self._build_request_payload(config)

        try:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code == 401:
                return GenerationResult(
                    success=False,
                    error="Invalid API key",
                    error_code="AUTH_FAILED",
                    suggestion="Check your DASHSCOPE_API_KEY",
                )

            if response.status_code == 429:
                return GenerationResult(
                    success=False,
                    error="Rate limit exceeded",
                    error_code="RATE_LIMIT",
                    suggestion="Wait and retry later",
                )

            response.raise_for_status()
            data = response.json()

            output = data.get("output", {})
            task_id = output.get("task_id")
            task_status = output.get("task_status", "UNKNOWN")

            if not task_id:
                return GenerationResult(
                    success=False,
                    error="No task_id returned from API",
                    error_code="API_ERROR",
                    suggestion="API response did not include task_id",
                )

            return GenerationResult(
                success=True,
                task_id=task_id,
                error=None if task_status in ["PENDING", "RUNNING"] else f"Task status: {task_status}",
            )

        except httpx.HTTPStatusError as e:
            return GenerationResult(
                success=False,
                error=f"HTTP error: {e.response.status_code}",
                error_code="HTTP_ERROR",
                suggestion="Check network connection and API endpoint",
            )
        except httpx.RequestError as e:
            return GenerationResult(
                success=False,
                error=f"Request error: {str(e)}",
                error_code="NETWORK_ERROR",
                suggestion="Check network connection",
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                error_code="UNKNOWN_ERROR",
                suggestion="An unexpected error occurred",
            )

    async def check_status(self, task_id: str) -> TaskStatus:
        if not self._api_key:
            raise NetworkError("API key not configured")

        client = self._get_client()
        url = f"{API_BASE_URL}/tasks/{task_id}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            output = data.get("output", {})
            status = output.get("task_status", "UNKNOWN")
            return self._map_task_status(status)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return TaskStatus.UNKNOWN
            raise NetworkError(f"HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise NetworkError(f"Request error: {str(e)}")

    async def get_task_result(self, task_id: str) -> dict[str, Any]:
        if not self._api_key:
            raise NetworkError("API key not configured")

        client = self._get_client()
        url = f"{API_BASE_URL}/tasks/{task_id}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    async def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 15.0,
        max_wait: float = 600.0,
    ) -> GenerationResult:
        start_time = asyncio.get_event_loop().time()

        while True:
            status = await self.check_status(task_id)

            if status == TaskStatus.SUCCEEDED:
                try:
                    result = await self.get_task_result(task_id)
                    output = result.get("output", {})
                    video_url = output.get("video_url")
                    return GenerationResult(
                        success=True,
                        task_id=task_id,
                        video_path=video_url,
                    )
                except Exception as e:
                    return GenerationResult(
                        success=False,
                        task_id=task_id,
                        error=f"Failed to get result: {str(e)}",
                        error_code="RESULT_ERROR",
                    )

            if status == TaskStatus.FAILED:
                try:
                    result = await self.get_task_result(task_id)
                    output = result.get("output", {})
                    error_msg = output.get("message", "Task failed")
                    error_code = output.get("code", "TASK_FAILED")
                    return GenerationResult(
                        success=False,
                        task_id=task_id,
                        error=error_msg,
                        error_code=error_code,
                    )
                except Exception:
                    return GenerationResult(
                        success=False,
                        task_id=task_id,
                        error="Task failed",
                        error_code="TASK_FAILED",
                    )

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= max_wait:
                return GenerationResult(
                    success=False,
                    task_id=task_id,
                    error="Timeout waiting for task completion",
                    error_code="TIMEOUT",
                    suggestion=f"Task did not complete within {max_wait} seconds",
                )

            await asyncio.sleep(poll_interval)

    async def download_video(self, url: str, output_path: Path) -> Path:
        client = self._get_client()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            response = await client.get(url)
            response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"Failed to download video: HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            raise NetworkError(f"Download failed: {str(e)}")