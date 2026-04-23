import pytest

from video_gen.core.types import OptimizationMode
from video_gen.optimizers import RuleOptimizer, LLMOptimizer, create_optimizer


class TestRuleOptimizer:
    @pytest.mark.asyncio
    async def test_optimize_injects_prefix(self):
        optimizer = RuleOptimizer()
        result = await optimizer.optimize("test prompt")
        assert result.startswith("高质量视频生成：")

    @pytest.mark.asyncio
    async def test_optimize_injects_suffix(self):
        optimizer = RuleOptimizer()
        result = await optimizer.optimize("test prompt")
        assert result.endswith(" | 4K超清画质")

    @pytest.mark.asyncio
    async def test_optimize_removes_forbidden_words(self):
        optimizer = RuleOptimizer()
        result = await optimizer.optimize("this contains 暴力 and 政治敏感 words")
        assert "暴力" not in result
        assert "政治敏感" not in result
        assert "contains" in result
        assert "words" in result

    @pytest.mark.asyncio
    async def test_optimize_removes_duplicates(self):
        optimizer = RuleOptimizer()
        result = await optimizer.optimize(" test test word word")
        words = result.split()
        test_count = sum(1 for w in words if w.lower().strip(".,!?，。！？") == "test")
        word_count = sum(1 for w in words if w.lower().strip(".,!?，。！？") == "word")
        assert test_count <= 1
        assert word_count <= 1

    @pytest.mark.asyncio
    async def test_optimize_truncates_long_prompt(self):
        optimizer = RuleOptimizer()
        long_prompt = "word " * 100
        result = await optimizer.optimize(long_prompt)
        assert len(result) <= 200

    @pytest.mark.asyncio
    async def test_optimize_preserves_short_prompt(self):
        optimizer = RuleOptimizer()
        short_prompt = "short prompt"
        result = await optimizer.optimize(short_prompt)
        assert "short" in result
        assert "prompt" in result

    @pytest.mark.asyncio
    async def test_optimize_full_pipeline(self):
        optimizer = RuleOptimizer()
        result = await optimizer.optimize("test 暴力 test duplicate duplicate")
        assert "高质量视频生成：" in result
        assert " | 4K超清画质" in result
        assert "暴力" not in result
        assert len(result) <= 200

    @pytest.mark.asyncio
    async def test_optimize_does_not_duplicate_prefix(self):
        optimizer = RuleOptimizer()
        result1 = await optimizer.optimize("test")
        result2 = await optimizer.optimize(result1)
        prefix_count = result2.count("高质量视频生成：")
        assert prefix_count == 1

    @pytest.mark.asyncio
    async def test_optimize_does_not_duplicate_suffix(self):
        optimizer = RuleOptimizer()
        result1 = await optimizer.optimize("test")
        result2 = await optimizer.optimize(result1)
        suffix_count = result2.count(" | 4K超清画质")
        assert suffix_count == 1


class TestRuleOptimizerPrivateMethods:
    def test_inject_prefix_adds_prefix(self):
        optimizer = RuleOptimizer()
        result = optimizer._inject_prefix("test")
        assert result == "高质量视频生成：test"

    def test_inject_prefix_skips_existing(self):
        optimizer = RuleOptimizer()
        result = optimizer._inject_prefix("高质量视频生成：test")
        assert result == "高质量视频生成：test"

    def test_inject_suffix_adds_suffix(self):
        optimizer = RuleOptimizer()
        result = optimizer._inject_suffix("test")
        assert result == "test | 4K超清画质"

    def test_inject_suffix_skips_existing(self):
        optimizer = RuleOptimizer()
        result = optimizer._inject_suffix("test | 4K超清画质")
        assert result == "test | 4K超清画质"

    def test_remove_forbidden_words_removes_all(self):
        optimizer = RuleOptimizer()
        result = optimizer._remove_forbidden_words("暴力色情政治敏感违法低俗")
        assert "暴力" not in result
        assert "色情" not in result
        assert "政治敏感" not in result
        assert "违法" not in result
        assert "低俗" not in result

    def test_remove_forbidden_words_preserves_others(self):
        optimizer = RuleOptimizer()
        result = optimizer._remove_forbidden_words("normal text 暴力 more text")
        assert "normal" in result
        assert "text" in result
        assert "暴力" not in result

    def test_remove_duplicates_basic(self):
        optimizer = RuleOptimizer()
        result = optimizer._remove_duplicates("hello hello world world")
        words = result.lower().split()
        assert words.count("hello") == 1
        assert words.count("world") == 1

    def test_remove_duplicates_case_insensitive(self):
        optimizer = RuleOptimizer()
        result = optimizer._remove_duplicates("Hello HELLO hello")
        words = [w.lower() for w in result.split()]
        assert words.count("hello") == 1

    def test_remove_duplicates_preserves_punctuation_variants(self):
        optimizer = RuleOptimizer()
        result = optimizer._remove_duplicates("hello, hello. hello!")
        assert "hello" in result.lower()

    def test_truncate_short_prompt_unchanged(self):
        optimizer = RuleOptimizer()
        short = "short"
        result = optimizer._truncate(short)
        assert result == short

    def test_truncate_long_prompt(self):
        optimizer = RuleOptimizer()
        long = "a" * 300
        result = optimizer._truncate(long)
        assert len(result) <= 200

    def test_truncate_preserves_word_boundary(self):
        optimizer = RuleOptimizer()
        long = "word " * 100
        result = optimizer._truncate(long)
        assert len(result) <= 200


class TestCreateOptimizer:
    def test_create_optimizer_returns_rule_optimizer_for_fast(self):
        optimizer = create_optimizer(mode=OptimizationMode.FAST)
        assert isinstance(optimizer, RuleOptimizer)

    def test_create_optimizer_returns_llm_optimizer_for_quality(self):
        optimizer = create_optimizer(
            mode=OptimizationMode.QUALITY,
            llm_api_key="test-key",
        )
        assert isinstance(optimizer, LLMOptimizer)

    def test_create_optimizer_defaults_to_fast(self):
        optimizer = create_optimizer()
        assert isinstance(optimizer, RuleOptimizer)

    def test_create_optimizer_passes_llm_config(self):
        optimizer = create_optimizer(
            mode=OptimizationMode.QUALITY,
            llm_api_key="test-key",
            llm_model="gpt-4",
            llm_base_url="https://api.example.com",
        )
        assert isinstance(optimizer, LLMOptimizer)
        assert optimizer.api_key == "test-key"
        assert optimizer.model == "gpt-4"
        assert optimizer.base_url == "https://api.example.com"