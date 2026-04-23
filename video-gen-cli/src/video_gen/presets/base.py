from abc import ABC, abstractmethod
from typing import Any

from video_gen.core.types import PresetConfig, PresetDimension


class BasePreset(ABC):
    dimension: PresetDimension
    config: PresetConfig

    @abstractmethod
    async def apply(self, context: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def get_keywords(self) -> list[str]:
        pass