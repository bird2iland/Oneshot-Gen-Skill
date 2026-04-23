import pytest

from video_gen.core.types import PresetDimension
from video_gen.presets import (
    PresetRegistry,
    PresetComposer,
    PresetCombinationValidator,
    register_default_presets,
    RealisticPreset,
    PixelArtPreset,
    OilPaintingPreset,
    TimelapsePreset,
    SlowMotionPreset,
    NormalPreset,
    ShuttlePreset,
    GimbalPreset,
    HandheldPreset,
)


class TestPresetRegistrySingleton:
    def test_singleton_returns_same_instance(self, reset_registry):
        instance1 = PresetRegistry()
        instance2 = PresetRegistry()
        assert instance1 is instance2

    def test_singleton_persists_data(self, reset_registry, mock_visual_preset):
        registry1 = PresetRegistry()
        registry1.register(mock_visual_preset)
        registry2 = PresetRegistry()
        result = registry2.get(PresetDimension.VISUAL, "test_visual")
        assert result is mock_visual_preset


class TestPresetRegistryRegister:
    def test_register_visual_preset(self, registry, mock_visual_preset):
        registry.register(mock_visual_preset)
        result = registry.get(PresetDimension.VISUAL, "test_visual")
        assert result is mock_visual_preset

    def test_register_time_preset(self, registry, mock_time_preset):
        registry.register(mock_time_preset)
        result = registry.get(PresetDimension.TIME, "test_time")
        assert result is mock_time_preset

    def test_register_camera_preset(self, registry, mock_camera_preset):
        registry.register(mock_camera_preset)
        result = registry.get(PresetDimension.CAMERA, "test_camera")
        assert result is mock_camera_preset

    def test_register_overwrites_existing(self, registry, mock_visual_preset):
        registry.register(mock_visual_preset)
        new_preset = mock_visual_preset
        new_preset.config.name = "Updated"
        registry.register(new_preset)
        result = registry.get(PresetDimension.VISUAL, "test_visual")
        assert result.config.name == "Updated"


class TestPresetRegistryGet:
    def test_get_existing_preset(self, registry, mock_visual_preset):
        registry.register(mock_visual_preset)
        result = registry.get(PresetDimension.VISUAL, "test_visual")
        assert result is mock_visual_preset

    def test_get_nonexistent_preset_returns_none(self, registry):
        result = registry.get(PresetDimension.VISUAL, "nonexistent")
        assert result is None

    def test_get_invalid_dimension_returns_none(self, registry):
        result = registry.get("invalid_dimension", "test")
        assert result is None


class TestPresetRegistryList:
    def test_list_empty_dimension(self, registry):
        result = registry.list(PresetDimension.VISUAL)
        assert result == []

    def test_list_single_preset(self, registry, mock_visual_preset):
        registry.register(mock_visual_preset)
        result = registry.list(PresetDimension.VISUAL)
        assert len(result) == 1
        assert result[0] is mock_visual_preset

    def test_list_multiple_presets(self, registry, mock_visual_preset, mock_time_preset, mock_camera_preset):
        registry.register(mock_visual_preset)
        registry.register(mock_time_preset)
        registry.register(mock_camera_preset)
        assert len(registry.list(PresetDimension.VISUAL)) == 1
        assert len(registry.list(PresetDimension.TIME)) == 1
        assert len(registry.list(PresetDimension.CAMERA)) == 1

    def test_list_ids(self, registry, mock_visual_preset):
        registry.register(mock_visual_preset)
        ids = registry.list_ids(PresetDimension.VISUAL)
        assert "test_visual" in ids


