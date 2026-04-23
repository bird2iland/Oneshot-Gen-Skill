from pathlib import Path
from typing import Any, TYPE_CHECKING, Optional

import yaml

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset

if TYPE_CHECKING:
    from video_gen.presets.registry import PresetRegistry


class CustomPreset(BasePreset):
    dimension: PresetDimension
    config: PresetConfig

    def __init__(
        self,
        dimension: PresetDimension,
        config: PresetConfig,
        is_custom: bool = True,
    ):
        self.dimension = dimension
        self.config = config
        self._is_custom = is_custom

    @property
    def is_custom(self) -> bool:
        return self._is_custom

    async def apply(self, context: dict[str, Any]) -> str:
        description = context.get("description", "")
        return self.config.template.format(description=description)

    def get_keywords(self) -> list[str]:
        return self.config.keywords


class CustomPresetLoader:
    def __init__(self, config_path: Optional[Path] = None):
        self._config_path = config_path

    def load(self, registry: "PresetRegistry") -> int:
        config_path = self._get_config_path()
        if not config_path.exists():
            return 0

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            return 0

        custom_presets = data.get("custom_presets", {})
        loaded_count = 0

        dimension_map = {
            "visual": PresetDimension.VISUAL,
            "time": PresetDimension.TIME,
            "camera": PresetDimension.CAMERA,
        }

        for dimension_key, presets in custom_presets.items():
            dimension = dimension_map.get(dimension_key.lower())
            if not dimension:
                continue

            for preset_id, preset_data in presets.items():
                preset = self._create_preset(dimension, preset_id, preset_data)
                if preset:
                    registry.register(preset, is_custom=True)
                    loaded_count += 1

        return loaded_count

    def _get_config_path(self) -> Path:
        if self._config_path:
            return self._config_path
        return Path.home() / ".video_gen" / "custom_presets.yaml"

    def _create_preset(
        self,
        dimension: PresetDimension,
        preset_id: str,
        preset_data: dict[str, Any],
    ) -> Optional[CustomPreset]:
        try:
            name = preset_data.get("name", preset_id)
            description = preset_data.get("description", "")
            keywords = preset_data.get("keywords", [])
            template = preset_data.get("template", "{description}")
            metadata = preset_data.get("metadata", {})

            config = PresetConfig(
                id=preset_id,
                name=name,
                description=description,
                keywords=keywords if isinstance(keywords, list) else [],
                template=template,
                metadata=metadata if isinstance(metadata, dict) else {},
            )

            return CustomPreset(
                dimension=dimension,
                config=config,
                is_custom=True,
            )
        except Exception:
            return None

    def list_available(self) -> list[dict[str, Any]]:
        config_path = self._get_config_path()
        if not config_path.exists():
            return []

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            return []

        custom_presets = data.get("custom_presets", {})
        result = []

        dimension_map = {
            "visual": PresetDimension.VISUAL,
            "time": PresetDimension.TIME,
            "camera": PresetDimension.CAMERA,
        }

        for dimension_key, presets in custom_presets.items():
            dimension = dimension_map.get(dimension_key.lower())
            if not dimension:
                continue

            for preset_id, preset_data in presets.items():
                result.append({
                    "id": preset_id,
                    "dimension": dimension.value,
                    "name": preset_data.get("name", preset_id),
                    "description": preset_data.get("description", ""),
                    "keywords": preset_data.get("keywords", []),
                    "is_custom": True,
                })

        return result