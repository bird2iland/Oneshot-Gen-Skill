import tempfile
from pathlib import Path

import pytest
import yaml

from video_gen.core.types import PresetDimension
from video_gen.presets.custom_loader import CustomPreset, CustomPresetLoader
from video_gen.presets.registry import PresetRegistry


class TestCustomPreset:
    def test_custom_preset_creation(self):
        from video_gen.core.types import PresetConfig
        
        config = PresetConfig(
            id="test_preset",
            name="Test Preset",
            description="A test preset",
            keywords=["test", "custom"],
            template="{description}, test style",
            metadata={"category": "test"},
        )
        
        preset = CustomPreset(
            dimension=PresetDimension.VISUAL,
            config=config,
            is_custom=True,
        )
        
        assert preset.dimension == PresetDimension.VISUAL
        assert preset.config.id == "test_preset"
        assert preset.is_custom is True
        assert preset.get_keywords() == ["test", "custom"]

    @pytest.mark.asyncio
    async def test_custom_preset_apply(self):
        from video_gen.core.types import PresetConfig
        
        config = PresetConfig(
            id="test_preset",
            name="Test Preset",
            description="A test preset",
            keywords=["test"],
            template="{description}, artistic style",
        )
        
        preset = CustomPreset(
            dimension=PresetDimension.VISUAL,
            config=config,
        )
        
        result = await preset.apply({"description": "A beautiful sunset"})
        assert result == "A beautiful sunset, artistic style"

    def test_custom_preset_default_is_custom(self):
        from video_gen.core.types import PresetConfig
        
        config = PresetConfig(
            id="test",
            name="Test",
            description="Test",
        )
        
        preset = CustomPreset(
            dimension=PresetDimension.VISUAL,
            config=config,
        )
        
        assert preset.is_custom is True


class TestCustomPresetLoader:
    def test_load_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.yaml"
            loader = CustomPresetLoader(config_path=config_path)
            registry = PresetRegistry()
            
            count = loader.load(registry)
            assert count == 0

    def test_load_valid_yaml(self):
        yaml_content = {
            "custom_presets": {
                "visual": {
                    "my_style": {
                        "name": "My Style",
                        "description": "Custom visual style",
                        "keywords": ["custom", "style"],
                        "template": "{description}, custom style",
                        "metadata": {"category": "artistic"},
                    }
                },
                "time": {
                    "slow_dramatic": {
                        "name": "Slow Dramatic",
                        "description": "Dramatic slow motion",
                        "keywords": ["slow", "dramatic"],
                        "template": "{description}, slow motion",
                    }
                },
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "custom_presets.yaml"
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_content, f)
            
            loader = CustomPresetLoader(config_path=config_path)
            registry = PresetRegistry()
            
            count = loader.load(registry)
            assert count == 2

            visual_preset = registry.get(PresetDimension.VISUAL, "my_style")
            assert visual_preset is not None
            assert visual_preset.config.name == "My Style"
            assert visual_preset.is_custom is True

            time_preset = registry.get(PresetDimension.TIME, "slow_dramatic")
            assert time_preset is not None
            assert time_preset.config.name == "Slow Dramatic"

    def test_load_invalid_dimension_skipped(self):
        yaml_content = {
            "custom_presets": {
                "invalid_dimension": {
                    "test_preset": {
                        "name": "Test",
                        "description": "Test",
                    }
                },
                "visual": {
                    "valid_preset": {
                        "name": "Valid",
                        "description": "Valid preset",
                    }
                },
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "custom_presets.yaml"
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_content, f)
            
            loader = CustomPresetLoader(config_path=config_path)
            registry = PresetRegistry()
            
            count = loader.load(registry)
            assert count == 1

    def test_load_malformed_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "custom_presets.yaml"
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("invalid: yaml: content: [")
            
            loader = CustomPresetLoader(config_path=config_path)
            registry = PresetRegistry()
            
            count = loader.load(registry)
            assert count == 0

    def test_list_available(self):
        yaml_content = {
            "custom_presets": {
                "visual": {
                    "style_a": {
                        "name": "Style A",
                        "description": "First style",
                        "keywords": ["a", "style"],
                    },
                    "style_b": {
                        "name": "Style B",
                        "description": "Second style",
                        "keywords": ["b", "style"],
                    },
                },
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "custom_presets.yaml"
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_content, f)
            
            loader = CustomPresetLoader(config_path=config_path)
            presets = loader.list_available()
            
            assert len(presets) == 2
            assert all(p["is_custom"] is True for p in presets)
            ids = [p["id"] for p in presets]
            assert "style_a" in ids
            assert "style_b" in ids

    def test_list_available_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.yaml"
            loader = CustomPresetLoader(config_path=config_path)
            
            presets = loader.list_available()
            assert presets == []

    def test_load_empty_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "empty.yaml"
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("")
            
            loader = CustomPresetLoader(config_path=config_path)
            registry = PresetRegistry()
            
            count = loader.load(registry)
            assert count == 0

    def test_load_with_missing_optional_fields(self):
        yaml_content = {
            "custom_presets": {
                "visual": {
                    "minimal_preset": {
                        "name": "Minimal",
                    }
                },
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "custom_presets.yaml"
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_content, f)
            
            loader = CustomPresetLoader(config_path=config_path)
            registry = PresetRegistry()
            
            count = loader.load(registry)
            assert count == 1

            preset = registry.get(PresetDimension.VISUAL, "minimal_preset")
            assert preset is not None
            assert preset.config.name == "Minimal"
            assert preset.config.description == ""
            assert preset.config.keywords == []

    @pytest.mark.asyncio
    async def test_loaded_preset_functional(self):
        yaml_content = {
            "custom_presets": {
                "visual": {
                    "functional_test": {
                        "name": "Functional Test",
                        "description": "A functional test preset",
                        "keywords": ["test", "functional"],
                        "template": "{description}, enhanced with test style",
                    }
                },
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "custom_presets.yaml"
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_content, f)
            
            loader = CustomPresetLoader(config_path=config_path)
            registry = PresetRegistry()
            loader.load(registry)

            preset = registry.get(PresetDimension.VISUAL, "functional_test")
            assert preset is not None
            
            result = await preset.apply({"description": "Mountain landscape"})
            assert result == "Mountain landscape, enhanced with test style"