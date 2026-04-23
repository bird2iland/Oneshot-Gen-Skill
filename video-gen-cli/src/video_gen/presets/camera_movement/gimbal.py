from typing import Any

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset


class GimbalPreset(BasePreset):
    dimension = PresetDimension.CAMERA
    config = PresetConfig(
        id="gimbal",
        name="Gimbal Shot",
        description="Smooth stabilized gimbal camera movement",
        keywords=["gimbal shot", "smooth", "stabilized", "steady"],
        template="{description}, gimbal shot, smooth stabilized movement",
        metadata={"category": "camera", "movement_type": "smooth"},
    )

    async def apply(self, context: dict[str, Any]) -> str:
        description = context.get("description", "")
        return self.config.template.format(description=description)

    def get_keywords(self) -> list[str]:
        return self.config.keywords