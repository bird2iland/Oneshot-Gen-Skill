import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from video_gen.agent_tools import AgentTools, AgentToolsConfig
from video_gen.core.types import PresetDimension


@pytest.fixture(autouse=True)
def reset_agent_tools():
    AgentTools.reset()
    yield
    AgentTools.reset()


@pytest.fixture
def mock_status_checker():
    mock = MagicMock()
    mock.check_full_status = AsyncMock()
    mock.get_install_guide.return_value = "mock install guide"
    return mock


@pytest.fixture
def mock_composer():
    mock = MagicMock()
    mock.compose = AsyncMock(return_value="composed prompt")
    return mock


@pytest.fixture
def mock_registry():
    from video_gen.presets.base import BasePreset
    from video_gen.core.types import PresetConfig

    class FakePreset(BasePreset):
        def __init__(self, preset_id: str, dimension: PresetDimension):
            self.dimension = dimension
            self.config = PresetConfig(
                id=preset_id,
                name=preset_id.capitalize(),
                description=f"Fake {preset_id}",
                keywords=[preset_id],
            )

        async def apply(self, context: dict) -> str:
            return f"applied {self.config.id}"

        def get_keywords(self) -> list[str]:
            return self.config.keywords

    mock = MagicMock()
    mock.list.return_value = [
        FakePreset("test_visual", PresetDimension.VISUAL),
        FakePreset("test_time", PresetDimension.TIME),
        FakePreset("test_camera", PresetDimension.CAMERA),
    ]
    mock.get.return_value = FakePreset("test_visual", PresetDimension.VISUAL)
    return mock


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_data_dir(temp_output_dir):
    return temp_output_dir / "data"


@pytest.fixture
def agent_tools_config(temp_output_dir, temp_data_dir):
    return AgentToolsConfig(
        output_dir=temp_output_dir,
        data_dir=temp_data_dir,
    )


class TestPresetList:
    @pytest.mark.asyncio
    async def test_preset_list(self, agent_tools_config, mock_registry, mock_composer, mock_status_checker):
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore"),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            presets = await tools.preset_list()

            assert isinstance(presets, list)
            mock_read_only_store.list_presets.assert_called()

    @pytest.mark.asyncio
    async def test_preset_list_with_dimension(
        self, agent_tools_config, mock_registry, mock_composer, mock_status_checker
    ):
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore"),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            presets = await tools.preset_list(dimension="visual")

            mock_read_only_store.list_presets.assert_called_with(dimension="visual")
            assert isinstance(presets, list)


class TestPresetShow:
    @pytest.mark.asyncio
    async def test_preset_show(self, agent_tools_config, mock_registry, mock_composer, mock_status_checker):
        from video_gen.core import PresetData
        
        mock_preset = PresetData(
            id="test_visual",
            dimension="visual",
            name="Test Visual",
            description="Test preset",
            keywords=["test"],
            template="{description}",
        )
        mock_read_only_store = MagicMock()
        mock_read_only_store.get_preset.return_value = mock_preset

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore"),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            result = await tools.preset_show(preset_id="test_visual", dimension="visual")

            assert result["success"] is True
            assert "preset" in result
            assert result["preset"]["id"] == "test_visual"

    @pytest.mark.asyncio
    async def test_preset_show_not_found(
        self, agent_tools_config, mock_registry, mock_composer, mock_status_checker
    ):
        mock_read_only_store = MagicMock()
        mock_read_only_store.get_preset.return_value = None

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore"),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            result = await tools.preset_show(preset_id="nonexistent", dimension="visual")

            assert result["success"] is False
            assert result["error_code"] == "PRESET_NOT_FOUND"


class TestOptimizePrompt:
    @pytest.mark.asyncio
    async def test_optimize_prompt(self, agent_tools_config, mock_registry, mock_composer, mock_status_checker):
        mock_optimizer = MagicMock()
        mock_optimizer.optimize = AsyncMock(return_value="optimized prompt result")
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.create_optimizer", return_value=mock_optimizer),
            patch("video_gen.agent_tools.DataStore"),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            result = await tools.optimize_prompt(
                visual_preset="realistic",
                time_preset="normal",
                camera_preset="gimbal",
                description="test description",
                mode="fast",
            )

            assert result == "optimized prompt result"
            mock_composer.compose.assert_called_once()

    @pytest.mark.asyncio
    async def test_optimize_prompt_quality_mode(
        self, agent_tools_config, mock_registry, mock_composer, mock_status_checker
    ):
        mock_optimizer = MagicMock()
        mock_optimizer.optimize = AsyncMock(return_value="quality optimized prompt")
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.create_optimizer", return_value=mock_optimizer),
            patch("video_gen.agent_tools.DataStore"),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            result = await tools.optimize_prompt(
                description="test",
                mode="quality",
            )

            assert result == "quality optimized prompt"


