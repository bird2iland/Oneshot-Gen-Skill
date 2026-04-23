from typing import Any

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset


class ShuttlePreset(BasePreset):
    dimension = PresetDimension.CAMERA
    config = PresetConfig(
        id="shuttle",
        name="Shuttle Cam",
        description="Fast shuttle camera movement",
        keywords=["shuttle cam", "fast movement", "dynamic", "speed"],
        template="{description}, shuttle camera movement, fast dynamic motion",
        metadata={"category": "camera", "movement_type": "fast"},
    )

    async def apply(self, context: dict[str, Any]) -> str:
        description = context.get("description", "")
        return self.config.template.format(description=description)

    def get_keywords(self) -> list[str]:
        return self.config.keywords