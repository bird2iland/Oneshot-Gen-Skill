from typing import Optional

from .base import BaseProvider
from .jimeng import JimengProvider
from .kling import KlingProvider


class ProviderRouter:
    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}

    def register(self, name: str, provider: BaseProvider) -> None:
        self._providers[name] = provider

    def get(self, name: str) -> BaseProvider:
        if name not in self._providers:
            raise KeyError(f"Provider '{name}' not found")
        return self._providers[name]

    def resolve(self, provider_hint: Optional[str] = None) -> BaseProvider:
        if provider_hint and provider_hint in self._providers:
            return self._providers[provider_hint]

        if "jimeng" in self._providers:
            return self._providers["jimeng"]

        if self._providers:
            return next(iter(self._providers.values()))

        raise RuntimeError("No providers registered")

    def list(self) -> list[str]:
        return list(self._providers.keys())

    def unregister(self, name: str) -> bool:
        if name in self._providers:
            del self._providers[name]
            return True
        return False

    def has(self, name: str) -> bool:
        return name in self._providers


_default_router: Optional[ProviderRouter] = None


def get_default_router() -> ProviderRouter:
    global _default_router
    if _default_router is None:
        _default_router = ProviderRouter()
        _default_router.register("jimeng", JimengProvider())
        _default_router.register("kling", KlingProvider())
    return _default_router


def reset_router() -> None:
    global _default_router
    _default_router = None