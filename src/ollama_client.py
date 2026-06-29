import httpx
import logging
import json
from typing import Optional, AsyncGenerator
from src.config import settings

logger = logging.getLogger(__name__)


class OllamaClientError(Exception):
    pass


class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None, timeout: int = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def check_connection(self) -> bool:
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
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        stream: bool = False
    ) -> Optional[dict]:
        if not self.client:
            raise OllamaClientError("Client no inicializado. Usa 'async with OllamaClient() as client'")

        temperature = temperature or settings.temperature
        top_p = top_p or settings.top_p

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens or settings.max_tokens,
            }
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()

            if stream:
                return response
            else:
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
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
    ) -> AsyncGenerator[str, None]:
        if not self.client:
            raise OllamaClientError("Client no inicializado")

        temperature = temperature or settings.temperature
        top_p = top_p or settings.top_p

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens or settings.max_tokens,
            }
        }

        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]

        except httpx.HTTPError as e:
            logger.error(f"Ollama stream generation failed: {e}")
            raise OllamaClientError(f"Stream generation failed: {str(e)}")

    async def get_models(self) -> list:
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
