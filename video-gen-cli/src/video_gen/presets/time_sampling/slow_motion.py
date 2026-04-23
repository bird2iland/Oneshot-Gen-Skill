from typing import Any

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset


class SlowMotionPreset(BasePreset):
    dimension = PresetDimension.TIME
    config = PresetConfig(
        id="slow_motion",
        name="Slow Motion",
        description="Slow motion effect for smooth detailed playback",
        keywords=["slow motion", "smooth", "slo-mo", "detailed motion"],
        template="{description}, slow motion effect, smooth playback",
        metadata={"category": "time", "speed_multiplier": "0.25x"},
    )

    async def apply(self, context: dict[str, Any]) -> str:
        description = context.get("description", "")
        return self.config.template.format(description=description)

    def get_keywords(self) -> list[str]:
        return self.config.keywords