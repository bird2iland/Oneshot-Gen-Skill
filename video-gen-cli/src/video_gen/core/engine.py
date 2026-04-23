import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from video_gen.core.errors import NetworkError, TaskTimeoutError
from video_gen.core.types import OptimizationMode, PollConfig
from video_gen.optimizers import create_optimizer
from video_gen.presets import PresetComposer, PresetRegistry, register_default_presets
from video_gen.providers import GenerationConfig, ProviderRouter, TaskStatus


@dataclass
class Config:
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None
    output_dir: Path = field(default_factory=lambda: Path("output"))


class VideoEngine:
    def __init__(
        self,
        config: Optional[Config] = None,
        poll_config: Optional[PollConfig] = None,
    ):
        self._config = config or Config()
        self._poll_config = poll_config or PollConfig()

        register_default_presets()
        self._registry = PresetRegistry()
        self._composer = PresetComposer(self._registry)

        self._optimizer = create_optimizer(
            mode=OptimizationMode.FAST,
            llm_api_key=self._config.llm_api_key,
            llm_model=self._config.llm_model,
            llm_base_url=self._config.llm_base_url,
        )

        self._router = ProviderRouter()
        from video_gen.providers import JimengProvider
        self._router.register("jimeng", JimengProvider())

    async def generate(
        self,
        images: list[str],
        visual_preset: Optional[str] = None,
        time_preset: Optional[str] = None,
        camera_preset: Optional[str] = None,
        description: str = "",
        mode: OptimizationMode = OptimizationMode.FAST,
        provider: str = "jimeng",
        output_dir: Optional[Path] = None,
        duration: float = 5.0,
        ratio: str = "16:9",
        model: Optional[str] = None,
        poll_config: Optional[PollConfig] = None,
    ) -> dict[str, Any]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_output_dir = output_dir or self._config.output_dir
        prompt_dir = base_output_dir / "prompts"
        video_dir = base_output_dir / "videos"

        prompt_dir.mkdir(parents=True, exist_ok=True)
        video_dir.mkdir(parents=True, exist_ok=True)

        prompt_filename = f"prompt_{timestamp}.txt"
        prompt_path = prompt_dir / prompt_filename
        video_filename = f"video_{timestamp}.mp4"
        video_path = video_dir / video_filename

        used_poll_config = poll_config or self._poll_config

        try:
            composed_prompt = await self._composer.compose(
                visual=visual_preset,
                time=time_preset,
                camera=camera_preset,
                description=description,
            )
        except Exception as e:
            return self._error_result(
                error=str(e),
                error_code="PROMPT_COMPOSITION_ERROR",
                suggestion="Failed to compose prompt from presets",
            )

        try:
            if mode != OptimizationMode.FAST:
                self._optimizer = create_optimizer(
                    mode=mode,
                    llm_api_key=self._config.llm_api_key,
                    llm_model=self._config.llm_model,
                    llm_base_url=self._config.llm_base_url,
                )

            optimized_prompt = await self._optimizer.optimize(
                composed_prompt,
                context={
                    "images": images,
                    "visual_preset": visual_preset,
                    "time_preset": time_preset,
                    "camera_preset": camera_preset,
                    "duration": duration,
                    "ratio": ratio,
                },
            )
        except Exception as e:
            return self._error_result(
                error=str(e),
                error_code="PROMPT_OPTIMIZATION_ERROR",
                suggestion="Failed to optimize prompt",
            )

        try:
            prompt_path.write_text(optimized_prompt, encoding="utf-8")
        except Exception as e:
            return self._error_result(
                error=str(e),
                error_code="PROMPT_SAVE_ERROR",
                suggestion=f"Failed to save prompt to {prompt_path}",
            )

        try:
            provider_instance = self._router.resolve(provider)
        except Exception as e:
            return self._error_result(
                error=str(e),
                error_code="PROVIDER_ERROR",
                suggestion=f"Failed to resolve provider: {provider}",
            )

        try:
            gen_config = GenerationConfig(
                images=images,
                prompt=optimized_prompt,
                duration=int(duration),
                ratio=ratio,
                model=model or "seedance2.0",
            )

            gen_result = await provider_instance.generate(gen_config)

            if not gen_result.success:
                return {
                    "success": False,
                    "video_path": None,
                    "prompt_path": str(prompt_path),
                    "task_id": gen_result.task_id,
                    "error": gen_result.error,
                    "error_code": gen_result.error_code,
                    "suggestion": gen_result.suggestion,
                }

            task_id = gen_result.task_id
            if not task_id:
                return self._error_result(
                    error="No task ID returned from provider",
                    error_code="NO_TASK_ID",
                    suggestion="Provider did not return a task ID",
                )

        except Exception as e:
            return self._error_result(
                error=str(e),
                error_code="GENERATION_ERROR",
                suggestion="Failed to submit generation task",
            )

        try:
            status = await self._poll_task(
                provider_instance=provider_instance,
                task_id=task_id,
                poll_config=used_poll_config,
            )

            if status == TaskStatus.SUCCEEDED:
                video_url = gen_result.video_path
                if video_url:
                    await provider_instance.download_video(video_url, video_path)

                    return {
                        "success": True,
                        "video_path": str(video_path),
                        "prompt_path": str(prompt_path),
                        "task_id": task_id,
                        "error": None,
                        "error_code": None,
                        "suggestion": None,
                    }
                else:
                    return {
                        "success": False,
                        "video_path": None,
                        "prompt_path": str(prompt_path),
                        "task_id": task_id,
                        "error": "No video URL returned",
                        "error_code": "NO_VIDEO_URL",
                        "suggestion": "Task succeeded but no video URL was provided",
                    }
            else:
                return {
                    "success": False,
                    "video_path": None,
                    "prompt_path": str(prompt_path),
                    "task_id": task_id,
                    "error": f"Task failed with status: {status.value}",
                    "error_code": "TASK_FAILED",
                    "suggestion": (
                        "Generation task failed, please check your input and try again"
                    ),
                }

        except TaskTimeoutError as e:
            return {
                "success": False,
                "video_path": None,
                "prompt_path": str(prompt_path),
                "task_id": task_id,
                "error": str(e),
                "error_code": e.code,
                "suggestion": f"Task timed out. Use 'task status {task_id}' to check status later",
            }
        except NetworkError as e:
            return {
                "success": False,
                "video_path": None,
                "prompt_path": str(prompt_path),
                "task_id": task_id,
                "error": str(e),
                "error_code": e.code,
                "suggestion": e.suggestion,
            }
        except Exception as e:
            return self._error_result(
                error=str(e),
                error_code="POLLING_ERROR",
                suggestion="An error occurred while polling task status",
            )

    async def _poll_task(
        self,
        provider_instance: Any,
        task_id: str,
        poll_config: PollConfig,
    ) -> TaskStatus:
        elapsed = 0.0
        interval = poll_config.interval

        while elapsed < poll_config.max_wait:
            try:
                status = await provider_instance.check_status_with_retry(
                    task_id=task_id,
                    retry_count=poll_config.retry_count,
                    retry_interval=poll_config.retry_interval,
                )

                if status == TaskStatus.SUCCEEDED:
                    return TaskStatus.SUCCEEDED
                elif status == TaskStatus.FAILED:
                    return TaskStatus.FAILED

                await asyncio.sleep(interval)
                elapsed += interval

            except Exception as e:
                raise NetworkError(f"Failed to check task status: {str(e)}")

        raise TaskTimeoutError(task_id=task_id, wait_time=poll_config.max_wait)

    def _error_result(
        self,
        error: str,
        error_code: str,
        suggestion: str,
    ) -> dict[str, Any]:
        return {
            "success": False,
            "video_path": None,
            "prompt_path": None,
            "task_id": None,
            "error": error,
            "error_code": error_code,
            "suggestion": suggestion,
        }
