import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from video_gen.core.data_store import (
    ConfigData,
    CredentialData,
    DataStore,
    PresetData,
    ReadOnlyDataStore,
)


@pytest.fixture
def temp_data_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def data_store(temp_data_dir):
    return DataStore(data_dir=temp_data_dir)


@pytest.fixture
def sample_presets():
    return {
        "version": "1.0",
        "last_updated": "2026-04-22T10:30:00Z",
        "built_in": {
            "visual": {
                "realistic": {
                    "name": "真实风格",
                    "description": "高度写实的视觉呈现",
                    "keywords": ["真实", "写实"],
                    "template": "写实风格，{description}",
                }
            }
        },
        "custom": {},
    }


@pytest.fixture
def sample_config():
    return {
        "version": "1.0",
        "output": {"dir": "./output"},
        "defaults": {"provider": "jimeng", "duration": 5},
        "polling": {"interval": 2.0},
        "logging": {"verbose": False},
    }


class TestDataStorePresets:
    def test_get_preset_built_in(self, data_store, temp_data_dir, sample_presets):
        presets_file = temp_data_dir / "presets.json"
        with open(presets_file, "w", encoding="utf-8") as f:
            json.dump(sample_presets, f)

        preset = data_store.get_preset("visual", "realistic")

        assert preset is not None
        assert preset.id == "realistic"
        assert preset.name == "真实风格"
        assert preset.is_custom is False
        assert preset.dimension == "visual"

    def test_get_preset_not_found(self, data_store):
        preset = data_store.get_preset("visual", "nonexistent")
        assert preset is None

    def test_list_presets_all(self, data_store, temp_data_dir, sample_presets):
        presets_file = temp_data_dir / "presets.json"
        with open(presets_file, "w", encoding="utf-8") as f:
            json.dump(sample_presets, f)

        presets = data_store.list_presets()

        assert len(presets) == 1
        assert presets[0].id == "realistic"

    def test_list_presets_by_dimension(self, data_store, temp_data_dir, sample_presets):
        sample_presets["built_in"]["time"] = {
            "normal": {
                "name": "正常速度",
                "description": "标准时间流逝",
                "keywords": ["正常"],
                "template": "{description}",
            }
        }
        presets_file = temp_data_dir / "presets.json"
        with open(presets_file, "w", encoding="utf-8") as f:
            json.dump(sample_presets, f)

        presets = data_store.list_presets(dimension="time")

        assert len(presets) == 1
        assert presets[0].id == "normal"
        assert presets[0].dimension == "time"

    def test_save_preset(self, data_store):
        preset = PresetData(
            id="my_style",
            dimension="visual",
            name="我的风格",
            description="自定义风格",
            keywords=["自定义"],
            template="自定义风格，{description}",
        )

        result = data_store.save_preset(preset)
        assert result is True

        saved = data_store.get_preset("visual", "my_style")
        assert saved is not None
        assert saved.name == "我的风格"
        assert saved.is_custom is True

    def test_delete_preset(self, data_store):
        preset = PresetData(
            id="to_delete",
            dimension="visual",
            name="待删除",
            description="测试删除",
            keywords=[],
        )
        data_store.save_preset(preset)

        result = data_store.delete_preset("visual", "to_delete")
        assert result is True

        deleted = data_store.get_preset("visual", "to_delete")
        assert deleted is None

    def test_delete_preset_not_found(self, data_store):
        result = data_store.delete_preset("visual", "nonexistent")
        assert result is False


class TestDataStoreCredentials:
    def test_save_and_get_credential(self, data_store):
        credential = CredentialData(
            provider="jimeng",
            api_key="test-api-key-12345",
        )

        result = data_store.save_credential(credential)
        assert result is True

        retrieved = data_store.get_credential("jimeng")
        assert retrieved is not None
        assert retrieved.api_key == "test-api-key-12345"
        assert retrieved.provider == "jimeng"

    def test_get_credential_not_found(self, data_store):
        result = data_store.get_credential("nonexistent")
        assert result is None

    def test_delete_credential(self, data_store):
        credential = CredentialData(provider="kling", api_key="test-key")
        data_store.save_credential(credential)

        result = data_store.delete_credential("kling")
        assert result is True

        deleted = data_store.get_credential("kling")
        assert deleted is None

    def test_credentials_file_permission(self, data_store, temp_data_dir):
        credential = CredentialData(provider="test", api_key="secret-key")
        data_store.save_credential(credential)

        credentials_file = temp_data_dir / "credentials.json"
        stat_info = credentials_file.stat()
        assert stat_info.st_mode & 0o777 == 0o600

    def test_encryption_key_file_permission(self, data_store, temp_data_dir):
        credential = CredentialData(provider="test", api_key="secret-key")
        data_store.save_credential(credential)

        key_file = temp_data_dir / ".key"
        stat_info = key_file.stat()
        assert stat_info.st_mode & 0o777 == 0o600


