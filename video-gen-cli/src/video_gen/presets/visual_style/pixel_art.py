from typing import Any

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset


class PixelArtPreset(BasePreset):
    dimension = PresetDimension.VISUAL
    config = PresetConfig(
        id="pixel_art",
        name="Pixel Art",
        description="Retro pixel art visual style",
        keywords=["pixel art", "retro", "8-bit", "nostalgic"],
        template="{description}, pixel art style, retro aesthetic",
        metadata={"category": "visual", "intensity": "medium"},
    )

    async def apply(self, context: dict[str, Any]) -> str:
        description = context.get("description", "")
        return self.config.template.format(description=description)

    def get_keywords(self) -> list[str]:
        return self.config.keywords