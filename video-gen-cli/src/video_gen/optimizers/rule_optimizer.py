import re
from typing import Any

from .base import BaseOptimizer


class RuleOptimizer(BaseOptimizer):
    RULES: dict[str, Any] = {
        "prefix": "高质量视频生成：",
        "suffix": " | 4K超清画质",
        "forbidden_words": ["暴力", "色情", "政治敏感", "违法", "低俗"],
        "format_rules": {
            "max_length": 200,
            "remove_duplicates": True,
        },
    }

    async def optimize(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        result = prompt

        result = self._inject_prefix(result)
        result = self._inject_suffix(result)
        result = self._remove_forbidden_words(result)
        result = self._remove_duplicates(result)
        result = self._truncate(result)

        return result

    def _inject_prefix(self, prompt: str) -> str:
        prefix = self.RULES["prefix"]
        if prefix and not prompt.startswith(prefix):
            return f"{prefix}{prompt}"
        return prompt

    def _inject_suffix(self, prompt: str) -> str:
        suffix = self.RULES["suffix"]
        if suffix and not prompt.endswith(suffix):
            return f"{prompt}{suffix}"
        return prompt

    def _remove_forbidden_words(self, prompt: str) -> str:
        forbidden_words = self.RULES["forbidden_words"]
        result = prompt
        for word in forbidden_words:
            result = result.replace(word, "")
        return result

    def _remove_duplicates(self, prompt: str) -> str:
        if not self.RULES["format_rules"]["remove_duplicates"]:
            return prompt

        words = prompt.split()
        seen: set[str] = set()
        unique_words: list[str] = []

        for word in words:
            normalized = word.lower().strip(".,!?，。！？")
            if normalized not in seen:
                seen.add(normalized)
                unique_words.append(word)

        return " ".join(unique_words)

    def _truncate(self, prompt: str) -> str:
        max_length = self.RULES["format_rules"]["max_length"]
        if len(prompt) <= max_length:
            return prompt

        truncated = prompt[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.7:
            truncated = truncated[:last_space]

        return truncated.rstrip()