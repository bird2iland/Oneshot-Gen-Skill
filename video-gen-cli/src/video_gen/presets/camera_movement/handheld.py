from typing import Any

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset


class HandheldPreset(BasePreset):
    dimension = PresetDimension.CAMERA
    config = PresetConfig(
        id="handheld",
        name="Handheld",
        description="Natural handheld camera movement",
        keywords=["handheld", "natural", "organic", "documentary style"],
        template="{description}, handheld camera movement, natural feel",
        metadata={"category": "camera", "movement_type": "natural"},
    )

    async def apply(self, context: dict[str, Any]) -> str:
        description = context.get("description", "")
        return self.config.template.format(description=description)

    def get_keywords(self) -> list[str]:
        return self.config.keywords