import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from src.config import settings
from src.utils import cosine_similarity, hash_text, simple_embedding

logger = logging.getLogger(__name__)


class Cache:
    """File-based semantic response cache.

    Each entry is a JSON file in ``cache_dir`` keyed by the SHA-256 hash of the
    prompt. Lookups try the exact-hash file first and then fall back to a
    semantic scan, returning the closest non-expired entry whose cosine
    similarity is >= ``semantic_similarity_threshold``.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir or settings.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = 24
        self.similarity_threshold = settings.semantic_similarity_threshold

    def _get_cache_file(self, prompt_hash: str) -> Path:
        return self.cache_dir / f"{prompt_hash}.json"

    def _is_expired(self, timestamp_str: str) -> bool:
        """Return True if the timestamp is older than the TTL or unparseable."""
        try:
            cache_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            expiry = cache_time + timedelta(hours=self.ttl_hours)
            return datetime.utcnow() > expiry.replace(tzinfo=None)
        except (ValueError, AttributeError, TypeError):
            return True

    async def get(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Return a cached entry for ``prompt`` if a similar, non-expired one exists.

        Tries the exact-hash file first, then scans all entries for the closest
        semantic match. Returns the best match whose similarity is >= the
        configured threshold, or ``None``. Expired and corrupt files are removed
        as they are encountered.
        """
        prompt_embedding = simple_embedding(prompt)
        exact_file = self._get_cache_file(hash_text(prompt))

        best_entry: Optional[Dict[str, Any]] = None
        best_similarity = -1.0

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
            except (OSError, ValueError) as e:
                logger.error(f"Cache read error: {e}")
                continue

            if self._is_expired(cache_data.get("timestamp", "")):
                cache_file.unlink(missing_ok=True)
                continue

            similarity = cosine_similarity(prompt_embedding, cache_data.get("embedding", []))
            if cache_file == exact_file:
                similarity = 1.0  # identical prompt always wins

            if similarity > best_similarity:
                best_similarity = similarity
                best_entry = cache_data

        if best_entry is not None and best_similarity >= self.similarity_threshold:
            logger.info(f"Cache hit with {best_similarity:.2f} similarity")
            return {
                "response": best_entry["response"],
                "tokens_input": best_entry["tokens_input"],
                "tokens_output": best_entry["tokens_output"],
                "cached": True,
            }

        return None

    async def set(self, prompt: str, response: str, tokens_input: int, tokens_output: int) -> None:
        """Store a response for ``prompt`` along with its embedding and timestamp."""
        prompt_hash = hash_text(prompt)
        cache_file = self._get_cache_file(prompt_hash)

        try:
            cache_data = {
                "prompt": prompt,
                "response": response,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "embedding": simple_embedding(prompt),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Cached response for prompt hash {prompt_hash}")

        except OSError as e:
            logger.error(f"Cache write error: {e}")

    async def clear(self) -> None:
        """Delete every cached entry."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink(missing_ok=True)
            logger.info("Cache cleared")
        except OSError as e:
            logger.error(f"Cache clear error: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """Return cache statistics: entry count, directory, and TTL."""
        cache_files = list(self.cache_dir.glob("*.json"))
        return {
            "total_entries": len(cache_files),
            "cache_dir": str(self.cache_dir),
            "ttl_hours": self.ttl_hours,
        }
