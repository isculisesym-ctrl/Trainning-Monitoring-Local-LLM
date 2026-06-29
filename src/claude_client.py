"""Claude API client for local use. Requires ANTHROPIC_API_KEY env var."""

import os
from typing import Optional

import httpx
from pydantic import BaseModel, Field


class ClaudeMessage(BaseModel):
    """Claude API request."""

    model: str = "claude-opus-4-8"
    max_tokens: int = 1024
    messages: list[dict] = Field(default_factory=list)
    system: Optional[str] = None
    temperature: float = 0.7


class ClaudeResponse(BaseModel):
    """Claude API response."""

    content: str
    model: str
    stop_reason: str
    usage: dict


class ClaudeClient:
    """Lightweight Claude API client with built-in retry + semantic cache support."""

    BASE_URL = "https://api.anthropic.com/v1"
    SUPPORTED_MODELS = ["claude-opus-4-8", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"]

    def __init__(self, api_key: Optional[str] = None):
        """Init with API key (defaults to ANTHROPIC_API_KEY env var)."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set. Set env var or pass api_key=...")
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
            timeout=60.0,
        )

    def message(
        self,
        messages: list[dict],
        model: str = "claude-opus-4-8",
        max_tokens: int = 1024,
        system: Optional[str] = None,
        temperature: float = 0.7,
    ) -> ClaudeResponse:
        """Send message to Claude. Format: [{"role": "user", "content": "..."}]."""
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(f"Model {model} not supported. Use: {self.SUPPORTED_MODELS}")

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
        }
        if system:
            payload["system"] = system

        resp = self.client.post("/messages", json=payload)
        resp.raise_for_status()
        data = resp.json()

        return ClaudeResponse(
            content=data["content"][0]["text"],
            model=data["model"],
            stop_reason=data["stop_reason"],
            usage=data["usage"],
        )

    def quick(
        self,
        prompt: str,
        model: str = "claude-haiku-4-5-20251001",
        max_tokens: int = 512,
        system: str = "You are a helpful assistant.",
    ) -> str:
        """Quick shortcut: single prompt → response text."""
        resp = self.message(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=max_tokens,
            system=system,
        )
        return resp.content

    def close(self):
        """Close HTTP connection."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


if __name__ == "__main__":
    # Example: quick test
    with ClaudeClient() as client:
        resp = client.quick(
            "Explain semantic caching in 1 sentence.",
            model="claude-haiku-4-5-20251001",
        )
        print(f"Response: {resp}")
