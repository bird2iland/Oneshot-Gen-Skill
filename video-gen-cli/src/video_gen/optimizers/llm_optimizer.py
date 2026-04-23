import os
from pathlib import Path
from typing import Any

import httpx
import yaml

from .base import BaseOptimizer
from .rule_optimizer import RuleOptimizer


class LLMOptimizer(BaseOptimizer):
    SYSTEM_PROMPT = """你是一个专业的视频提示词优化专家。你的任务是优化用户提供的视频生成提示词，使其更加清晰、具体、易于视频生成模型理解。

优化规则：
1. 保持原意，增强描述的具体性和画面感
2. 添加适当的视觉细节（光影、色彩、构图）
3. 确保提示词简洁有力，避免冗余
4. 使用专业视频术语提升质量
5. 输出语言与输入语言保持一致"""

    USER_PROMPT_TEMPLATE = """请优化以下视频生成提示词：

原始提示词：{prompt}

请输出优化后的提示词，只输出优化结果，不要添加任何解释或说明。"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        provider: str = "openai",
    ):
        self.rule_optimizer = RuleOptimizer()
        self.api_key = api_key
        self.base_url = base_url
        self.model = model or "gpt-4"
        self.provider = provider
        self._load_credentials()

    def _load_credentials(self) -> None:
        if self.api_key:
            return

        credentials_path = Path.home() / ".video_gen" / "credentials.yaml"
        if not credentials_path.exists():
            return

        try:
            with open(credentials_path, "r", encoding="utf-8") as f:
                credentials = yaml.safe_load(f)

            llm_config = credentials.get("llm", {})
            if not self.api_key:
                self.api_key = llm_config.get("api_key")
            if not self.base_url:
                self.base_url = llm_config.get("base_url")
            if self.model == "gpt-4" and llm_config.get("model"):
                self.model = llm_config["model"]
            if llm_config.get("provider"):
                self.provider = llm_config["provider"]
        except (OSError, yaml.YAMLError):
            pass

    async def optimize(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        rule_optimized = await self.rule_optimizer.optimize(prompt, context)

        if not self.api_key or not self.base_url:
            return rule_optimized

        try:
            llm_enhanced = await self._call_llm(rule_optimized)
            return llm_enhanced
        except Exception:
            return rule_optimized

    async def _call_llm(self, prompt: str) -> str:
        headers = self._build_headers()
        payload = self._build_payload(prompt)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]

    def _build_headers(self) -> dict[str, str]:
        if self.provider in ("openai", "deepseek"):
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        elif self.provider == "zhipu":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        else:
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

    def _build_payload(self, prompt: str) -> dict[str, Any]:
        base_payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": self.USER_PROMPT_TEMPLATE.format(prompt=prompt)},
            ],
            "temperature": 0.7,
            "max_tokens": 300,
        }

        if self.provider == "deepseek":
            base_payload["temperature"] = 0.7
        elif self.provider == "zhipu":
            base_payload["temperature"] = 0.7

        return base_payload