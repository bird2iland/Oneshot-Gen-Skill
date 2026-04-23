from pathlib import Path
from typing import Optional

from video_gen.core.data_store import ConfigData, DataStore

_data_store: Optional[DataStore] = None


def set_data_store(data_store: DataStore) -> None:
    global _data_store
    _data_store = data_store


def get_data_store() -> DataStore:
    global _data_store
    if _data_store is None:
        _data_store = DataStore()
    return _data_store


class Config:
    def __init__(self, config_data: Optional[ConfigData] = None):
        if config_data:
            self._data = config_data
        else:
            self._data = get_data_store().get_config()
    
    @property
    def output_dir(self) -> Path:
        return self._data.output_dir
    
    @property
    def default_provider(self) -> str:
        return self._data.default_provider
    
    @property
    def default_model(self) -> str:
        return self._data.default_model
    
    @property
    def default_visual_preset(self) -> Optional[str]:
        return self._data.default_visual_preset
    
    @property
    def default_time_preset(self) -> Optional[str]:
        return self._data.default_time_preset
    
    @property
    def default_camera_preset(self) -> Optional[str]:
        return self._data.default_camera_preset
    
    @property
    def default_duration(self) -> int:
        return self._data.default_duration
    
    @property
    def default_ratio(self) -> str:
        return self._data.default_ratio
    
    @property
    def default_mode(self) -> str:
        return self._data.default_mode
    
    @property
    def verbose(self) -> bool:
        return self._data.verbose
    
    @property
    def poll_interval(self) -> float:
        return self._data.poll_interval
    
    @property
    def poll_max_wait(self) -> float:
        return self._data.poll_max_wait
    
    @property
    def poll_retry_count(self) -> int:
        return self._data.poll_retry_count
    
    @classmethod
    def load(cls, data_store: Optional[DataStore] = None) -> "Config":
        if data_store:
            set_data_store(data_store)
        return cls()
    
    def save(self) -> None:
        data_store = get_data_store()
        data_store.save_config(self._data)
    
    def set_output_dir(self, value: Path) -> None:
        self._data.output_dir = value
    
    def set_default_provider(self, value: str) -> None:
        self._data.default_provider = value
    
    def set_default_model(self, value: str) -> None:
        self._data.default_model = value
    
    def set_default_duration(self, value: int) -> None:
        self._data.default_duration = value
    
    def set_verbose(self, value: bool) -> None:
        self._data.verbose = value
    
    def to_dict(self) -> dict[str, str | int | float | bool | None]:
        return {
            "output_dir": str(self.output_dir),
            "default_provider": self.default_provider,
            "default_model": self.default_model,
            "default_visual_preset": self.default_visual_preset,
            "default_time_preset": self.default_time_preset,
            "default_camera_preset": self.default_camera_preset,
            "default_duration": self.default_duration,
            "default_ratio": self.default_ratio,
            "default_mode": self.default_mode,
            "verbose": self.verbose,
            "poll_interval": self.poll_interval,
            "poll_max_wait": self.poll_max_wait,
            "poll_retry_count": self.poll_retry_count,
        }