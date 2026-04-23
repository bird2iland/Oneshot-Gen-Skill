from typing import Any

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset


class OilPaintingPreset(BasePreset):
    dimension = PresetDimension.VISUAL
    config = PresetConfig(
        id="oil_painting",
        name="Oil Painting",
        description="Artistic oil painting visual style",
        keywords=["oil painting", "artistic", "painterly", "expressive"],
        template="{description}, oil painting style, artistic rendering",
        metadata={"category": "visual", "intensity": "high"},
    )

    async def apply(self, context: dict[str, Any]) -> str:
        description = context.get("description", "")
        return self.config.template.format(description=description)

    def get_keywords(self) -> list[str]:
        return self.config.keywords