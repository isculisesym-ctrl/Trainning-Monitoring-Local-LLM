import hashlib
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

EMBEDDING_DIM = 128


def setup_logging(log_level: str = "INFO", log_dir: str = "data/logs") -> logging.Logger:
    """Configure and return the shared ``ai_platform`` logger.

    Writes JSON-formatted lines to ``{log_dir}/app.log`` using UTF-8 so that
    non-ASCII messages are not mangled. Handlers are added only once.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')

    logger = logging.getLogger("ai_platform")
    logger.setLevel(log_level)

    if not logger.handlers:
        fh = logging.FileHandler(f"{log_dir}/app.log", encoding="utf-8")
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def generate_id(prefix: str = "gen") -> str:
    """Return a short unique id like ``gen-1a2b3c4d`` (UUID4, 8 hex chars)."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def hash_text(text: str) -> str:
    """Return the SHA-256 hex digest of ``text`` (stable across processes)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def simple_embedding(text: str, dim: int = EMBEDDING_DIM) -> List[float]:
    """Build an L2-normalized bag-of-words embedding via signed feature hashing.

    Each distinct word is hashed deterministically (SHA-256) into one of ``dim``
    buckets with a +/-1 sign. This makes cosine similarity reflect real word
    overlap: unrelated words land in different buckets (low similarity), while
    prompts that share most of their words score high. Word order is ignored.
    """
    vec = [0.0] * dim
    for word in text.lower().split():
        digest = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
        bucket = digest % dim
        sign = 1.0 if (digest // dim) % 2 == 0 else -1.0
        vec[bucket] += sign

    norm = sum(v * v for v in vec) ** 0.5
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Return the cosine similarity of two equal-length vectors (0.0 on mismatch)."""
    if len(embedding1) != len(embedding2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    mag1 = sum(a**2 for a in embedding1) ** 0.5
    mag2 = sum(b**2 for b in embedding2) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return 0.0

    return dot_product / (mag1 * mag2)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Return an ISO-8601 UTC timestamp string with a trailing ``Z``."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"
