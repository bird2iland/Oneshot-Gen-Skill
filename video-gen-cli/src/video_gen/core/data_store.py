import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml
from cryptography.fernet import Fernet


@dataclass
class PresetData:
    id: str
    dimension: str
    name: str
    description: str
    keywords: list[str] = field(default_factory=list)
    template: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    is_custom: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class CredentialData:
    provider: str
    api_key: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None


@dataclass
class ConfigData:
    output_dir: Path
    default_provider: str = "jimeng"
    default_model: str = "seedance2.0"
    default_visual_preset: Optional[str] = None
    default_time_preset: Optional[str] = None
    default_camera_preset: Optional[str] = None
    default_duration: int = 5
    default_ratio: str = "16:9"
    default_mode: str = "fast"
    poll_interval: float = 2.0
    poll_max_wait: float = 300.0
    poll_retry_count: int = 3
    verbose: bool = False


DEFAULT_PRESETS: dict[str, dict[str, dict[str, Any]]] = {
    "visual": {
        "realistic": {"name": "真实风格", "description": "高度写实的视觉呈现", "keywords": ["真实", "写实", "自然"]},
        "cinematic": {"name": "电影风格", "description": "电影质感的视觉呈现", "keywords": ["电影", "电影感", "质感"]},
        "anime": {"name": "动漫风格", "description": "动漫风格的视觉呈现", "keywords": ["动漫", "动画", "二次元"]},
    },
    "time": {
        "normal": {"name": "正常速度", "description": "标准时间流逝", "keywords": ["正常", "标准"]},
        "slow_motion": {"name": "慢动作", "description": "缓慢的时间流逝", "keywords": ["慢动作", "慢", "缓慢"]},
        "timelapse": {"name": "延时摄影", "description": "加速的时间流逝", "keywords": ["延时", "加速", "快进"]},
    },
    "camera": {
        "gimbal": {"name": "稳定器拍摄", "description": "使用云台稳定器拍摄", "keywords": ["稳定", "平滑", "云台"]},
        "handheld": {"name": "手持拍摄", "description": "手持相机拍摄", "keywords": ["手持", "自然", "动感"]},
        "tripod": {"name": "三脚架拍摄", "description": "使用三脚架固定拍摄", "keywords": ["固定", "静止", "稳定"]},
    },
}


class DataStoreReader(ABC):
    @abstractmethod
    def get_preset(self, dimension: str, preset_id: str) -> Optional[PresetData]:
        pass

    @abstractmethod
    def list_presets(self, dimension: Optional[str] = None) -> list[PresetData]:
        pass

    @abstractmethod
    def get_credential(self, provider: str) -> Optional[CredentialData]:
        pass

    @abstractmethod
    def get_llm_config(self) -> Optional[dict[str, Any]]:
        pass

    @abstractmethod
    def get_config(self) -> ConfigData:
        pass


class DataStoreWriter(ABC):
    @abstractmethod
    def save_preset(self, preset: PresetData) -> bool:
        pass

    @abstractmethod
    def delete_preset(self, dimension: str, preset_id: str) -> bool:
        pass

    @abstractmethod
    def save_credential(self, credential: CredentialData) -> bool:
        pass

    @abstractmethod
    def delete_credential(self, provider: str) -> bool:
        pass

    @abstractmethod
    def save_config(self, config: ConfigData) -> bool:
        pass


