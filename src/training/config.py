"""Training configuration."""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class TrainingConfig(BaseSettings):
    """Training system configuration."""

    # Paths
    CORPUS_DIR: Path = Path(__file__).parent.parent.parent / "data" / "training_corpus"
    EXERCISES_FILE: Path = CORPUS_DIR / "exercises_v1.json"
    TRAINING_LOGS_DIR: Path = Path(__file__).parent.parent.parent / "data" / "training_logs"
    TRAINING_STATE_FILE: Path = TRAINING_LOGS_DIR / "training_state.json"

    # Ollama configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "neural-chat"
    OLLAMA_TIMEOUT: int = 300  # seconds

    # Generation parameters
    GENERATION_TEMPERATURE: float = 0.7
    GENERATION_TOP_P: float = 0.9
    GENERATION_MAX_TOKENS: int = 2048

    # Training configuration
    TRAINING_MODE: str = "local_only"  # or "hybrid"
    CHECKPOINT_INTERVAL_MINUTES: int = 480  # 8 hours (low budget)
    TRAINING_DURATION_HOURS: int = 12

    # Claude API (for checkpoints)
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-haiku-4-5-20251001"
    CLAUDE_CHECKPOINT_MAX_TOKENS: int = 1500

    # Quality thresholds
    QUALITY_SCORE_THRESHOLD: float = 6.0  # 0-10 scale
    PATTERN_MATCH_MIN_PERCENT: float = 0.6  # 60%
    REGEX_MATCH_MIN_PERCENT: float = 0.5  # 50%

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path(__file__).parent.parent.parent / "data" / "training_logs"

    class Config:
        env_file = ".env.training"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def validate_paths(self) -> None:
        """Validate that required paths exist or can be created."""
        self.CORPUS_DIR.mkdir(parents=True, exist_ok=True)
        self.TRAINING_LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

        if not self.EXERCISES_FILE.exists():
            raise FileNotFoundError(f"Exercises file not found: {self.EXERCISES_FILE}")

        if not self.CORPUS_DIR.exists() or not list(self.CORPUS_DIR.glob("*.md")):
            raise FileNotFoundError(f"No corpus files found in: {self.CORPUS_DIR}")

    def validate_training_mode(self) -> None:
        """Validate training mode configuration."""
        if self.TRAINING_MODE == "hybrid":
            if not self.ANTHROPIC_API_KEY:
                raise ValueError("TRAINING_MODE=hybrid requires ANTHROPIC_API_KEY")
        elif self.TRAINING_MODE != "local_only":
            raise ValueError(f"Invalid TRAINING_MODE: {self.TRAINING_MODE}")

    def is_hybrid_mode(self) -> bool:
        """Check if running in hybrid mode."""
        return self.TRAINING_MODE == "hybrid"

    def __init__(self, **data):
        super().__init__(**data)
        self.validate_paths()
        self.validate_training_mode()


# Singleton instance
_config: Optional[TrainingConfig] = None


def get_training_config() -> TrainingConfig:
    """Get or create training config singleton."""
    global _config

    if _config is None:
        _config = TrainingConfig()

    return _config
