import pytest

from video_gen.core.types import PresetConfig, PresetDimension
from video_gen.presets.base import BasePreset
from video_gen.presets.registry import PresetRegistry


class MockPreset(BasePreset):
    def __init__(self, preset_id: str, dimension: PresetDimension, keywords: list[str]):
        self.dimension = dimension
        self.config = PresetConfig(
            id=preset_id,
            name=preset_id.capitalize(),
            description=f"Mock {preset_id} preset",
            keywords=keywords,
        )

    async def apply(self, context: dict) -> str:
        return f"Applied {self.config.id}"

    def get_keywords(self) -> list[str]:
        return self.config.keywords


@pytest.fixture
def reset_registry():
    PresetRegistry._instance = None
    yield
    PresetRegistry._instance = None


@pytest.fixture
def registry(reset_registry):
    return PresetRegistry()


@pytest.fixture
def mock_visual_preset():
    return MockPreset("test_visual", PresetDimension.VISUAL, ["visual", "test"])


@pytest.fixture
def mock_time_preset():
    return MockPreset("test_time", PresetDimension.TIME, ["time", "test"])


@pytest.fixture
def mock_camera_preset():
    return MockPreset("test_camera", PresetDimension.CAMERA, ["camera", "test"])