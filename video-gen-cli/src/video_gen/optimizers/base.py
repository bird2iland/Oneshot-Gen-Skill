from abc import ABC, abstractmethod
from typing import Any


class BaseOptimizer(ABC):
    @abstractmethod
    async def optimize(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        pass