class DataStore(DataStoreReader, DataStoreWriter):
    DATA_DIR: Optional[Path] = None
    PRESETS_FILE: Optional[Path] = None
    CREDENTIALS_FILE: Optional[Path] = None
    CONFIG_FILE: Optional[Path] = None
    KEY_FILE: Optional[Path] = None
    
    @classmethod
    def _find_data_dir(cls) -> Path:
        """查找数据目录：优先使用环境变量，否则向上查找根目录的 data/"""
        # 尝试 1: 从环境变量
        if os.getenv('VIDEO_GEN_DATA_DIR'):
            return Path(os.getenv('VIDEO_GEN_DATA_DIR'))
        
        # 尝试 2: 从当前文件向上查找，直到找到包含 data 目录的根目录
        current = Path(__file__).parent
        for _ in range(5):  # 最多向上查找 5 层
            root = current.parent
            if (root / 'data').exists() and (root / 'data' / 'presets.json').exists():
                return root / 'data'
            current = root
        
        # 默认：使用当前目录的 data（兼容旧版本）
        return Path(__file__).parent.parent.parent.parent / 'data'
    
    @classmethod
    def _init_data_paths(cls, data_dir: Optional[Path] = None):
        """初始化数据文件路径"""
        if cls.DATA_DIR is None:
            cls.DATA_DIR = data_dir if data_dir else cls._find_data_dir()
            cls.PRESETS_FILE = cls.DATA_DIR / "presets.json"
            cls.CREDENTIALS_FILE = cls.DATA_DIR / "credentials.json"
            cls.CONFIG_FILE = cls.DATA_DIR / "config.yaml"
            cls.KEY_FILE = cls.DATA_DIR / ".key"

    def __init__(self, data_dir: Optional[Path] = None):
        # 初始化数据路径（类级别，只初始化一次）
        self._init_data_paths(data_dir)
        
        # 实例级别初始化
        self._cache: dict[str, Any] = {}
        self._cache_timestamp: dict[str, float] = {}
        self._encryption_key: Optional[bytes] = None
        self._ensure_data_dir()
        self._ensure_default_presets()
    
    def _ensure_default_presets(self) -> bool:
        """Initialize default presets if custom is empty."""
        data = self._load_presets()
        saved = False
        
        for dim, presets in DEFAULT_PRESETS.items():
            if dim not in data.get("custom", {}) or len(data["custom"][dim]) == 0:
                data.setdefault("custom", {})[dim] = {}
                for preset_id, preset_data in presets.items():
                    data["custom"][dim][preset_id] = {
                        **preset_data,
                        "template": "",
                        "metadata": {},
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                    }
                saved = True
        
        if saved:
            data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.PRESETS_FILE, data)
        
        return saved

    def get_preset(self, dimension: str, preset_id: str) -> Optional[PresetData]:
        data = self._load_presets()

        custom = data.get("custom", {}).get(dimension, {}).get(preset_id)
        if custom:
            return self._dict_to_preset(preset_id, dimension, custom, is_custom=True)

        return None

    def list_presets(self, dimension: Optional[str] = None) -> list[PresetData]:
        data = self._load_presets()
        result: list[PresetData] = []

        dimensions = [dimension] if dimension else ["visual", "time", "camera"]

        # 直接从 custom 中读取所有预设
        for dim in dimensions:
            for preset_id, preset_data in data.get("custom", {}).get(dim, {}).items():
                # 跳过删除标记
                if isinstance(preset_data, dict) and preset_data.get("_deleted"):
                    continue
                result.append(self._dict_to_preset(preset_id, dim, preset_data, is_custom=True))

        return result

    def get_credential(self, provider: str) -> Optional[CredentialData]:
        data = self._load_credentials()

        provider_data = data.get("providers", {}).get(provider)
        if not provider_data:
            return None

        encrypted_key = provider_data.get("api_key", "")
        decrypted_key = self._decrypt(encrypted_key)

        return CredentialData(
            provider=provider,
            api_key=decrypted_key,
            metadata={},
            created_at=self._parse_datetime(provider_data.get("created_at")),
        )

    def get_llm_config(self) -> Optional[dict[str, Any]]:
        data = self._load_credentials()
        llm_data = data.get("llm", {})

        if not llm_data.get("api_key"):
            return None

        return {
            "api_key": self._decrypt(llm_data.get("api_key", "")),
            "provider": llm_data.get("provider", "openai"),
            "model": llm_data.get("model", "gpt-4"),
            "base_url": llm_data.get("base_url"),
        }

    def get_config(self) -> ConfigData:
        data = self._load_config()

        return ConfigData(
            output_dir=Path(data.get("output", {}).get("dir", "./output")),
            default_provider=data.get("defaults", {}).get("provider", "jimeng"),
            default_model=data.get("defaults", {}).get("model", "seedance2.0"),
            default_visual_preset=data.get("defaults", {}).get("visual_preset"),
            default_time_preset=data.get("defaults", {}).get("time_preset"),
            default_camera_preset=data.get("defaults", {}).get("camera_preset"),
            default_duration=data.get("defaults", {}).get("duration", 5),
            default_ratio=data.get("defaults", {}).get("ratio", "16:9"),
            default_mode=data.get("defaults", {}).get("mode", "fast"),
            poll_interval=data.get("polling", {}).get("interval", 2.0),
            poll_max_wait=data.get("polling", {}).get("max_wait", 300.0),
            poll_retry_count=data.get("polling", {}).get("retry_count", 3),
            verbose=data.get("logging", {}).get("verbose", False),
        )

    def save_preset(self, preset: PresetData) -> bool:
        import json

        data = self._load_presets()

        # 确保 custom 结构存在
        if "custom" not in data:
            data["custom"] = {}
        if preset.dimension not in data["custom"]:
            data["custom"][preset.dimension] = {}

        preset_dict: dict[str, Any] = {
            "name": preset.name,
            "description": preset.description,
            "keywords": preset.keywords,
            "template": preset.template,
            "metadata": preset.metadata,
            "created_at": preset.created_at.isoformat() if preset.created_at else datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # 保存到 custom 中（覆盖同名预设）
        data["custom"][preset.dimension][preset.id] = preset_dict
        data["last_updated"] = datetime.now().isoformat()

        return self._save_json(self.PRESETS_FILE, data)

    def delete_preset(self, dimension: str, preset_id: str) -> bool:
        data = self._load_presets()
        
        # 从 custom 中删除预设
        if preset_id in data.get("custom", {}).get(dimension, {}):
            del data["custom"][dimension][preset_id]
            data["last_updated"] = datetime.now().isoformat()
            return self._save_json(self.PRESETS_FILE, data)
        
        return False

    def save_preset_combo(
        self,
        name: str,
        visual: Optional[str] = None,
        time: Optional[str] = None,
        camera: Optional[str] = None,
    ) -> bool:
        """Save a preset combination (combo)."""
        preset = PresetData(
            id=name,
            dimension="combo",
            name=name,
            description=f"Visual: {visual or 'none'}, Time: {time or 'none'}, Camera: {camera or 'none'}",
            keywords=[],
            template="",
            metadata={
                "visual": visual,
                "time": time,
                "camera": camera,
            },
            is_custom=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        return self.save_preset(preset)

    def delete_preset_combo(self, name: str) -> bool:
        """Delete a preset combination."""
        return self.delete_preset("combo", name)

    def list_preset_combos(self) -> list[PresetData]:
        """List all preset combinations."""
        return self.list_presets("combo")

    def get_preset_combo(self, name: str) -> Optional[PresetData]:
        """Get a preset combination by name."""
        return self.get_preset("combo", name)

    def save_credential(self, credential: CredentialData) -> bool:
        import json

        data = self._load_credentials()

        if "providers" not in data:
            data["providers"] = {}

        data["providers"][credential.provider] = {
            "api_key": self._encrypt(credential.api_key),
            "created_at": credential.created_at.isoformat()
            if credential.created_at
            else datetime.now().isoformat(),
        }
        data["last_updated"] = datetime.now().isoformat()

        return self._save_json(self.CREDENTIALS_FILE, data, secure=True)

    def delete_credential(self, provider: str) -> bool:
        data = self._load_credentials()

        if provider in data.get("providers", {}):
            del data["providers"][provider]
            data["last_updated"] = datetime.now().isoformat()
            return self._save_json(self.CREDENTIALS_FILE, data, secure=True)

        return False

    def save_config(self, config: ConfigData) -> bool:
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "output": {
                "dir": str(config.output_dir),
            },
            "defaults": {
                "provider": config.default_provider,
                "model": config.default_model,
                "visual_preset": config.default_visual_preset,
                "time_preset": config.default_time_preset,
                "camera_preset": config.default_camera_preset,
                "duration": config.default_duration,
                "ratio": config.default_ratio,
                "mode": config.default_mode,
            },
            "polling": {
                "interval": config.poll_interval,
                "max_wait": config.poll_max_wait,
                "retry_count": config.poll_retry_count,
            },
            "logging": {
                "verbose": config.verbose,
            },
        }

        return self._save_yaml(self.CONFIG_FILE, data)

    def _load_presets(self) -> dict[str, Any]:
        return self._load_cached_json(self.PRESETS_FILE, "presets")

    def _load_credentials(self) -> dict[str, Any]:
        return self._load_cached_json(self.CREDENTIALS_FILE, "credentials")

    def _load_config(self) -> dict[str, Any]:
        return self._load_cached_yaml(self.CONFIG_FILE, "config")

    def _load_cached_json(self, file_path: Path, cache_key: str) -> dict[str, Any]:
        import json

        if self._is_cache_valid(cache_key, file_path):
            cached: dict[str, Any] = self._cache[cache_key]
            return cached

        if not file_path.exists():
            return self._get_default_data(cache_key)

        with open(file_path, "r", encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)

        self._cache[cache_key] = data
        self._cache_timestamp[cache_key] = file_path.stat().st_mtime

        return data

    def _load_cached_yaml(self, file_path: Path, cache_key: str) -> dict[str, Any]:
        if self._is_cache_valid(cache_key, file_path):
            cached: dict[str, Any] = self._cache[cache_key]
            return cached

        if not file_path.exists():
            return self._get_default_data(cache_key)

        with open(file_path, "r", encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}

        self._cache[cache_key] = data
        self._cache_timestamp[cache_key] = file_path.stat().st_mtime

        return data

    def _is_cache_valid(self, cache_key: str, file_path: Path) -> bool:
        if cache_key not in self._cache:
            return False

        if not file_path.exists():
            return False

        cached_mtime = self._cache_timestamp.get(cache_key, 0)
        current_mtime = file_path.stat().st_mtime

        return cached_mtime == current_mtime

    def _get_default_data(self, cache_key: str) -> dict[str, Any]:
        defaults: dict[str, dict[str, Any]] = {
            "presets": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "built_in": {},
                "custom": {},
            },
            "credentials": {
                "version": "1.0",
                "encrypted": True,
                "providers": {},
                "llm": {},
            },
            "config": {
                "version": "1.0",
                "output": {"dir": "./output"},
                "defaults": {},
                "polling": {},
                "logging": {},
            },
        }
        return defaults.get(cache_key, {})

    def _save_json(self, file_path: Path, data: dict[str, Any], secure: bool = False) -> bool:
        import json

        self._ensure_data_dir()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if secure:
            file_path.chmod(0o600)

        self._cache[file_path.stem] = data
        self._cache_timestamp[file_path.stem] = file_path.stat().st_mtime

        return True

    def _save_yaml(self, file_path: Path, data: dict[str, Any]) -> bool:
        self._ensure_data_dir()

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

        self._cache[file_path.stem] = data
        self._cache_timestamp[file_path.stem] = file_path.stat().st_mtime

        return True

    def _get_encryption_key(self) -> bytes:
        if self._encryption_key:
            return self._encryption_key

        if self.KEY_FILE.exists():
            with open(self.KEY_FILE, "rb") as f:
                self._encryption_key = f.read()
        else:
            self._encryption_key = Fernet.generate_key()
            self._ensure_data_dir()
            with open(self.KEY_FILE, "wb") as f:
                f.write(self._encryption_key)
            self.KEY_FILE.chmod(0o600)

        return self._encryption_key

    def _encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return ""

        key = self._get_encryption_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(plaintext.encode())
        return f"enc:AES256:{encrypted.decode()}"

    def _decrypt(self, ciphertext: str) -> str:
        if not ciphertext or not ciphertext.startswith("enc:AES256:"):
            return ciphertext

        key = self._get_encryption_key()
        fernet = Fernet(key)
        encrypted_part = ciphertext.replace("enc:AES256:", "")
        decrypted = fernet.decrypt(encrypted_part.encode())
        return decrypted.decode()

    def _ensure_data_dir(self) -> None:
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _dict_to_preset(
        self, preset_id: str, dimension: str, data: dict[str, Any], is_custom: bool
    ) -> PresetData:
        return PresetData(
            id=preset_id,
            dimension=dimension,
            name=data.get("name", preset_id),
            description=data.get("description", ""),
            keywords=data.get("keywords", []),
            template=data.get("template", "{description}"),
            metadata=data.get("metadata", {}),
            is_custom=is_custom,
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
        )

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return None


class ReadOnlyDataStore:
    def __init__(self, data_store: DataStore):
        self._store = data_store

    def get_preset(self, dimension: str, preset_id: str) -> Optional[PresetData]:
        return self._store.get_preset(dimension, preset_id)

    def list_presets(self, dimension: Optional[str] = None) -> list[PresetData]:
        return self._store.list_presets(dimension)

    def get_credential(self, provider: str) -> Optional[CredentialData]:
        return self._store.get_credential(provider)

    def get_llm_config(self) -> Optional[dict[str, Any]]:
        return self._store.get_llm_config()

    def get_config(self) -> ConfigData:
        return self._store.get_config()