import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from video_gen.core.types import GenerationResult
from video_gen.providers.base import GenerationConfig, TaskStatus
from video_gen.providers.jimeng import (
    JimengProvider,
    SUPPORTED_RATIOS,
    SUPPORTED_MODELS,
    MIN_DURATION,
    MAX_DURATION,
    MAX_IMAGES,
)
from video_gen.providers.router import ProviderRouter, get_default_router, reset_router
from video_gen.core.errors import InvalidParameterError


class TestJimengProviderValidateConfig:
    def test_validate_config_accepts_valid_config(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["image1.jpg"],
            prompt="test",
            duration=5,
            ratio="16:9",
            model="seedance2.0",
        )
        provider._validate_config(config)

    def test_validate_config_rejects_too_many_images(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=[f"image{i}.jpg" for i in range(15)],
            prompt="test",
            duration=5,
            ratio="16:9",
            model="seedance2.0",
        )
        with pytest.raises(InvalidParameterError) as exc_info:
            provider._validate_config(config)
        assert "images" in str(exc_info.value)
        assert str(MAX_IMAGES) in str(exc_info.value)

    def test_validate_config_rejects_invalid_duration_too_low(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["image1.jpg"],
            prompt="test",
            duration=1,
            ratio="16:9",
            model="seedance2.0",
        )
        with pytest.raises(InvalidParameterError) as exc_info:
            provider._validate_config(config)
        assert "duration" in str(exc_info.value)

    def test_validate_config_rejects_invalid_duration_too_high(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["image1.jpg"],
            prompt="test",
            duration=100,
            ratio="16:9",
            model="seedance2.0",
        )
        with pytest.raises(InvalidParameterError) as exc_info:
            provider._validate_config(config)
        assert "duration" in str(exc_info.value)

    def test_validate_config_rejects_invalid_ratio(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["image1.jpg"],
            prompt="test",
            duration=5,
            ratio="invalid_ratio",
            model="seedance2.0",
        )
        with pytest.raises(InvalidParameterError) as exc_info:
            provider._validate_config(config)
        assert "ratio" in str(exc_info.value)

    def test_validate_config_rejects_invalid_model(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["image1.jpg"],
            prompt="test",
            duration=5,
            ratio="16:9",
            model="invalid_model",
        )
        with pytest.raises(InvalidParameterError) as exc_info:
            provider._validate_config(config)
        assert "model" in str(exc_info.value)

    def test_validate_config_accepts_all_supported_ratios(self):
        provider = JimengProvider()
        for ratio in SUPPORTED_RATIOS:
            config = GenerationConfig(
                images=["image1.jpg"],
                prompt="test",
                duration=5,
                ratio=ratio,
                model="seedance2.0",
            )
            provider._validate_config(config)

    def test_validate_config_accepts_all_supported_models(self):
        provider = JimengProvider()
        for model in SUPPORTED_MODELS:
            config = GenerationConfig(
                images=["image1.jpg"],
                prompt="test",
                duration=5,
                ratio="16:9",
                model=model,
            )
            provider._validate_config(config)

    def test_validate_config_accepts_min_duration(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["image1.jpg"],
            prompt="test",
            duration=MIN_DURATION,
            ratio="16:9",
            model="seedance2.0",
        )
        provider._validate_config(config)

    def test_validate_config_accepts_max_duration(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["image1.jpg"],
            prompt="test",
            duration=MAX_DURATION,
            ratio="16:9",
            model="seedance2.0",
        )
        provider._validate_config(config)

    def test_validate_config_accepts_max_images(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=[f"image{i}.jpg" for i in range(MAX_IMAGES)],
            prompt="test",
            duration=5,
            ratio="16:9",
            model="seedance2.0",
        )
        provider._validate_config(config)


