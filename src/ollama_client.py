import json
import logging
from typing import AsyncGenerator, List, Optional

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class OllamaClientError(Exception):
    pass


class OllamaClient:
    """Async HTTP client for a local Ollama server.

    Use as an async context manager so the underlying ``httpx.AsyncClient`` is
    opened and closed deterministically::

        async with OllamaClient() as client:
            result = await client.generate(prompt="...")
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "OllamaClient":
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if self.client:
            await self.client.aclose()

    async def check_connection(self) -> bool:
        """Return True if the Ollama server answers ``GET /api/tags`` with 200."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection check failed: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> dict:
        """Generate a completion for ``prompt`` (non-streaming).

        Returns a dict with ``text``, ``tokens_input`` and ``tokens_output``.
        ``None`` parameters fall back to the configured defaults; explicit
        ``0.0`` values (e.g. ``temperature=0.0``) are preserved.
        """
        if not self.client:
            raise OllamaClientError("Client no inicializado. Usa 'async with OllamaClient() as client'")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature if temperature is not None else settings.temperature,
                "top_p": top_p if top_p is not None else settings.top_p,
                "num_predict": max_tokens if max_tokens is not None else settings.max_tokens,
            },
        }

        try:
            response = await self.client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()

            data = response.json()
            return {
                "text": data.get("response", ""),
                "tokens_input": data.get("prompt_eval_count", 0),
                "tokens_output": data.get("eval_count", 0),
            }

        except httpx.HTTPError as e:
            logger.error(f"Ollama generation failed: {e}")
            raise OllamaClientError(f"Failed to generate: {str(e)}")

    async def stream_generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Yield response chunks for ``prompt`` as they arrive from Ollama."""
        if not self.client:
            raise OllamaClientError("Client no inicializado")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature if temperature is not None else settings.temperature,
                "top_p": top_p if top_p is not None else settings.top_p,
                "num_predict": max_tokens if max_tokens is not None else settings.max_tokens,
            },
        }

        try:
            async with self.client.stream("POST", f"{self.base_url}/api/generate", json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]

        except httpx.HTTPError as e:
            logger.error(f"Ollama stream generation failed: {e}")
            raise OllamaClientError(f"Stream generation failed: {str(e)}")

    async def get_models(self) -> List[dict]:
        """Return the list of models reported by Ollama's ``/api/tags``."""
        if not self.client:
            raise OllamaClientError("Client no inicializado")

        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])

        except httpx.HTTPError as e:
            logger.error(f"Failed to get models: {e}")
            raise OllamaClientError(f"Failed to get models: {str(e)}")
