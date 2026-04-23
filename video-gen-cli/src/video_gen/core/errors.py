from dataclasses import dataclass


@dataclass
class VideoGenError(Exception):
    code: str
    message: str
    suggestion: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
            "suggestion": self.suggestion,
        }


class JimengNotInstalledError(VideoGenError):
    def __init__(self) -> None:
        super().__init__(
            code="JIMENG_NOT_INSTALLED",
            message="Jimeng video generation tool is not installed",
            suggestion="Please install Jimeng and try again",
        )


class JimengNotLoggedInError(VideoGenError):
    def __init__(self) -> None:
        super().__init__(
            code="JIMENG_NOT_LOGGED_IN",
            message="Jimeng user is not logged in",
            suggestion="Please login to Jimeng and try again",
        )


class JimengVersionMismatchError(VideoGenError):
    def __init__(self, current_version: str, required_version: str) -> None:
        super().__init__(
            code="JIMENG_VERSION_MISMATCH",
            message=f"Jimeng version mismatch: current={current_version}, required={required_version}",
            suggestion=f"Please upgrade Jimeng to version {required_version} or higher",
        )


class LLMNotConfiguredError(VideoGenError):
    def __init__(self) -> None:
        super().__init__(
            code="LLM_NOT_CONFIGURED",
            message="LLM provider is not configured",
            suggestion="Please configure LLM provider in settings",
        )


class InvalidPresetCombinationError(VideoGenError):
    def __init__(self, preset_type: str, preset_id: str) -> None:
        super().__init__(
            code="INVALID_PRESET_COMBINATION",
            message=f"Invalid preset combination: {preset_type}={preset_id}",
            suggestion="Please check preset configuration and try again",
        )


class NetworkError(VideoGenError):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            code="NETWORK_ERROR",
            message=f"Network error occurred: {detail}" if detail else "Network error occurred",
            suggestion="Please check your network connection and try again",
        )


class TaskTimeoutError(VideoGenError):
    def __init__(self, task_id: str, wait_time: float) -> None:
        super().__init__(
            code="TASK_TIMEOUT",
            message=f"Task {task_id} timed out after {wait_time} seconds",
            suggestion="Please try again or increase max_wait time",
        )


class InvalidParameterError(VideoGenError):
    def __init__(self, param_name: str, param_value: str, reason: str = "") -> None:
        message = f"Invalid parameter {param_name}={param_value}"
        if reason:
            message += f": {reason}"
        super().__init__(
            code="INVALID_PARAMETER",
            message=message,
            suggestion="Please check the parameter value and try again",
        )