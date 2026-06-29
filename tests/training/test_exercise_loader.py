"""Tests for exercise loader."""

import pytest
import json
from pathlib import Path
from src.training.exercise_loader import (
    ExerciseLoader,
    Exercise,
    Level,
    load_exercises,
)


@pytest.fixture
def exercises_data():
    """Sample exercises data."""
    return {
        "metadata": {
            "version": "1.0",
            "total_exercises": 2,
        },
        "exercises": [
            {
                "id": "arch_junior_001",
                "level": "junior",
                "category": "architecture",
                "title": "Explain MVC",
                "description": "Explain the MVC pattern.",
                "expected_patterns": ["model", "view", "controller"],
                "auto_eval_regex": ["mvc|MVC"],
                "manual_eval_required": False,
            },
            {
                "id": "arch_senior_025",
                "level": "senior",
                "category": "architecture",
                "title": "Scale to 1M users",
                "description": "Design for 1M concurrent users.",
                "expected_patterns": ["load balance", "cache", "sharding"],
                "auto_eval_regex": ["load.*balance", "cache", "shard"],
                "manual_eval_required": True,
            },
        ],
    }


def test_exercise_initialization():
    """Test Exercise initialization."""
    data = {
        "id": "test_001",
        "level": "junior",
        "category": "architecture",
        "title": "Test Exercise",
        "description": "Test description",
        "expected_patterns": ["pattern1"],
        "auto_eval_regex": ["regex1"],
        "manual_eval_required": False,
    }

    exercise = Exercise(data)

    assert exercise.id == "test_001"
    assert exercise.level == Level.JUNIOR
    assert exercise.category == "architecture"
    assert len(exercise.expected_patterns) == 1


def test_exercise_loader_load(tmp_path, exercises_data):
    """Test loading exercises from JSON."""
    exercises_file = tmp_path / "exercises.json"
    exercises_file.write_text(json.dumps(exercises_data), encoding="utf-8")

    loader = ExerciseLoader(exercises_file)
    exercises = loader.load()

    assert len(exercises) == 2
    assert "arch_junior_001" in exercises
    assert "arch_senior_025" in exercises


def test_exercise_loader_missing_file():
    """Test handling of missing exercises file."""
    loader = ExerciseLoader(Path("/nonexistent/file.json"))

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_exercise_loader_invalid_json(tmp_path):
    """Test handling of invalid JSON."""
    exercises_file = tmp_path / "exercises.json"
    exercises_file.write_text("invalid json {", encoding="utf-8")

    loader = ExerciseLoader(exercises_file)

    with pytest.raises(ValueError, match="Invalid JSON"):
        loader.load()


def test_exercise_loader_no_exercises(tmp_path):
    """Test handling of no exercises."""
    exercises_data = {"metadata": {}, "exercises": []}
    exercises_file = tmp_path / "exercises.json"
    exercises_file.write_text(json.dumps(exercises_data), encoding="utf-8")

    loader = ExerciseLoader(exercises_file)

    with pytest.raises(ValueError, match="No exercises"):
        loader.load()


def test_get_exercises_by_level(tmp_path, exercises_data):
    """Test getting exercises filtered by level."""
    exercises_file = tmp_path / "exercises.json"
    exercises_file.write_text(json.dumps(exercises_data), encoding="utf-8")

    loader = ExerciseLoader(exercises_file)
    loader.load()

    junior = loader.get_exercises(Level.JUNIOR)
    assert len(junior) == 1
    assert junior[0].id == "arch_junior_001"

    senior = loader.get_exercises(Level.SENIOR)
    assert len(senior) == 1


def test_get_exercise_by_id(tmp_path, exercises_data):
    """Test getting specific exercise."""
    exercises_file = tmp_path / "exercises.json"
    exercises_file.write_text(json.dumps(exercises_data), encoding="utf-8")

    loader = ExerciseLoader(exercises_file)
    loader.load()

    exercise = loader.get_exercise("arch_junior_001")
    assert exercise.title == "Explain MVC"
    assert exercise.level == Level.JUNIOR


def test_get_by_category(tmp_path, exercises_data):
    """Test getting exercises by category."""
    exercises_file = tmp_path / "exercises.json"
    exercises_file.write_text(json.dumps(exercises_data), encoding="utf-8")

    loader = ExerciseLoader(exercises_file)
    loader.load()

    arch_exercises = loader.get_by_category("architecture")
    assert len(arch_exercises) == 2


def test_get_categories(tmp_path, exercises_data):
    """Test getting all categories."""
    exercises_file = tmp_path / "exercises.json"
    exercises_file.write_text(json.dumps(exercises_data), encoding="utf-8")

    loader = ExerciseLoader(exercises_file)
    loader.load()

    categories = loader.get_categories()
    assert "architecture" in categories


def test_random_exercise(tmp_path, exercises_data):
    """Test getting random exercise."""
    exercises_file = tmp_path / "exercises.json"
    exercises_file.write_text(json.dumps(exercises_data), encoding="utf-8")

    loader = ExerciseLoader(exercises_file)
    loader.load()

    random_ex = loader.get_random_exercise(Level.JUNIOR)
    assert random_ex is not None
    assert random_ex.level == Level.JUNIOR


def test_exercise_to_dict():
    """Test Exercise to_dict conversion."""
    data = {
        "id": "test_001",
        "level": "mid",
        "category": "patterns",
        "title": "Test",
        "description": "Test description",
        "expected_patterns": ["p1", "p2"],
        "auto_eval_regex": ["r1"],
        "manual_eval_required": False,
    }

    exercise = Exercise(data)
    converted = exercise.to_dict()

    assert converted["id"] == "test_001"
    assert converted["level"] == "mid"
    assert len(converted["expected_patterns"]) == 2
