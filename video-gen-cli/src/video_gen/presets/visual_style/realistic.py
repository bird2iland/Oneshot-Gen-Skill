from typing import Any

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset


class RealisticPreset(BasePreset):
    dimension = PresetDimension.VISUAL
    config = PresetConfig(
        id="realistic",
        name="Realistic",
        description="Photorealistic visual style with high detail",
        keywords=["photorealistic", "detailed", "realistic", "high fidelity"],
        template="{description}, photorealistic style, highly detailed",
        metadata={"category": "visual", "intensity": "high"},
    )

    async def apply(self, context: dict[str, Any]) -> str:
        description = context.get("description", "")
        return self.config.template.format(description=description)

    def get_keywords(self) -> list[str]:
        return self.config.keywords