"""Tests for corpus loader."""

import pytest
from pathlib import Path
from src.training.corpus_loader import CorpusLoader, load_corpus, get_corpus_loader


def test_corpus_loader_initialization(tmp_path):
    """Test corpus loader initialization."""
    loader = CorpusLoader(tmp_path)
    assert loader.corpus_dir == tmp_path
    assert loader.corpus == {}


def test_corpus_load_success(tmp_path):
    """Test successful corpus loading."""
    # Create test corpus file
    corpus_file = tmp_path / "test_patterns.md"
    corpus_file.write_text("# Test Patterns\n\nContent here.", encoding="utf-8")

    loader = CorpusLoader(tmp_path)
    corpus = loader.load()

    assert "test_patterns" in corpus
    assert "# Test Patterns" in corpus["test_patterns"]


def test_corpus_load_missing_directory():
    """Test handling of missing corpus directory."""
    loader = CorpusLoader(Path("/nonexistent/path"))

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_corpus_load_no_files(tmp_path):
    """Test handling of directory with no MD files."""
    loader = CorpusLoader(tmp_path)

    with pytest.raises(ValueError, match="No .md files"):
        loader.load()


def test_corpus_validate_markdown_short_content(tmp_path):
    """Test validation fails for short content."""
    corpus_file = tmp_path / "short.md"
    corpus_file.write_text("Short", encoding="utf-8")

    loader = CorpusLoader(tmp_path)

    with pytest.raises(ValueError, match="too short"):
        loader.load()


def test_corpus_validate_markdown_no_headers(tmp_path):
    """Test validation fails for content without headers."""
    corpus_file = tmp_path / "no_headers.md"
    corpus_file.write_text("Some content here" * 10, encoding="utf-8")

    loader = CorpusLoader(tmp_path)

    with pytest.raises(ValueError, match="No headers"):
        loader.load()


def test_corpus_get_content(tmp_path):
    """Test getting corpus content."""
    corpus_file = tmp_path / "test.md"
    corpus_file.write_text("# Test\n\nContent.", encoding="utf-8")

    loader = CorpusLoader(tmp_path)
    loader.load()

    content = loader.get_corpus_content("test")
    assert "# Test" in content


def test_corpus_get_all_content(tmp_path):
    """Test getting all corpus content concatenated."""
    for i in range(2):
        corpus_file = tmp_path / f"test_{i}.md"
        corpus_file.write_text(f"# Test {i}\n\nContent {i}.", encoding="utf-8")

    loader = CorpusLoader(tmp_path)
    loader.load()

    all_content = loader.get_corpus_content()
    assert "# Test 0" in all_content
    assert "# Test 1" in all_content


def test_corpus_get_size_mb(tmp_path):
    """Test corpus size calculation."""
    corpus_file = tmp_path / "test.md"
    corpus_file.write_text("# Test\n\nContent." * 100, encoding="utf-8")

    loader = CorpusLoader(tmp_path)
    loader.load()

    size_mb = loader.get_corpus_size_mb()
    assert size_mb > 0
    assert size_mb < 1  # Should be less than 1 MB


def test_get_corpus_loader_singleton():
    """Test corpus loader singleton."""
    loader1 = get_corpus_loader(Path("/tmp"))
    loader2 = get_corpus_loader(Path("/tmp"))

    # Note: Will fail if /tmp doesn't have corpus, but tests the singleton pattern
    assert loader1 is loader2


def test_corpus_loader_available_keys(tmp_path):
    """Test getting available corpus keys."""
    for i in range(3):
        corpus_file = tmp_path / f"pattern_{i}.md"
        corpus_file.write_text(f"# Pattern {i}\n\nContent.", encoding="utf-8")

    loader = CorpusLoader(tmp_path)
    loader.load()

    keys = loader.get_available_keys()
    assert len(keys) == 3
    assert "pattern_0" in keys
