import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List
import hashlib


def setup_logging(log_level: str = "INFO", log_dir: str = "data/logs") -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    )

    logger = logging.getLogger("ai_platform")
    logger.setLevel(log_level)

    if not logger.handlers:
        fh = logging.FileHandler(f"{log_dir}/app.log")
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def generate_id(prefix: str = "gen") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def simple_embedding(text: str) -> List[float]:
    words = text.lower().split()
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:128]
    embedding = [freq for _, freq in sorted_words]

    while len(embedding) < 128:
        embedding.append(0.0)

    max_val = max(embedding) if max(embedding) > 0 else 1
    return [x / max_val for x in embedding]


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    if len(embedding1) != len(embedding2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    mag1 = sum(a ** 2 for a in embedding1) ** 0.5
    mag2 = sum(b ** 2 for b in embedding2) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return 0.0

    return dot_product / (mag1 * mag2)


def format_timestamp(dt: datetime = None) -> str:
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"
