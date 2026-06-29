import json
import tempfile
from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from src.cache import Cache


@pytest_asyncio.fixture
async def cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Cache(cache_dir=tmpdir)


@pytest.mark.asyncio
async def test_cache_set_get(cache):
    await cache.set("Test prompt", "Test response", 10, 20)
    result = await cache.get("Test prompt")

    assert result is not None
    assert result["response"] == "Test response"
    assert result["cached"] is True


@pytest.mark.asyncio
async def test_cache_not_found(cache):
    assert await cache.get("Nonexistent prompt") is None


@pytest.mark.asyncio
async def test_cache_clear(cache):
    await cache.set("Prompt", "Response", 10, 20)
    await cache.clear()
    assert await cache.get("Prompt") is None


@pytest.mark.asyncio
async def test_cache_semantic_hit_beyond_exact_hash(cache):
    """A prompt that differs only by casing/word-order (different SHA-256, so the
    exact-hash file misses) must still hit via the semantic scan."""
    await cache.set("Write a hello world function", "RESP", 5, 10)

    # Different raw string -> different hash file, but identical embedding.
    result = await cache.get("write a HELLO world function")
    assert result is not None
    assert result["response"] == "RESP"


@pytest.mark.asyncio
async def test_cache_semantic_miss_for_different_intent(cache):
    """Genuinely different prompts must NOT collapse (no wrong cached answer)."""
    await cache.set("Write a python function to sort a list", "SORT", 5, 10)
    assert await cache.get("Explain quantum entanglement to a child") is None


@pytest.mark.asyncio
async def test_cache_expiration(cache):
    await cache.set("Prompt to expire", "OLD", 5, 10)

    # Backdate the stored entry past the 24h TTL.
    cache_file = next(cache.cache_dir.glob("*.json"))
    data = json.loads(cache_file.read_text(encoding="utf-8"))
    data["timestamp"] = (datetime.utcnow() - timedelta(hours=25)).isoformat() + "Z"
    cache_file.write_text(json.dumps(data), encoding="utf-8")

    assert await cache.get("Prompt to expire") is None
    # Expired file is purged on access.
    assert list(cache.cache_dir.glob("*.json")) == []


@pytest.mark.asyncio
async def test_cache_stats(cache):
    await cache.set("a prompt", "r", 1, 2)
    stats = await cache.get_stats()
    assert stats["total_entries"] == 1
    assert stats["ttl_hours"] == 24