class TestDataStoreConfig:
    def test_get_config_default(self, data_store):
        config = data_store.get_config()

        assert config.default_provider == "jimeng"
        assert config.default_duration == 5
        assert config.poll_interval == 2.0

    def test_save_config(self, data_store):
        config = ConfigData(
            output_dir=Path("./custom_output"),
            default_provider="kling",
            default_model="custom-model",
            default_duration=10,
            verbose=True,
        )

        result = data_store.save_config(config)
        assert result is True

        loaded = data_store.get_config()
        assert loaded.default_provider == "kling"
        assert loaded.default_model == "custom-model"
        assert loaded.default_duration == 10
        assert loaded.verbose is True


class TestDataStoreCache:
    def test_cache_mechanism(self, data_store, temp_data_dir, sample_presets):
        presets_file = temp_data_dir / "presets.json"
        with open(presets_file, "w", encoding="utf-8") as f:
            json.dump(sample_presets, f)

        data_store.get_preset("visual", "realistic")

        assert "presets" in data_store._cache

        data_store.get_preset("visual", "realistic")

        assert data_store._cache_timestamp.get("presets") is not None

    def test_cache_invalidation_on_file_change(self, data_store, temp_data_dir, sample_presets):
        presets_file = temp_data_dir / "presets.json"
        with open(presets_file, "w", encoding="utf-8") as f:
            json.dump(sample_presets, f)

        data_store.get_preset("visual", "realistic")

        sample_presets["built_in"]["visual"]["realistic"]["name"] = "更新后的名称"
        with open(presets_file, "w", encoding="utf-8") as f:
            json.dump(sample_presets, f)

        preset = data_store.get_preset("visual", "realistic")
        assert preset.name == "更新后的名称"


class TestDataStoreEncryption:
    def test_encrypt_decrypt(self, data_store):
        plaintext = "my-secret-api-key"

        encrypted = data_store._encrypt(plaintext)

        assert encrypted != plaintext
        assert encrypted.startswith("enc:AES256:")

        decrypted = data_store._decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_empty_string(self, data_store):
        encrypted = data_store._encrypt("")
        assert encrypted == ""

    def test_decrypt_non_encrypted(self, data_store):
        result = data_store._decrypt("plain-text")
        assert result == "plain-text"


class TestReadOnlyDataStore:
    def test_get_preset(self, data_store, temp_data_dir, sample_presets):
        presets_file = temp_data_dir / "presets.json"
        with open(presets_file, "w", encoding="utf-8") as f:
            json.dump(sample_presets, f)

        read_only = ReadOnlyDataStore(data_store)
        preset = read_only.get_preset("visual", "realistic")

        assert preset is not None
        assert preset.id == "realistic"

    def test_list_presets(self, data_store, temp_data_dir, sample_presets):
        presets_file = temp_data_dir / "presets.json"
        with open(presets_file, "w", encoding="utf-8") as f:
            json.dump(sample_presets, f)

        read_only = ReadOnlyDataStore(data_store)
        presets = read_only.list_presets()

        assert len(presets) == 1

    def test_get_credential(self, data_store):
        credential = CredentialData(provider="test", api_key="test-key")
        data_store.save_credential(credential)

        read_only = ReadOnlyDataStore(data_store)
        retrieved = read_only.get_credential("test")

        assert retrieved is not None
        assert retrieved.api_key == "test-key"

    def test_get_config(self, data_store):
        read_only = ReadOnlyDataStore(data_store)
        config = read_only.get_config()

        assert config is not None
        assert config.default_provider == "jimeng"

    def test_no_write_methods(self, data_store):
        read_only = ReadOnlyDataStore(data_store)

        assert not hasattr(read_only, "save_preset")
        assert not hasattr(read_only, "delete_preset")
        assert not hasattr(read_only, "save_credential")
        assert not hasattr(read_only, "delete_credential")
        assert not hasattr(read_only, "save_config")


class TestDefaultData:
    def test_default_presets(self, data_store):
        presets = data_store.list_presets()
        assert presets == []

    def test_default_credentials(self, data_store):
        credential = data_store.get_credential("nonexistent")
        assert credential is None

    def test_default_config(self, data_store):
        config = data_store.get_config()
        assert config.default_provider == "jimeng"
        assert config.poll_interval == 2.0