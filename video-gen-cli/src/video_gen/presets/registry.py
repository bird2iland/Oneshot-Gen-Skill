from typing import Optional

from video_gen.core.types import PresetDimension
from video_gen.presets.base import BasePreset


class PresetRegistry:
    _instance: Optional["PresetRegistry"] = None

    def __new__(cls) -> "PresetRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._presets: dict[PresetDimension, dict[str, BasePreset]] = {
                PresetDimension.VISUAL: {},
                PresetDimension.TIME: {},
                PresetDimension.CAMERA: {},
            }
            cls._instance._custom_ids: set[str] = set()
        return cls._instance

    def register(self, preset: BasePreset, is_custom: bool = False) -> None:
        self._presets[preset.dimension][preset.config.id] = preset
        if is_custom:
            self._custom_ids.add(preset.config.id)

    def is_custom(self, preset_id: str) -> bool:
        return preset_id in self._custom_ids

    def get(self, dimension: PresetDimension, preset_id: str) -> Optional[BasePreset]:
        return self._presets.get(dimension, {}).get(preset_id)

    def list(self, dimension: PresetDimension) -> list[BasePreset]:
        return list(self._presets.get(dimension, {}).values())

    def list_ids(self, dimension: PresetDimension) -> list[str]:
        return list(self._presets.get(dimension, {}).keys())