class TestPresetComposer:
    @pytest.mark.asyncio
    async def test_compose_with_all_presets(self, registry, mock_visual_preset, mock_time_preset, mock_camera_preset):
        registry.register(mock_visual_preset)
        registry.register(mock_time_preset)
        registry.register(mock_camera_preset)
        composer = PresetComposer(registry)
        result = await composer.compose(
            visual="test_visual",
            time="test_time",
            camera="test_camera",
            description="test description",
        )
        assert "visual test" in result
        assert "time test" in result
        assert "camera test" in result
        assert "test description" in result

    @pytest.mark.asyncio
    async def test_compose_with_only_description(self, registry):
        composer = PresetComposer(registry)
        result = await composer.compose(
            visual=None,
            time=None,
            camera=None,
            description="just a description",
        )
        assert result == "just a description"

    @pytest.mark.asyncio
    async def test_compose_ignores_nonexistent_presets(self, registry):
        composer = PresetComposer(registry)
        result = await composer.compose(
            visual="nonexistent",
            time=None,
            camera=None,
            description="description only",
        )
        assert "description only" in result
        assert "nonexistent" not in result

    @pytest.mark.asyncio
    async def test_compose_with_partial_presets(self, registry, mock_visual_preset):
        registry.register(mock_visual_preset)
        composer = PresetComposer(registry)
        result = await composer.compose(
            visual="test_visual",
            time=None,
            camera=None,
            description="with visual",
        )
        assert "visual test" in result
        assert "with visual" in result


class TestRegisterDefaultPresets:
    def test_registers_nine_presets(self, reset_registry):
        register_default_presets()
        registry = PresetRegistry()
        visual_ids = registry.list_ids(PresetDimension.VISUAL)
        time_ids = registry.list_ids(PresetDimension.TIME)
        camera_ids = registry.list_ids(PresetDimension.CAMERA)
        assert len(visual_ids) == 3
        assert len(time_ids) == 3
        assert len(camera_ids) == 3

    def test_registers_visual_presets(self, reset_registry):
        register_default_presets()
        registry = PresetRegistry()
        visual_ids = registry.list_ids(PresetDimension.VISUAL)
        assert "realistic" in visual_ids
        assert "pixel_art" in visual_ids
        assert "oil_painting" in visual_ids

    def test_registers_time_presets(self, reset_registry):
        register_default_presets()
        registry = PresetRegistry()
        time_ids = registry.list_ids(PresetDimension.TIME)
        assert "timelapse" in time_ids
        assert "slow_motion" in time_ids
        assert "normal" in time_ids

    def test_registers_camera_presets(self, reset_registry):
        register_default_presets()
        registry = PresetRegistry()
        camera_ids = registry.list_ids(PresetDimension.CAMERA)
        assert "shuttle" in camera_ids
        assert "gimbal" in camera_ids
        assert "handheld" in camera_ids


class TestPresetCombinationValidator:
    @pytest.mark.asyncio
    async def test_validate_no_conflicts(self):
        validator = PresetCombinationValidator(
            visual="realistic",
            time="normal",
            camera="gimbal",
        )
        warnings = await validator.validate()
        assert warnings == []

    @pytest.mark.asyncio
    async def test_validate_slow_motion_timelapse_conflict(self):
        validator = PresetCombinationValidator(
            visual=None,
            time="slow_motion",
            camera="timelapse",
        )
        warnings = await validator.validate()
        assert len(warnings) >= 1
        assert any("slow_motion" in w and "timelapse" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_validate_handheld_gimbal_conflict(self):
        validator = PresetCombinationValidator(
            visual=None,
            time="handheld",
            camera="gimbal",
        )
        warnings = await validator.validate()
        assert len(warnings) >= 1
        assert any("handheld" in w and "gimbal" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_validate_multiple_conflicts(self):
        validator = PresetCombinationValidator(
            visual="slow_motion",
            time="timelapse",
            camera="handheld",
        )
        warnings = await validator.validate()
        assert len(warnings) >= 1

    @pytest.mark.asyncio
    async def test_validate_empty_presets(self):
        validator = PresetCombinationValidator(
            visual=None,
            time=None,
            camera=None,
        )
        warnings = await validator.validate()
        assert warnings == []

    @pytest.mark.asyncio
    async def test_validate_single_preset(self):
        validator = PresetCombinationValidator(
            visual="realistic",
            time=None,
            camera=None,
        )
        warnings = await validator.validate()
        assert warnings == []