import pytest
from src.ollama_client import OllamaClient


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