class TestJimengProviderBuildCliArgs:
    def test_build_cli_args_basic(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["image1.jpg", "image2.jpg"],
            prompt="test prompt",
            duration=5,
            ratio="16:9",
            model="seedance2.0",
        )
        args = provider._build_cli_args(config)
        assert "multimodal2video" in args
        assert "--image" in args
        assert "image1.jpg" in args
        assert "image2.jpg" in args
        assert "--prompt" in args
        assert "test prompt" in args
        assert "--duration" in args
        assert "5" in args
        assert "--ratio" in args
        assert "16:9" in args
        assert "--model_version" in args
        assert "seedance2.0" in args

    def test_build_cli_args_multiple_images(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["img1.jpg", "img2.jpg", "img3.jpg"],
            prompt="test",
            duration=5,
            ratio="16:9",
            model="seedance2.0",
        )
        args = provider._build_cli_args(config)
        image_indices = [i for i, x in enumerate(args) if x == "--image"]
        assert len(image_indices) == 3

    def test_build_cli_args_no_prompt(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["image1.jpg"],
            prompt="",
            duration=5,
            ratio="16:9",
            model="seedance2.0",
        )
        args = provider._build_cli_args(config)
        assert "--prompt" not in args

    def test_build_cli_args_order(self):
        provider = JimengProvider()
        config = GenerationConfig(
            images=["img.jpg"],
            prompt="prompt text",
            duration=10,
            ratio="9:16",
            model="seedance2.0fast",
        )
        args = provider._build_cli_args(config)
        assert args[0] == "multimodal2video"


class TestJimengProviderParseCliOutput:
    def test_parse_cli_output_json_format(self):
        provider = JimengProvider()
        output = '{"task_id": "abc-123", "status": "success", "video_url": "https://example.com/video.mp4"}'
        result = provider._parse_cli_output(output)
        assert result["task_id"] == "abc-123"
        assert result["status"] == "success"
        assert result["video_url"] == "https://example.com/video.mp4"

    def test_parse_cli_output_json_embedded_in_text(self):
        provider = JimengProvider()
        output = 'Starting generation...\n{"task_id": "xyz-789", "status": "pending"}\nDone!'
        result = provider._parse_cli_output(output)
        assert result["task_id"] == "xyz-789"
        assert result["status"] == "pending"

    def test_parse_cli_output_text_format_task_id(self):
        provider = JimengProvider()
        output = "task_id: abc-123-def"
        result = provider._parse_cli_output(output)
        assert result["task_id"] == "abc-123-def"

    def test_parse_cli_output_text_format_status(self):
        provider = JimengProvider()
        output = "status: succeeded"
        result = provider._parse_cli_output(output)
        assert result["status"] == "succeeded"

    def test_parse_cli_output_text_format_video_url(self):
        provider = JimengProvider()
        output = "video: https://cdn.example.com/video.mp4"
        result = provider._parse_cli_output(output)
        assert result["video_url"] == "https://cdn.example.com/video.mp4"

    def test_parse_cli_output_text_format_error(self):
        provider = JimengProvider()
        output = "error: Something went wrong\n"
        result = provider._parse_cli_output(output)
        assert result["error"] == "Something went wrong"

    def test_parse_cli_output_task_id_with_underscore(self):
        provider = JimengProvider()
        output = "task_id: test-123"
        result = provider._parse_cli_output(output)
        assert result["task_id"] == "test-123"

    def test_parse_cli_output_empty_string(self):
        provider = JimengProvider()
        result = provider._parse_cli_output("")
        assert result == {}

    def test_parse_cli_output_whitespace_only(self):
        provider = JimengProvider()
        result = provider._parse_cli_output("   \n\t  ")
        assert result == {}

    def test_parse_cli_output_invalid_json(self):
        provider = JimengProvider()
        output = "{invalid json}"
        result = provider._parse_cli_output(output)
        assert result == {}

    def test_parse_cli_output_url_with_http(self):
        provider = JimengProvider()
        output = "url: http://example.com/video.mp4"
        result = provider._parse_cli_output(output)
        assert result["video_url"] == "http://example.com/video.mp4"


class TestJimengProviderProperties:
    def test_name_property(self):
        provider = JimengProvider()
        assert provider.name == "jimeng"

    def test_info_property(self):
        provider = JimengProvider()
        info = provider.info
        assert info.name == "jimeng"
        assert info.display_name == "Jimeng Video Generator"
        assert info.min_duration == MIN_DURATION
        assert info.max_duration == MAX_DURATION
        assert info.max_images == MAX_IMAGES
        assert info.supported_ratios == SUPPORTED_RATIOS
        assert info.supported_models == SUPPORTED_MODELS


