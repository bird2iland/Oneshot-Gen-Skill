from typing import Optional

from video_gen.core.types import PresetDimension
from video_gen.presets.base import BasePreset
from video_gen.presets.registry import PresetRegistry


class PresetComposer:
    def __init__(self, registry: Optional[PresetRegistry] = None):
        self._registry = registry or PresetRegistry()

    async def compose(
        self,
        visual: Optional[str],
        time: Optional[str],
        camera: Optional[str],
        description: str,
    ) -> str:
        parts: list[str] = []

        if visual:
            preset = self._registry.get(PresetDimension.VISUAL, visual)
            if preset:
                parts.append(" ".join(preset.get_keywords()))

        if time:
            preset = self._registry.get(PresetDimension.TIME, time)
            if preset:
                parts.append(" ".join(preset.get_keywords()))

        if camera:
            preset = self._registry.get(PresetDimension.CAMERA, camera)
            if preset:
                parts.append(" ".join(preset.get_keywords()))

        if description:
            parts.append(description)

        return ", ".join(parts)