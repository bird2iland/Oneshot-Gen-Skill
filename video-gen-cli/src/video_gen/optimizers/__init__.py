from video_gen.core.types import OptimizationMode

from .base import BaseOptimizer
from .llm_optimizer import LLMOptimizer
from .rule_optimizer import RuleOptimizer

__all__ = [
    "BaseOptimizer",
    "RuleOptimizer",
    "LLMOptimizer",
    "create_optimizer",
]


def create_optimizer(
    mode: OptimizationMode = OptimizationMode.FAST,
    llm_api_key: str | None = None,
    llm_model: str | None = None,
    llm_base_url: str | None = None,
) -> BaseOptimizer:
    if mode == OptimizationMode.QUALITY:
        return LLMOptimizer(
            api_key=llm_api_key,
            base_url=llm_base_url,
            model=llm_model,
        )
    else:
        return RuleOptimizer()