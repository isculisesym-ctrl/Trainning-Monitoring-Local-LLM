from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    gateway_host: str = Field(default="127.0.0.1", env="GATEWAY_HOST")
    gateway_port: int = Field(default=8000, env="GATEWAY_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen:7b-coder", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(default=300, env="OLLAMA_TIMEOUT")

    temperature: float = Field(default=0.7, env="TEMPERATURE")
    top_p: float = Field(default=0.9, env="TOP_P")
    max_tokens: int = Field(default=2048, env="MAX_TOKENS")

    cache_type: str = Field(default="file", env="CACHE_TYPE")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")
    semantic_similarity_threshold: float = Field(default=0.85, env="SEMANTIC_SIMILARITY_THRESHOLD")
    cache_dir: Path = Field(default=Path("data/cache"), env="CACHE_DIR")

    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")

    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")

    class Config:
        env_file = ".env"
        case_sensitive = False

    def model_post_init(self, __context):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        Path("data/logs").mkdir(parents=True, exist_ok=True)


settings = Settings()
