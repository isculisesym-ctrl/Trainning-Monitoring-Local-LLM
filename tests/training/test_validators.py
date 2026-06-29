"""Tests for validators."""

import pytest
from src.training.validators import (
    CorpusValidator,
    ExerciseValidator,
    ResponseValidator,
)
from src.training.exercise_loader import Exercise


def test_corpus_validator_valid_markdown():
    """Test corpus validation with valid markdown."""
    content = "# Title\n\nSome content here that is long enough."
    valid, issues = CorpusValidator.validate_markdown(content)

    assert valid
    assert len(issues) == 0


def test_corpus_validator_short_content():
    """Test corpus validation fails for short content."""
    content = "Short"
    valid, issues = CorpusValidator.validate_markdown(content)

    assert not valid
    assert "too short" in issues[0].lower()


def test_corpus_validator_no_headers():
    """Test corpus validation fails without headers."""
    content = ("Content line 1. " * 20)
    valid, issues = CorpusValidator.validate_markdown(content)

    assert not valid


def test_corpus_validator_size():
    """Test corpus size validation."""
    content = "# Title\n\nContent." * 100
    valid, msg = CorpusValidator.validate_size(content, min_kb=1)

    assert valid
    assert "Size OK" in msg


def test_exercise_validator_valid_structure():
    """Test exercise validation with valid structure."""
    exercise_data = {
        "id": "test_001",
        "level": "junior",
        "category": "architecture",
        "title": "Test Title",
        "description": "Test description that is long enough.",
        "expected_patterns": ["pattern1"],
        "auto_eval_regex": ["regex1"],
        "manual_eval_required": False,
    }

    exercise = Exercise(exercise_data)
    valid, issues = ExerciseValidator.validate_structure(exercise)

    assert valid
    assert len(issues) == 0


def test_exercise_validator_id_format_valid():
    """Test exercise ID format validation - valid."""
    valid, msg = ExerciseValidator.validate_id_format("arch_junior_001")

    assert valid
    assert "format valid" in msg.lower()


def test_exercise_validator_id_format_invalid():
    """Test exercise ID format validation - invalid."""
    valid, msg = ExerciseValidator.validate_id_format("invalid_id")

    assert not valid
    assert "format invalid" in msg.lower()


def test_response_validator_check_patterns():
    """Test pattern matching in response."""
    response = "This response mentions cache and database optimization."
    patterns = ["cache", "database"]

    found_count, found_patterns = ResponseValidator.check_patterns(response, patterns)

    assert found_count == 2
    assert "cache" in found_patterns


def test_response_validator_check_regex():
    """Test regex matching in response."""
    response = "The latency was 500ms, improved to 50ms."
    regex_patterns = [r"\d+ms"]

    found_count, matched = ResponseValidator.check_regex(response, regex_patterns)

    assert found_count > 0


def test_response_validator_quality_score():
    """Test quality score calculation."""
    exercise_data = {
        "id": "test_001",
        "level": "junior",
        "category": "architecture",
        "title": "Test",
        "description": "Test description.",
        "expected_patterns": ["cache", "database"],
        "auto_eval_regex": [r"cache|database"],
        "manual_eval_required": False,
    }

    exercise = Exercise(exercise_data)

    response = "We need to implement caching and use a database for persistence."
    score, metrics = ResponseValidator.calculate_quality_score(response, exercise)

    assert 0 <= score <= 10
    assert "pattern_score" in metrics
    assert "regex_score" in metrics
    assert "length_score" in metrics


def test_response_validator_auto_evaluate():
    """Test automatic evaluation."""
    exercise_data = {
        "id": "test_001",
        "level": "junior",
        "category": "architecture",
        "title": "Test",
        "description": "Test description.",
        "expected_patterns": ["pattern1", "pattern2"],
        "auto_eval_regex": ["pattern1", "pattern2"],
        "manual_eval_required": False,
    }

    exercise = Exercise(exercise_data)

    # Good response
    response = "Pattern1 and pattern2 are important considerations. " * 3
    result = ResponseValidator.auto_evaluate(response, exercise)

    assert result["success"] == True
    assert result["quality_score"] > 5
    assert result["patterns_found"] > 0


def test_response_validator_auto_evaluate_poor():
    """Test automatic evaluation with poor response."""
    exercise_data = {
        "id": "test_001",
        "level": "senior",
        "category": "architecture",
        "title": "Test",
        "description": "Test description.",
        "expected_patterns": ["scalability", "consistency", "availability"],
        "auto_eval_regex": [r"scalab", r"consist", r"availab"],
        "manual_eval_required": False,
    }

    exercise = Exercise(exercise_data)

    # Poor response (missing most patterns)
    response = "OK"
    result = ResponseValidator.auto_evaluate(response, exercise)

    assert result["quality_score"] < 5
    assert result["patterns_found"] == 0
