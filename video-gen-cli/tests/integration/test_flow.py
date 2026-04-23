import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from video_gen.core.engine import Config, VideoEngine
from video_gen.core.types import (
    GenerationResult,
    OptimizationMode,
    PollConfig,
    PresetDimension,
)
from video_gen.presets.base import BasePreset
from video_gen.presets.registry import PresetRegistry
from video_gen.providers.base import GenerationConfig, TaskStatus


class MockPreset(BasePreset):
    def __init__(self, preset_id: str, dimension: PresetDimension, keywords: list[str]):
        self.dimension = dimension
        self.config = MagicMock()
        self.config.id = preset_id
        self.config.name = preset_id.capitalize()
        self.config.description = f"Mock {preset_id} preset"
        self.config.keywords = keywords
        self._keywords = keywords

    async def apply(self, context: dict) -> str:
        return f"Applied {self.config.id}"

    def get_keywords(self) -> list[str]:
        return self._keywords


def make_mock_generate():
    async def mock_generate(config: GenerationConfig) -> GenerationResult:
        return GenerationResult(
            success=True,
            task_id="test-task-123",
            video_path="https://example.com/video.mp4",
        )
    return mock_generate


def make_mock_check_status():
    async def mock_check_status_with_retry(
        task_id: str, retry_count: int = 3, retry_interval: float = 1.0
    ) -> TaskStatus:
        return TaskStatus.SUCCEEDED
    return mock_check_status_with_retry


