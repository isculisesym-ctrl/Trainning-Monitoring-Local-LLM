from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / ``.env``.

    Field names map case-insensitively to env vars (e.g. ``gateway_host`` <-
    ``GATEWAY_HOST``), so no explicit ``env=`` aliases are required.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    gateway_host: str = Field(default="127.0.0.1")
    gateway_port: int = Field(default=8000)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="qwen:7b-coder")
    ollama_timeout: int = Field(default=300)

    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.9)
    max_tokens: int = Field(default=2048)

    cache_type: str = Field(default="file")
    cache_max_size: int = Field(default=1000)
    # Conservative default: only collapses near-duplicate prompts (whitespace,
    # casing, word order, trivial filler). Lower it to cache more aggressively,
    # at the risk of serving a cached answer to a differently-intended prompt.
    semantic_similarity_threshold: float = Field(default=0.95)
    cache_dir: Path = Field(default=Path("data/cache"))

    rate_limit_requests: int = Field(default=100)
    rate_limit_period: int = Field(default=60)

    prometheus_enabled: bool = Field(default=True)

    def model_post_init(self, __context: object) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        Path("data/logs").mkdir(parents=True, exist_ok=True)


settings = Settings()
