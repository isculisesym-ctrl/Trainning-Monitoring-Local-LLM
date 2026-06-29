"""Data types for checkpoint and audit system."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional
import json
from pathlib import Path


@dataclass
class ExerciseResult:
    """Result of a single exercise."""

    exercise_id: str
    quality_score: float  # 0-10
    success: bool
    timestamp: datetime
    patterns_found: int
    patterns_total: int
    regex_matched: int
    regex_total: int
    requires_manual_review: bool
    response_length: int

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SessionMetrics:
    """Metrics for a training session."""

    session_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    total_exercises: int = 0
    successful_exercises: int = 0
    failed_exercises: int = 0
    avg_quality_score: float = 0.0
    exercise_results: List[ExerciseResult] = field(default_factory=list)

    def add_result(self, result: ExerciseResult) -> None:
        """Add an exercise result."""
        self.exercise_results.append(result)
        self.total_exercises += 1

        if result.success:
            self.successful_exercises += 1
        else:
            self.failed_exercises += 1

        # Update average
        if self.exercise_results:
            scores = [r.quality_score for r in self.exercise_results]
            self.avg_quality_score = sum(scores) / len(scores)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_exercises == 0:
            return 0.0
        return self.successful_exercises / self.total_exercises

    def to_dict(self) -> dict:
        data = asdict(self)
        data["started_at"] = self.started_at.isoformat()
        data["ended_at"] = self.ended_at.isoformat() if self.ended_at else None
        data["exercise_results"] = [r.to_dict() for r in self.exercise_results]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "SessionMetrics":
        """Create from dict."""
        metrics = cls(
            session_id=data["session_id"],
            started_at=datetime.fromisoformat(data["started_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            total_exercises=data.get("total_exercises", 0),
            successful_exercises=data.get("successful_exercises", 0),
            failed_exercises=data.get("failed_exercises", 0),
            avg_quality_score=data.get("avg_quality_score", 0.0),
        )
        return metrics


@dataclass
class CheckpointReport:
    """Report generated for a checkpoint."""

    checkpoint_id: str
    session_metrics: SessionMetrics
    timestamp: datetime
    failed_exercises_summary: str = ""
    quality_observations: str = ""

    def to_dict(self) -> dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "session_metrics": self.session_metrics.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "failed_exercises_summary": self.failed_exercises_summary,
            "quality_observations": self.quality_observations,
        }

    def save(self, filepath: Path) -> None:
        """Save checkpoint report to file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


@dataclass
class AuditFeedback:
    """Feedback from Claude audit."""

    checkpoint_id: str
    audit_timestamp: datetime
    improvement_assessment: str
    weak_areas: List[str] = field(default_factory=list)
    strong_areas: List[str] = field(default_factory=list)
    recommended_focus: List[str] = field(default_factory=list)
    prompt_adjustments: str = ""
    overall_verdict: str = ""  # e.g., "improving", "plateau", "regression"

    def to_dict(self) -> dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "audit_timestamp": self.audit_timestamp.isoformat(),
            "improvement_assessment": self.improvement_assessment,
            "weak_areas": self.weak_areas,
            "strong_areas": self.strong_areas,
            "recommended_focus": self.recommended_focus,
            "prompt_adjustments": self.prompt_adjustments,
            "overall_verdict": self.overall_verdict,
        }

    def save(self, filepath: Path) -> None:
        """Save audit feedback to file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