class TestProviderRouter:
    def test_register_and_get(self):
        router = ProviderRouter()
        mock_provider = MagicMock()
        mock_provider.name = "test_provider"
        router.register("test_provider", mock_provider)
        result = router.get("test_provider")
        assert result is mock_provider

    def test_get_nonexistent_raises_key_error(self):
        router = ProviderRouter()
        with pytest.raises(KeyError):
            router.get("nonexistent")

    def test_resolve_with_hint(self):
        router = ProviderRouter()
        mock_provider = MagicMock()
        mock_provider.name = "hinted"
        router.register("hinted", mock_provider)
        router.register("other", MagicMock())
        result = router.resolve("hinted")
        assert result is mock_provider

    def test_resolve_defaults_to_jimeng(self):
        router = ProviderRouter()
        jimeng_mock = MagicMock()
        jimeng_mock.name = "jimeng"
        router.register("jimeng", jimeng_mock)
        router.register("other", MagicMock())
        result = router.resolve()
        assert result is jimeng_mock

    def test_resolve_returns_first_if_no_jimeng(self):
        router = ProviderRouter()
        provider1 = MagicMock()
        provider1.name = "provider1"
        provider2 = MagicMock()
        provider2.name = "provider2"
        router.register("provider1", provider1)
        router.register("provider2", provider2)
        result = router.resolve()
        assert result is provider1

    def test_resolve_raises_if_no_providers(self):
        router = ProviderRouter()
        with pytest.raises(RuntimeError):
            router.resolve()

    def test_list_returns_provider_names(self):
        router = ProviderRouter()
        router.register("provider1", MagicMock())
        router.register("provider2", MagicMock())
        names = router.list()
        assert "provider1" in names
        assert "provider2" in names

    def test_unregister_existing(self):
        router = ProviderRouter()
        router.register("test", MagicMock())
        result = router.unregister("test")
        assert result is True
        assert "test" not in router.list()

    def test_unregister_nonexistent(self):
        router = ProviderRouter()
        result = router.unregister("nonexistent")
        assert result is False

    def test_has_existing(self):
        router = ProviderRouter()
        router.register("test", MagicMock())
        assert router.has("test") is True

    def test_has_nonexistent(self):
        router = ProviderRouter()
        assert router.has("nonexistent") is False


class TestGetDefaultRouter:
    def test_get_default_router_returns_singleton(self):
        reset_router()
        router1 = get_default_router()
        router2 = get_default_router()
        assert router1 is router2
        reset_router()

    def test_get_default_router_has_jimeng(self):
        reset_router()
        router = get_default_router()
        assert router.has("jimeng") is True
        reset_router()


class TestJimengProviderIsAvailable:
    @pytest.mark.asyncio
    async def test_is_available_returns_true_when_installed_and_logged_in(self):
        provider = JimengProvider()
        mock_checker = MagicMock()
        mock_status = MagicMock()
        mock_status.installed = True
        mock_status.logged_in = True
        mock_checker.check_full_status = AsyncMock(return_value=mock_status)
        provider._status_checker = mock_checker
        result = await provider.is_available()
        assert result is True

    @pytest.mark.asyncio
    async def test_is_available_returns_false_when_not_installed(self):
        provider = JimengProvider()
        mock_checker = MagicMock()
        mock_status = MagicMock()
        mock_status.installed = False
        mock_status.logged_in = True
        mock_checker.check_full_status = AsyncMock(return_value=mock_status)
        provider._status_checker = mock_checker
        result = await provider.is_available()
        assert result is False

    @pytest.mark.asyncio
    async def test_is_available_returns_false_when_not_logged_in(self):
        provider = JimengProvider()
        mock_checker = MagicMock()
        mock_status = MagicMock()
        mock_status.installed = True
        mock_status.logged_in = False
        mock_checker.check_full_status = AsyncMock(return_value=mock_status)
        provider._status_checker = mock_checker
        result = await provider.is_available()
        assert result is False