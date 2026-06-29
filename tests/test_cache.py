import pytest
import pytest_asyncio
from src.cache import Cache
from pathlib import Path
import tempfile


@pytest_asyncio.fixture
async def cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        c = Cache(cache_dir=tmpdir)
        yield c


@pytest.mark.asyncio
async def test_cache_set_get(cache):
    prompt = "Test prompt"
    response = "Test response"

    await cache.set(prompt, response, 10, 20)
    result = await cache.get(prompt)

    assert result is not None
    assert result["response"] == response


@pytest.mark.asyncio
async def test_cache_not_found(cache):
    result = await cache.get("Nonexistent prompt")
    assert result is None


@pytest.mark.asyncio
async def test_cache_clear(cache):
    await cache.set("Prompt", "Response", 10, 20)
    await cache.clear()
    result = await cache.get("Prompt")
    assert result is None