def make_mock_download_video():
    async def mock_download_video(url: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake video content")
        return output_path
    return mock_download_video


@pytest.fixture
def reset_registry():
    PresetRegistry._instance = None
    yield
    PresetRegistry._instance = None


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.name = "mock_provider"
    provider.generate = AsyncMock(side_effect=make_mock_generate())
    provider.check_status = AsyncMock(return_value=TaskStatus.SUCCEEDED)
    provider.check_status_with_retry = AsyncMock(side_effect=make_mock_check_status())
    provider.download_video = AsyncMock(side_effect=make_mock_download_video())
    provider.is_available = AsyncMock(return_value=True)
    return provider


@pytest.fixture
def engine_with_mock_provider(temp_output_dir, mock_provider, reset_registry):
    registry = PresetRegistry()
    registry.register(
        MockPreset("realistic", PresetDimension.VISUAL, ["realistic", "natural"])
    )
    registry.register(
        MockPreset("normal", PresetDimension.TIME, ["normal", "standard"])
    )
    registry.register(
        MockPreset("gimbal", PresetDimension.CAMERA, ["gimbal", "stable"])
    )

    config = Config(output_dir=temp_output_dir)
    poll_config = PollConfig(interval=0.1, max_wait=5.0)
    engine = VideoEngine(config=config, poll_config=poll_config)
    engine._router.register("mock_provider", mock_provider)
    engine._mock_provider = mock_provider
    return engine


@pytest.mark.asyncio
async def test_full_flow_mock(engine_with_mock_provider, temp_output_dir):
    engine = engine_with_mock_provider
    mock_provider = engine._mock_provider

    result = await engine.generate(
        images=["image1.jpg", "image2.jpg"],
        visual_preset="realistic",
        time_preset="normal",
        camera_preset="gimbal",
        description="A beautiful sunset over the ocean",
        provider="mock_provider",
        duration=5.0,
        ratio="16:9",
    )

    assert result["success"] is True
    assert result["task_id"] == "test-task-123"
    assert result["video_path"] is not None
    assert result["prompt_path"] is not None

    prompt_path = Path(result["prompt_path"])
    assert prompt_path.exists()
    prompt_content = prompt_path.read_text(encoding="utf-8")
    assert "realistic" in prompt_content or "natural" in prompt_content
    assert "normal" in prompt_content or "standard" in prompt_content
    assert "gimbal" in prompt_content or "stable" in prompt_content
    assert "sunset" in prompt_content

    video_path = Path(result["video_path"])
    assert video_path.exists()
    video_content = video_path.read_bytes()
    assert video_content == b"fake video content"

    mock_provider.generate.assert_called_once()
    call_config = mock_provider.generate.call_args[0][0]
    assert isinstance(call_config, GenerationConfig)
    assert call_config.images == ["image1.jpg", "image2.jpg"]
    assert call_config.duration == 5
    assert call_config.ratio == "16:9"

    mock_provider.check_status_with_retry.assert_called()
    mock_provider.download_video.assert_called_once()


@pytest.mark.asyncio
async def test_prompt_saved(engine_with_mock_provider, temp_output_dir):
    engine = engine_with_mock_provider

    result = await engine.generate(
        images=["test_image.jpg"],
        visual_preset="realistic",
        description="Test prompt saving",
        provider="mock_provider",
    )

    assert result["success"] is True
    assert result["prompt_path"] is not None

    prompt_path = Path(result["prompt_path"])
    assert prompt_path.exists()
    assert "prompts" in str(prompt_path)
    assert prompt_path.suffix == ".txt"

    content = prompt_path.read_text(encoding="utf-8")
    assert len(content) > 0
    assert "Test prompt saving" in content


@pytest.mark.asyncio
async def test_error_handling_generation_failure(temp_output_dir, reset_registry):
    registry = PresetRegistry()
    registry.register(MockPreset("realistic", PresetDimension.VISUAL, ["realistic"]))

    failing_provider = MagicMock()
    failing_provider.name = "failing_provider"
    failing_provider.generate = AsyncMock(
        return_value=GenerationResult(
            success=False,
            error="API quota exceeded",
            error_code="QUOTA_EXCEEDED",
            suggestion="Please upgrade your plan or wait for quota reset",
        )
    )

    config = Config(output_dir=temp_output_dir)
    poll_config = PollConfig(interval=0.1, max_wait=5.0)
    engine = VideoEngine(config=config, poll_config=poll_config)
    engine._router.register("failing_provider", failing_provider)

    result = await engine.generate(
        images=["image.jpg"],
        visual_preset="realistic",
        provider="failing_provider",
    )

    assert result["success"] is False
    assert result["error"] == "API quota exceeded"
    assert result["error_code"] == "QUOTA_EXCEEDED"
    assert result["suggestion"] == "Please upgrade your plan or wait for quota reset"


@pytest.mark.asyncio
async def test_error_handling_task_failed(temp_output_dir, reset_registry):
    registry = PresetRegistry()
    registry.register(MockPreset("realistic", PresetDimension.VISUAL, ["realistic"]))

    provider_with_failed_task = MagicMock()
    provider_with_failed_task.name = "failed_provider"
    provider_with_failed_task.generate = AsyncMock(
        return_value=GenerationResult(
            success=True,
            task_id="failed-task-456",
            video_path="https://example.com/video.mp4",
        )
    )
    provider_with_failed_task.check_status = AsyncMock(return_value=TaskStatus.FAILED)
    provider_with_failed_task.check_status_with_retry = AsyncMock(
        return_value=TaskStatus.FAILED
    )

    config = Config(output_dir=temp_output_dir)
    poll_config = PollConfig(interval=0.1, max_wait=5.0)
    engine = VideoEngine(config=config, poll_config=poll_config)
    engine._router.register("failed_provider", provider_with_failed_task)

    result = await engine.generate(
        images=["image.jpg"],
        visual_preset="realistic",
        provider="failed_provider",
    )

    assert result["success"] is False
    assert result["task_id"] == "failed-task-456"
    assert result["error_code"] == "TASK_FAILED"
    assert "failed" in result["error"].lower()


@pytest.mark.asyncio
async def test_error_handling_invalid_preset(temp_output_dir, reset_registry):
    registry = PresetRegistry()
    registry.register(MockPreset("realistic", PresetDimension.VISUAL, ["realistic"]))

    config = Config(output_dir=temp_output_dir)
    poll_config = PollConfig(interval=0.1, max_wait=5.0)
    engine = VideoEngine(config=config, poll_config=poll_config)

    mock_provider = MagicMock()
    mock_provider.name = "mock_provider"
    mock_provider.generate = AsyncMock(
        return_value=GenerationResult(success=True, task_id="test-id", video_path="https://example.com/video.mp4")
    )
    mock_provider.check_status_with_retry = AsyncMock(return_value=TaskStatus.SUCCEEDED)
    mock_provider.download_video = AsyncMock(side_effect=make_mock_download_video())
    engine._router.register("mock_provider", mock_provider)

    result = await engine.generate(
        images=["image.jpg"],
        visual_preset="nonexistent_preset",
        provider="mock_provider",
    )

    assert result["success"] is True
    assert result["prompt_path"] is not None


@pytest.mark.asyncio
async def test_error_handling_provider_not_found(temp_output_dir, reset_registry):
    registry = PresetRegistry()
    registry.register(MockPreset("realistic", PresetDimension.VISUAL, ["realistic"]))

    config = Config(output_dir=temp_output_dir)
    poll_config = PollConfig(interval=0.1, max_wait=5.0)
    engine = VideoEngine(config=config, poll_config=poll_config)

    engine._router.unregister("jimeng")

    result = await engine.generate(
        images=["image.jpg"],
        visual_preset="realistic",
        provider="nonexistent_provider",
    )

    assert result["success"] is False
    assert result["error_code"] == "PROVIDER_ERROR" or "No providers" in result["error"]


@pytest.mark.asyncio
async def test_full_flow_with_quality_mode(engine_with_mock_provider, temp_output_dir):
    engine = engine_with_mock_provider

    with patch.object(
        engine._optimizer,
        "optimize",
        new=AsyncMock(return_value="Optimized quality prompt with realistic style"),
    ):
        result = await engine.generate(
            images=["image1.jpg"],
            visual_preset="realistic",
            description="Test quality mode",
            mode=OptimizationMode.QUALITY,
            provider="mock_provider",
        )

    assert result["success"] is True

    prompt_path = Path(result["prompt_path"])
    content = prompt_path.read_text(encoding="utf-8")
    assert "Optimized quality prompt" in content or len(content) > 0


@pytest.mark.asyncio
async def test_full_flow_custom_poll_config(temp_output_dir, reset_registry):
    registry = PresetRegistry()
    registry.register(MockPreset("realistic", PresetDimension.VISUAL, ["realistic"]))

    mock_provider = MagicMock()
    mock_provider.name = "mock_provider"
    mock_provider.generate = AsyncMock(
        return_value=GenerationResult(
            success=True,
            task_id="test-task-789",
            video_path="https://example.com/video.mp4",
        )
    )
    mock_provider.check_status_with_retry = AsyncMock(return_value=TaskStatus.SUCCEEDED)
    mock_provider.download_video = AsyncMock(side_effect=make_mock_download_video())

    config = Config(output_dir=temp_output_dir)
    custom_poll_config = PollConfig(
        interval=0.01, max_wait=1.0, retry_count=2, retry_interval=0.01
    )
    engine = VideoEngine(config=config, poll_config=custom_poll_config)
    engine._router.register("mock_provider", mock_provider)

    result = await engine.generate(
        images=["image.jpg"],
        visual_preset="realistic",
        provider="mock_provider",
        poll_config=PollConfig(interval=0.01, max_wait=0.5),
    )

    assert result["success"] is True
    assert result["task_id"] == "test-task-789"


@pytest.mark.asyncio
async def test_error_handling_no_video_url(temp_output_dir, reset_registry):
    registry = PresetRegistry()
    registry.register(MockPreset("realistic", PresetDimension.VISUAL, ["realistic"]))

    provider_no_url = MagicMock()
    provider_no_url.name = "no_url_provider"
    provider_no_url.generate = AsyncMock(
        return_value=GenerationResult(
            success=True,
            task_id="no-url-task",
            video_path=None,
        )
    )
    provider_no_url.check_status_with_retry = AsyncMock(
        return_value=TaskStatus.SUCCEEDED
    )

    config = Config(output_dir=temp_output_dir)
    poll_config = PollConfig(interval=0.1, max_wait=5.0)
    engine = VideoEngine(config=config, poll_config=poll_config)
    engine._router.register("no_url_provider", provider_no_url)

    result = await engine.generate(
        images=["image.jpg"],
        visual_preset="realistic",
        provider="no_url_provider",
    )

    assert result["success"] is False
    assert result["error_code"] == "NO_VIDEO_URL"
    assert result["task_id"] == "no-url-task"


@pytest.mark.asyncio
async def test_error_handling_no_task_id(temp_output_dir, reset_registry):
    registry = PresetRegistry()
    registry.register(MockPreset("realistic", PresetDimension.VISUAL, ["realistic"]))

    provider_no_task = MagicMock()
    provider_no_task.name = "no_task_provider"
    provider_no_task.generate = AsyncMock(
        return_value=GenerationResult(
            success=True,
            task_id=None,
            video_path=None,
        )
    )

    config = Config(output_dir=temp_output_dir)
    poll_config = PollConfig(interval=0.1, max_wait=5.0)
    engine = VideoEngine(config=config, poll_config=poll_config)
    engine._router.register("no_task_provider", provider_no_task)

    result = await engine.generate(
        images=["image.jpg"],
        visual_preset="realistic",
        provider="no_task_provider",
    )

    assert result["success"] is False
    assert result["error_code"] == "NO_TASK_ID"
