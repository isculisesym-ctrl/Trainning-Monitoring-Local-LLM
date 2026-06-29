import httpx
import pytest

from src.ollama_client import OllamaClient, OllamaClientError


def _handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/api/generate":
        return httpx.Response(200, json={"response": "hi there", "prompt_eval_count": 2, "eval_count": 3})
    if request.url.path == "/api/tags":
        return httpx.Response(
            200,
            json={
                "models": [
                    {
                        "name": "qwen:7b-coder",
                        "size": 1073741824,
                        "details": {"parameter_size": "7B", "quantization_level": "Q4_0"},
                    }
                ]
            },
        )
    return httpx.Response(404)


@pytest.mark.asyncio
async def test_ollama_client_init():
    client = OllamaClient()
    assert client.model == "qwen:7b-coder"
    assert "localhost" in client.base_url


@pytest.mark.asyncio
async def test_ollama_connection_check():
    client = OllamaClient()
    is_connected = await client.check_connection()
    assert isinstance(is_connected, bool)


@pytest.mark.asyncio
async def test_generate_parses_ollama_response():
    client = OllamaClient()
    client.client = httpx.AsyncClient(transport=httpx.MockTransport(_handler))
    try:
        result = await client.generate("prompt", temperature=0.0)
        assert result["text"] == "hi there"
        assert result["tokens_input"] == 2
        assert result["tokens_output"] == 3
    finally:
        await client.client.aclose()


@pytest.mark.asyncio
async def test_get_models_returns_list():
    client = OllamaClient()
    client.client = httpx.AsyncClient(transport=httpx.MockTransport(_handler))
    try:
        models = await client.get_models()
        assert models[0]["name"] == "qwen:7b-coder"
    finally:
        await client.client.aclose()


@pytest.mark.asyncio
async def test_generate_without_context_raises():
    client = OllamaClient()
    with pytest.raises(OllamaClientError):
        await client.generate("prompt")
