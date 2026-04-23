import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, cast

import yaml

from video_gen.core.engine import Config, VideoEngine
from video_gen.core.types import OptimizationMode, PollConfig


@dataclass
class BatchTask:
    images: list[str] = field(default_factory=list)
    visual: Optional[str] = None
    time: Optional[str] = None
    camera: Optional[str] = None
    description: str = ""
    duration: float = 5.0
    ratio: str = "16:9"
    model: Optional[str] = None


@dataclass
class BatchRequest:
    tasks: list[BatchTask] = field(default_factory=list)
    concurrency: int = 3
    mode: OptimizationMode = OptimizationMode.FAST
    provider: str = "jimeng"
    output_dir: Optional[Path] = None
    continue_on_error: bool = True
    poll_config: Optional[PollConfig] = None


@dataclass
class TaskResult:
    index: int
    success: bool
    video_path: Optional[str] = None
    prompt_path: Optional[str] = None
    task_id: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None


@dataclass
class ProgressInfo:
    total: int
    completed: int
    succeeded: int
    failed: int
    current_index: int
    current_description: str


@dataclass
class BatchResult:
    success: bool
    total: int
    succeeded: int
    failed: int
    results: list[TaskResult] = field(default_factory=list)
    duration: float = 0.0


ProgressCallback = Callable[[ProgressInfo], None]


class BatchEngine:
    def __init__(self, config: Optional[Config] = None):
        self._config = config or Config()
        self._engine = VideoEngine(config=self._config)

    def from_yaml(self, yaml_path: Path) -> BatchRequest:
        if not yaml_path.exists():
            raise FileNotFoundError(f"Batch config file not found: {yaml_path}")

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "tasks" not in data:
            raise ValueError("Invalid batch config: 'tasks' field is required")

        tasks: list[BatchTask] = []
        for i, task_data in enumerate(data["tasks"]):
            if not isinstance(task_data, dict):
                raise ValueError(f"Invalid task at index {i}: expected dict")

            images = task_data.get("images", [])
            if isinstance(images, str):
                images = [images]

            task = BatchTask(
                images=images,
                visual=task_data.get("visual"),
                time=task_data.get("time"),
                camera=task_data.get("camera"),
                description=task_data.get("description", ""),
                duration=task_data.get("duration", 5.0),
                ratio=task_data.get("ratio", "16:9"),
                model=task_data.get("model"),
            )
            tasks.append(task)

        mode_str = data.get("mode", "fast")
        is_quality = mode_str.lower() == "quality"
        mode = OptimizationMode.QUALITY if is_quality else OptimizationMode.FAST

        output_dir = data.get("output_dir")
        if output_dir:
            output_dir = Path(output_dir)

        return BatchRequest(
            tasks=tasks,
            concurrency=data.get("concurrency", 3),
            mode=mode,
            provider=data.get("provider", "jimeng"),
            output_dir=output_dir,
            continue_on_error=data.get("continue_on_error", True),
        )

    async def execute_batch(
        self,
        request: BatchRequest,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> BatchResult:
        start_time = time.time()
        results: list[TaskResult] = []
        completed = 0
        succeeded = 0
        failed = 0

        semaphore = asyncio.Semaphore(request.concurrency)

        async def execute_task(index: int, task: BatchTask) -> TaskResult:
            nonlocal completed, succeeded, failed

            async with semaphore:
                if progress_callback:
                    progress_callback(ProgressInfo(
                        total=len(request.tasks),
                        completed=completed,
                        succeeded=succeeded,
                        failed=failed,
                        current_index=index,
                        current_description=task.description,
                    ))

                try:
                    result = await self._engine.generate(
                        images=task.images,
                        visual_preset=task.visual,
                        time_preset=task.time,
                        camera_preset=task.camera,
                        description=task.description,
                        mode=request.mode,
                        provider=request.provider,
                        output_dir=request.output_dir,
                        duration=task.duration,
                        ratio=task.ratio,
                        model=task.model,
                        poll_config=request.poll_config,
                    )

                    task_result = TaskResult(
                        index=index,
                        success=result.get("success", False),
                        video_path=result.get("video_path"),
                        prompt_path=result.get("prompt_path"),
                        task_id=result.get("task_id"),
                        error=result.get("error"),
                        error_code=result.get("error_code"),
                    )

                except Exception as e:
                    task_result = TaskResult(
                        index=index,
                        success=False,
                        error=str(e),
                        error_code="TASK_EXCEPTION",
                    )

                completed += 1
                if task_result.success:
                    succeeded += 1
                else:
                    failed += 1

                return task_result

        try:
            if request.continue_on_error:
                task_coroutines = [
                    execute_task(i, task) for i, task in enumerate(request.tasks)
                ]
                raw_results = await asyncio.gather(
                    *task_coroutines, return_exceptions=True
                )

                processed_results: list[TaskResult] = []
                for i, r in enumerate(raw_results):
                    if isinstance(r, Exception):
                        processed_results.append(TaskResult(
                            index=i,
                            success=False,
                            error=str(r),
                            error_code="TASK_EXCEPTION",
                        ))
                        failed += 1
                    else:
                        processed_results.append(cast(TaskResult, r))

                results = sorted(processed_results, key=lambda x: x.index)

            else:
                for i, task in enumerate(request.tasks):
                    result = await execute_task(i, task)
                    results.append(result)

                    if not result.success:
                        break

        except Exception:
            end_time = time.time()
            return BatchResult(
                success=False,
                total=len(request.tasks),
                succeeded=succeeded,
                failed=failed,
                results=results,
                duration=end_time - start_time,
            )

        end_time = time.time()
        return BatchResult(
            success=failed == 0,
            total=len(request.tasks),
            succeeded=succeeded,
            failed=failed,
            results=results,
            duration=end_time - start_time,
        )