class TestExportPrompt:
    @pytest.mark.asyncio
    async def test_export_prompt(self, agent_tools_config, mock_registry, mock_composer, mock_status_checker):
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore"),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            prompt = "test prompt content"
            path = await tools.export_prompt(prompt)

            assert path.endswith(".txt")
            assert Path(path).exists()
            assert Path(path).read_text(encoding="utf-8") == prompt

    @pytest.mark.asyncio
    async def test_export_prompt_with_filename(
        self, agent_tools_config, mock_registry, mock_composer, mock_status_checker
    ):
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore"),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            prompt = "test prompt content"
            path = await tools.export_prompt(prompt, filename="custom_prompt.txt")

            assert path.endswith("custom_prompt.txt")
            assert Path(path).exists()

    @pytest.mark.asyncio
    async def test_export_prompt_with_filename_without_extension(
        self, agent_tools_config, mock_registry, mock_composer, mock_status_checker
    ):
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore"),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            prompt = "test prompt content"
            path = await tools.export_prompt(prompt, filename="custom_prompt")

            assert path.endswith("custom_prompt.txt")
            assert Path(path).exists()

    @pytest.mark.asyncio
    async def test_export_prompt_with_custom_output_dir(
        self, agent_tools_config, mock_registry, mock_composer, mock_status_checker
    ):
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore"),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            with tempfile.TemporaryDirectory() as tmpdir:
                prompt = "test prompt"
                path = await tools.export_prompt(prompt, output_dir=tmpdir)

                assert Path(path).exists()
                assert tmpdir in path


class TestCheckStatus:
    @pytest.mark.asyncio
    async def test_check_status(self, agent_tools_config, mock_registry, mock_composer, mock_status_checker):
        from video_gen.providers.jimeng_status import JimengStatus

        mock_status = JimengStatus(
            installed=True,
            version="1.0.0",
            logged_in=True,
            user_info="user_id: 12345",
        )
        mock_status_checker.check_full_status.return_value = mock_status
        
        mock_data_store = MagicMock()
        mock_data_store.PRESETS_FILE.exists.return_value = True
        mock_data_store.CREDENTIALS_FILE.exists.return_value = True
        mock_data_store.CONFIG_FILE.exists.return_value = True
        
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []
        mock_read_only_store.get_llm_config.return_value = {"api_key": "test"}

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore", return_value=mock_data_store),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            result = await tools.check_status()

            assert result["success"] is True
            assert result["installed"] is True
            assert result["version"] == "1.0.0"
            assert result["logged_in"] is True
            assert result["user_info"] == "user_id: 12345"
            assert "data_store" in result
            assert result["llm_configured"] is True

    @pytest.mark.asyncio
    async def test_check_status_not_installed(
        self, agent_tools_config, mock_registry, mock_composer, mock_status_checker
    ):
        from video_gen.providers.jimeng_status import JimengStatus

        mock_status = JimengStatus(
            installed=False,
            version=None,
            logged_in=False,
            user_info=None,
            error="Jimeng CLI not found",
        )
        mock_status_checker.check_full_status.return_value = mock_status
        
        mock_data_store = MagicMock()
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []
        mock_read_only_store.get_llm_config.return_value = None

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore", return_value=mock_data_store),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            result = await tools.check_status()

            assert result["success"] is True
            assert result["installed"] is False
            assert result["install_guide"] is not None

    @pytest.mark.asyncio
    async def test_check_status_not_logged_in(
        self, agent_tools_config, mock_registry, mock_composer, mock_status_checker
    ):
        from video_gen.providers.jimeng_status import JimengStatus

        mock_status = JimengStatus(
            installed=True,
            version="1.0.0",
            logged_in=False,
            user_info=None,
            error="User not logged in",
        )
        mock_status_checker.check_full_status.return_value = mock_status
        
        mock_data_store = MagicMock()
        mock_read_only_store = MagicMock()
        mock_read_only_store.list_presets.return_value = []
        mock_read_only_store.get_llm_config.return_value = None

        with (
            patch("video_gen.agent_tools.PresetRegistry", return_value=mock_registry),
            patch("video_gen.agent_tools.PresetComposer", return_value=mock_composer),
            patch("video_gen.agent_tools.JimengStatusChecker", return_value=mock_status_checker),
            patch("video_gen.agent_tools.register_default_presets"),
            patch("video_gen.agent_tools.DataStore", return_value=mock_data_store),
            patch("video_gen.agent_tools.ReadOnlyDataStore", return_value=mock_read_only_store),
        ):
            tools = AgentTools(config=agent_tools_config)
            result = await tools.check_status()

            assert result["success"] is True
            assert result["installed"] is True
            assert result["logged_in"] is False


class TestAgentToolsSingleton:
    def test_singleton_returns_same_instance(self, agent_tools_config):
        AgentTools.reset()
        with patch("video_gen.agent_tools.register_default_presets"):
            instance1 = AgentTools(config=agent_tools_config)
            instance2 = AgentTools(config=agent_tools_config)
            assert instance1 is instance2

    def test_reset_creates_new_instance(self, agent_tools_config):
        AgentTools.reset()
        with patch("video_gen.agent_tools.register_default_presets"):
            instance1 = AgentTools(config=agent_tools_config)
        AgentTools.reset()
        with patch("video_gen.agent_tools.register_default_presets"):
            instance2 = AgentTools(config=agent_tools_config)
        assert instance1 is not instance2