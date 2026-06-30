"""Load and validate Sr-level exercises from JSON."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Level(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


class Exercise:
    """Represents a single training exercise."""

    def __init__(self, data: dict):
        self.id: str = data["id"]
        self.level: Level = Level(data["level"])
        self.category: str = data["category"]
        self.title: str = data["title"]
        self.description: str = data["description"]
        self.expected_patterns: List[str] = data.get("expected_patterns", [])
        self.auto_eval_regex: List[str] = data.get("auto_eval_regex", [])
        self.manual_eval_required: bool = data.get("manual_eval_required", False)

    def __repr__(self):
        return f"Exercise(id={self.id}, level={self.level.value}, title={self.title})"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "level": self.level.value,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "expected_patterns": self.expected_patterns,
            "auto_eval_regex": self.auto_eval_regex,
            "manual_eval_required": self.manual_eval_required,
        }


class ExerciseLoader:
    """Load and manage exercises."""

    def __init__(self, exercises_file: Path):
        self.exercises_file = Path(exercises_file)
        self.exercises: Dict[str, Exercise] = {}
        self.metadata: Dict[str, any] = {}

    def load(self) -> Dict[str, Exercise]:
        """Load exercises from JSON file."""
        if not self.exercises_file.exists():
            raise FileNotFoundError(f"Exercises file not found: {self.exercises_file}")

        try:
            with open(self.exercises_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.metadata = data.get("metadata", {})
            exercises_list = data.get("exercises", [])

            if not exercises_list:
                raise ValueError("No exercises found in JSON")

            for ex_data in exercises_list:
                exercise = Exercise(ex_data)
                self._validate_exercise(exercise)
                self.exercises[exercise.id] = exercise

            logger.info(f"[OK] Loaded {len(self.exercises)} exercises from {self.exercises_file.name}")
            logger.info(f"  Distribution: {self._count_by_level()}")
            return self.exercises

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.exercises_file}: {e}")

    @staticmethod
    def _validate_exercise(exercise: Exercise) -> None:
        """Validate exercise structure."""
        if not exercise.id:
            raise ValueError("Exercise must have 'id'")
        if not exercise.title:
            raise ValueError(f"Exercise {exercise.id} must have 'title'")
        if not exercise.description:
            raise ValueError(f"Exercise {exercise.id} must have 'description'")

    def _count_by_level(self) -> Dict[str, int]:
        """Count exercises by level."""
        counts = {level.value: 0 for level in Level}
        for exercise in self.exercises.values():
            counts[exercise.level.value] += 1
        return counts

    def get_exercises(self, level: Optional[Level] = None) -> List[Exercise]:
        """Get exercises, optionally filtered by level."""
        if not self.exercises:
            self.load()

        if level:
            return [ex for ex in self.exercises.values() if ex.level == level]

        return list(self.exercises.values())

    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """Get a specific exercise by ID."""
        if not self.exercises:
            self.load()
        return self.exercises.get(exercise_id)

    def get_random_exercise(self, level: Optional[Level] = None) -> Optional[Exercise]:
        """Get a random exercise."""
        import random

        exercises = self.get_exercises(level)
        return random.choice(exercises) if exercises else None

    def get_by_category(self, category: str) -> List[Exercise]:
        """Get exercises by category."""
        if not self.exercises:
            self.load()
        return [ex for ex in self.exercises.values() if ex.category == category]

    def get_categories(self) -> set:
        """Get all categories."""
        if not self.exercises:
            self.load()
        return {ex.category for ex in self.exercises.values()}


# Singleton instance
_exercise_loader: Optional[ExerciseLoader] = None


def get_exercise_loader(exercises_file: Path = None) -> ExerciseLoader:
    """Get or create exercise loader singleton."""
    global _exercise_loader

    if _exercise_loader is None:
        if exercises_file is None:
            exercises_file = Path(__file__).parent.parent.parent / "data" / "training_corpus" / "exercises_v1.json"

        _exercise_loader = ExerciseLoader(exercises_file)

    return _exercise_loader


def load_exercises(exercises_file: Path = None) -> Dict[str, Exercise]:
    """Load exercises directly."""
    loader = get_exercise_loader(exercises_file)
    return loader.load()
