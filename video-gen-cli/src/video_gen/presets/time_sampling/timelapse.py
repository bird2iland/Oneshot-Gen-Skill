from typing import Any

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset


class TimelapsePreset(BasePreset):
    dimension = PresetDimension.TIME
    config = PresetConfig(
        id="timelapse",
        name="Timelapse",
        description="Time-lapse effect showing time passing quickly",
        keywords=["timelapse", "time passing", "accelerated time", "fast forward"],
        template="{description}, timelapse effect, time passing rapidly",
        metadata={"category": "time", "speed_multiplier": "10x"},
    )

    async def apply(self, context: dict[str, Any]) -> str:
        description = context.get("description", "")
        return self.config.template.format(description=description)

    def get_keywords(self) -> list[str]:
        return self.config.keywords