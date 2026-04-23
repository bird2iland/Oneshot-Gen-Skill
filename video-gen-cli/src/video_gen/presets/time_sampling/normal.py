from typing import Any

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset


class NormalPreset(BasePreset):
    dimension = PresetDimension.TIME
    config = PresetConfig(
        id="normal",
        name="Normal Speed",
        description="Normal speed time sampling",
        keywords=["normal speed", "standard playback"],
        template="{description}, normal speed playback",
        metadata={"category": "time", "speed_multiplier": "1x"},
    )

    async def apply(self, context: dict[str, Any]) -> str:
        description = context.get("description", "")
        return self.config.template.format(description=description)

    def get_keywords(self) -> list[str]:
        return self.config.keywords