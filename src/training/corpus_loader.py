"""Load and validate Sr-level corpus from Markdown files."""

import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CorpusLoader:
    """Loads Sr-level corpus from Markdown files."""

    def __init__(self, corpus_dir: Path):
        self.corpus_dir = Path(corpus_dir)
        self.corpus: Dict[str, str] = {}
        self.metadata: Dict[str, any] = {}

    def load(self) -> Dict[str, str]:
        """Load all .md files from corpus directory."""
        if not self.corpus_dir.exists():
            raise FileNotFoundError(f"Corpus directory not found: {self.corpus_dir}")

        md_files = sorted(self.corpus_dir.glob("*.md"))

        if not md_files:
            raise ValueError(f"No .md files found in {self.corpus_dir}")

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                key = md_file.stem  # filename without extension

                # Validate content
                self._validate_markdown(content, md_file.name)

                self.corpus[key] = content
                logger.info(f"[OK] Loaded corpus: {md_file.name} ({len(content)} chars)")
            except Exception as e:
                logger.error(f"[ERROR] Failed to load {md_file.name}: {e}")
                raise

        logger.info(f"[OK] Total corpus loaded: {len(self.corpus)} files, {sum(len(c) for c in self.corpus.values())} chars")
        return self.corpus

    @staticmethod
    def _validate_markdown(content: str, filename: str) -> None:
        """Validate markdown content."""
        if not content or len(content) < 100:
            raise ValueError(f"{filename} is too short (< 100 chars)")

        # Check for basic markdown structure
        if not any(line.startswith("#") for line in content.split("\n")):
            raise ValueError(f"{filename} has no headers (missing # title)")

    def get_corpus(self) -> Dict[str, str]:
        """Return loaded corpus."""
        if not self.corpus:
            self.load()
        return self.corpus

    def get_corpus_content(self, key: Optional[str] = None) -> str:
        """Get corpus content. If key is None, return all concatenated."""
        if not self.corpus:
            self.load()

        if key:
            if key not in self.corpus:
                raise KeyError(f"Corpus key not found: {key}")
            return self.corpus[key]

        # Concatenate all corpus files
        return "\n\n---\n\n".join(self.corpus.values())

    def get_corpus_size_mb(self) -> float:
        """Return total corpus size in MB."""
        return sum(len(c) for c in self.corpus.values()) / (1024 * 1024)

    def get_available_keys(self) -> List[str]:
        """Return list of available corpus keys."""
        if not self.corpus:
            self.load()
        return sorted(self.corpus.keys())


# Singleton instance
_corpus_loader: Optional[CorpusLoader] = None


def get_corpus_loader(corpus_dir: Path = None) -> CorpusLoader:
    """Get or create corpus loader singleton."""
    global _corpus_loader

    if _corpus_loader is None:
        if corpus_dir is None:
            corpus_dir = Path(__file__).parent.parent.parent / "data" / "training_corpus"

        _corpus_loader = CorpusLoader(corpus_dir)

    return _corpus_loader


def load_corpus(corpus_dir: Path = None) -> Dict[str, str]:
    """Load corpus directly."""
    loader = get_corpus_loader(corpus_dir)
    return loader.load()


def get_full_corpus_text(corpus_dir: Path = None) -> str:
    """Get full corpus text concatenated."""
    loader = get_corpus_loader(corpus_dir)
    return loader.get_corpus_content()
