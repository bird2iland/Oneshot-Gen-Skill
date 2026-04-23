from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from video_gen.core import Config, DataStore, ReadOnlyDataStore, VideoEngine
from video_gen.core.types import OptimizationMode, PresetDimension
from video_gen.optimizers import create_optimizer
from video_gen.presets import PresetComposer, PresetRegistry, register_default_presets
from video_gen.providers import JimengStatusChecker


@dataclass
class AgentToolsConfig:
    output_dir: Path = field(default_factory=lambda: Path("output"))
    data_dir: Optional[Path] = None
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None


class AgentTools:
    _instance: Optional["AgentTools"] = None
    _initialized: bool = False

    def __new__(cls, config: Optional[AgentToolsConfig] = None) -> "AgentTools":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: Optional[AgentToolsConfig] = None):
        if self._initialized:
            return

        self._config = config or AgentToolsConfig()
        self._ensure_output_dirs()

        register_default_presets()
        self._registry = PresetRegistry()
        self._composer = PresetComposer(self._registry)
        self._status_checker = JimengStatusChecker()
        
        self._data_store = DataStore(data_dir=self._config.data_dir)
        self._read_only_store = ReadOnlyDataStore(self._data_store)

        self._engine: Optional[VideoEngine] = None
        AgentTools._initialized = True

    def _ensure_output_dirs(self) -> None:
        self._config.output_dir.mkdir(parents=True, exist_ok=True)
        (self._config.output_dir / "prompts").mkdir(parents=True, exist_ok=True)

    def _get_engine(self) -> VideoEngine:
        if self._engine is None:
            engine_config = Config(
                output_dir=self._config.output_dir,
                llm_api_key=self._config.llm_api_key,
                llm_model=self._config.llm_model,
                llm_base_url=self._config.llm_base_url,
            )
            self._engine = VideoEngine(config=engine_config)
        return self._engine

    def _preset_to_dict(self, preset_data) -> dict[str, Any]:
        from video_gen.core import PresetData
        if isinstance(preset_data, PresetData):
            return {
                "id": preset_data.id,
                "name": preset_data.name,
                "dimension": preset_data.dimension,
                "description": preset_data.description,
                "keywords": preset_data.keywords,
                "template": preset_data.template,
                "metadata": preset_data.metadata,
                "is_custom": preset_data.is_custom,
            }
        return {}

    async def preset_list(
        self, dimension: Optional[str] = None
    ) -> list[dict[str, Any]]:
        try:
            presets = self._read_only_store.list_presets(dimension=dimension)
            return [self._preset_to_dict(p) for p in presets]
        except Exception as e:
            return [{"error": str(e), "error_code": "PRESET_LIST_ERROR"}]

    async def preset_show(self, preset_id: str, dimension: str) -> dict[str, Any]:
        try:
            preset_data = self._read_only_store.get_preset(dimension=dimension, preset_id=preset_id)
            if not preset_data:
                return {
                    "success": False,
                    "error": f"Preset not found: {preset_id}",
                    "error_code": "PRESET_NOT_FOUND",
                    "suggestion": f"Use preset_list to see available presets for {dimension}",
                }

            return {
                "success": True,
                "preset": self._preset_to_dict(preset_data),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "PRESET_SHOW_ERROR",
                "suggestion": "An error occurred while fetching preset details",
            }

    async def optimize_prompt(
        self,
        visual_preset: Optional[str] = None,
        time_preset: Optional[str] = None,
        camera_preset: Optional[str] = None,
        description: str = "",
        mode: str = "fast",
    ) -> str:
        try:
            composed_prompt = await self._composer.compose(
                visual=visual_preset,
                time=time_preset,
                camera=camera_preset,
                description=description,
            )

            opt_mode = OptimizationMode.QUALITY if mode.lower() == "quality" else OptimizationMode.FAST
            optimizer = create_optimizer(
                mode=opt_mode,
                llm_api_key=self._config.llm_api_key,
                llm_model=self._config.llm_model,
                llm_base_url=self._config.llm_base_url,
            )

            optimized_prompt = await optimizer.optimize(
                composed_prompt,
                context={
                    "visual_preset": visual_preset,
                    "time_preset": time_preset,
                    "camera_preset": camera_preset,
                },
            )

            return optimized_prompt
        except Exception as e:
            return f"Error optimizing prompt: {str(e)}"

    async def export_prompt(
        self,
        prompt: str,
        filename: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> str:
        try:
            base_dir = Path(output_dir) if output_dir else self._config.output_dir
            prompt_dir = base_dir / "prompts"
            prompt_dir.mkdir(parents=True, exist_ok=True)

            if filename:
                prompt_path = prompt_dir / filename
                if not filename.endswith(".txt"):
                    prompt_path = prompt_dir / f"{filename}.txt"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                prompt_path = prompt_dir / f"prompt_{timestamp}.txt"

            prompt_path.write_text(prompt, encoding="utf-8")
            return str(prompt_path)
        except Exception as e:
            return f"Error exporting prompt: {str(e)}"

    async def generate_video(
        self,
        images: list[str],
        visual_preset: Optional[str] = None,
        time_preset: Optional[str] = None,
        camera_preset: Optional[str] = None,
        description: str = "",
        mode: str = "fast",
        duration: float = 5.0,
        ratio: str = "16:9",
        model: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            engine = self._get_engine()
            opt_mode = OptimizationMode.QUALITY if mode.lower() == "quality" else OptimizationMode.FAST

            result = await engine.generate(
                images=images,
                visual_preset=visual_preset,
                time_preset=time_preset,
                camera_preset=camera_preset,
                description=description,
                mode=opt_mode,
                duration=duration,
                ratio=ratio,
                model=model,
            )

            return result
        except Exception as e:
            return {
                "success": False,
                "video_path": None,
                "prompt_path": None,
                "task_id": None,
                "error": str(e),
                "error_code": "GENERATION_ERROR",
                "suggestion": "An error occurred during video generation",
            }

    async def check_status(self) -> dict[str, Any]:
        try:
            status = await self._status_checker.check_full_status()
            
            data_store_status = {
                "presets_file": self._data_store.PRESETS_FILE.exists(),
                "credentials_file": self._data_store.CREDENTIALS_FILE.exists(),
                "config_file": self._data_store.CONFIG_FILE.exists(),
            }
            
            llm_config = self._read_only_store.get_llm_config()
            
            return {
                "success": True,
                "installed": status.installed,
                "version": status.version,
                "logged_in": status.logged_in,
                "user_info": status.user_info,
                "error": status.error,
                "install_guide": self._status_checker.get_install_guide() if not status.installed else None,
                "data_store": data_store_status,
                "llm_configured": llm_config is not None,
            }
        except Exception as e:
            return {
                "success": False,
                "installed": False,
                "version": None,
                "logged_in": False,
                "user_info": None,
                "error": str(e),
                "install_guide": self._status_checker.get_install_guide(),
            }

    @classmethod
    def reset(cls) -> None:
        cls._instance = None
        cls._initialized = False


__all__ = ["AgentTools", "AgentToolsConfig"]