from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PresetDimension(Enum):
    VISUAL = "visual"
    TIME = "time"
    CAMERA = "camera"


class OptimizationMode(Enum):
    FAST = "fast"
    QUALITY = "quality"


@dataclass
class PresetConfig:
    id: str
    name: str
    description: str
    keywords: list[str] = field(default_factory=list)
    template: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class PollConfig:
    interval: float = 2.0
    max_wait: float = 300.0
    retry_count: int = 3
    retry_interval: float = 1.0


@dataclass
class GenerationRequest:
    images: list[str] = field(default_factory=list)
    visual_preset: Optional[str] = None
    time_preset: Optional[str] = None
    camera_preset: Optional[str] = None
    description: str = ""
    mode: OptimizationMode = OptimizationMode.FAST
    provider: str = "jimeng"
    duration: float = 5.0
    ratio: str = "16:9"
    model: Optional[str] = None
    poll_config: PollConfig = field(default_factory=PollConfig)


@dataclass
class GenerationResult:
    success: bool = False
    video_path: Optional[str] = None
    prompt_path: Optional[str] = None
    task_id: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    suggestion: Optional[str] = None