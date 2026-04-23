from video_gen.presets.base import BasePreset
from video_gen.presets.registry import PresetRegistry
from video_gen.presets.composer import PresetComposer
from video_gen.presets.validator import PresetCombinationValidator
from video_gen.presets.custom_loader import CustomPreset, CustomPresetLoader
from video_gen.presets.visual_style import RealisticPreset, PixelArtPreset, OilPaintingPreset
from video_gen.presets.time_sampling import TimelapsePreset, SlowMotionPreset, NormalPreset
from video_gen.presets.camera_movement import ShuttlePreset, GimbalPreset, HandheldPreset

__all__ = [
    "BasePreset",
    "PresetRegistry",
    "PresetComposer",
    "PresetCombinationValidator",
    "CustomPreset",
    "CustomPresetLoader",
    "RealisticPreset",
    "PixelArtPreset",
    "OilPaintingPreset",
    "TimelapsePreset",
    "SlowMotionPreset",
    "NormalPreset",
    "ShuttlePreset",
    "GimbalPreset",
    "HandheldPreset",
    "register_default_presets",
]


def register_default_presets() -> None:
    registry = PresetRegistry()
    registry.register(RealisticPreset())
    registry.register(PixelArtPreset())
    registry.register(OilPaintingPreset())
    registry.register(TimelapsePreset())
    registry.register(SlowMotionPreset())
    registry.register(NormalPreset())
    registry.register(ShuttlePreset())
    registry.register(GimbalPreset())
    registry.register(HandheldPreset())