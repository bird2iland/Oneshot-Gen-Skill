from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from video_gen.core.types import GenerationResult


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class GenerationConfig:
    images: list[str] = field(default_factory=list)
    prompt: str = ""
    duration: int = 5
    ratio: str = "16:9"
    model: str = "seedance2.0"
    output_dir: Optional[Path] = None
    task_id: Optional[str] = None


@dataclass
class ProviderInfo:
    name: str
    display_name: str
    description: str
    supported_ratios: list[str] = field(default_factory=list)
    supported_models: list[str] = field(default_factory=list)
    min_duration: int = 4
    max_duration: int = 15
    max_images: int = 9


class BaseProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def info(self) -> ProviderInfo:
        pass

    @abstractmethod
    async def generate(self, config: GenerationConfig) -> GenerationResult:
        pass

    @abstractmethod
    async def check_status(self, task_id: str) -> TaskStatus:
        pass

    async def check_status_with_retry(
        self,
        task_id: str,
        retry_count: int = 3,
        retry_interval: float = 1.0,
    ) -> TaskStatus:
        import asyncio

        last_error: Optional[Exception] = None
        for attempt in range(retry_count):
            try:
                return await self.check_status(task_id)
            except Exception as e:
                last_error = e
                if attempt < retry_count - 1:
                    await asyncio.sleep(retry_interval)
        raise last_error or Exception(f"Failed to check status for task {task_id}")

    @abstractmethod
    async def download_video(self, url: str, output_path: Path) -> Path:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass