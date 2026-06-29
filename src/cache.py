import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from src.config import settings
from src.utils import hash_text, simple_embedding, cosine_similarity

logger = logging.getLogger(__name__)


class Cache:
    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir or settings.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = 24
        self.similarity_threshold = settings.semantic_similarity_threshold

    def _get_cache_file(self, prompt_hash: str) -> Path:
        return self.cache_dir / f"{prompt_hash}.json"

    def _is_expired(self, timestamp_str: str) -> bool:
        try:
            cache_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            expiry = cache_time + timedelta(hours=self.ttl_hours)
            return datetime.utcnow() > expiry.replace(tzinfo=None)
        except:
            return True

    async def get(self, prompt: str) -> Optional[Dict[str, Any]]:
        prompt_hash = hash_text(prompt)
        cache_file = self._get_cache_file(prompt_hash)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            if self._is_expired(cache_data.get("timestamp", "")):
                cache_file.unlink()
                return None

            prompt_embedding = simple_embedding(prompt)
            cached_embedding = cache_data.get("embedding", [])

            similarity = cosine_similarity(prompt_embedding, cached_embedding)

            if similarity >= self.similarity_threshold:
                logger.info(f"Cache hit with {similarity:.2f} similarity")
                return {
                    "response": cache_data["response"],
                    "tokens_input": cache_data["tokens_input"],
                    "tokens_output": cache_data["tokens_output"],
                    "cached": True
                }

            return None

        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    async def set(self, prompt: str, response: str, tokens_input: int, tokens_output: int):
        prompt_hash = hash_text(prompt)
        cache_file = self._get_cache_file(prompt_hash)

        try:
            cache_data = {
                "prompt": prompt,
                "response": response,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "embedding": simple_embedding(prompt),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Cached response for prompt hash {prompt_hash}")

        except Exception as e:
            logger.error(f"Cache write error: {e}")

    async def clear(self):
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        cache_files = list(self.cache_dir.glob("*.json"))
        return {
            "total_entries": len(cache_files),
            "cache_dir": str(self.cache_dir),
            "ttl_hours": self.ttl_hours
        }
