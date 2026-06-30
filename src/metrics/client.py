"""Metrics collector for real-time training dashboard updates."""

import json
import logging
from pathlib import Path
from datetime import datetime
from threading import Lock
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and persists training metrics for dashboard consumption."""

    def __init__(self, metrics_file: str = None):
        """Initialize metrics collector.

        Args:
            metrics_file: Path to metrics JSON file. Defaults to data/training_logs/live_metrics.json
        """
        if metrics_file is None:
            metrics_file = Path(__file__).parent.parent.parent / "data" / "training_logs" / "live_metrics.json"

        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self.exercises: List[Dict[str, Any]] = []
        self.session_start = datetime.now()
        self.stats = {
            "total_exercises": 0,
            "successful": 0,
            "failed": 0,
            "avg_score": 0.0,
            "success_rate": 0.0,
            "avg_quality_score": 0.0,
            "current_hour": 0.0,
            "failed_exercises": [],
            "last_updated": None,
            "categories": {}
        }
        self._load_existing()

    def _load_existing(self):
        """Load existing metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.exercises = data.get('exercises', [])
                    self.stats = data.get('stats', self.stats)
            except Exception as e:
                logger.warning(f"Could not load existing metrics: {e}")

    def record_exercise(self, exercise_id: str, quality_score: float, success: bool,
                       category: str = "general", details: Dict[str, Any] = None):
        """Record a single exercise result.

        Args:
            exercise_id: ID of the exercise
            quality_score: Quality score (0-10)
            success: Whether exercise was successful
            category: Exercise category
            details: Additional details (patterns, regex matches, etc.)
        """
        with self._lock:
            exercise_record = {
                "exercise_id": exercise_id,
                "quality_score": quality_score,
                "success": success,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "details": details or {}
            }

            self.exercises.append(exercise_record)

            # Update stats
            self.stats["total_exercises"] += 1
            if success:
                self.stats["successful"] += 1
            else:
                self.stats["failed"] += 1

            # Update category stats
            if category not in self.stats["categories"]:
                self.stats["categories"][category] = {
                    "count": 0,
                    "successful": 0,
                    "avg_score": 0.0
                }

            cat_stats = self.stats["categories"][category]
            cat_stats["count"] += 1
            if success:
                cat_stats["successful"] += 1

            # Recalculate averages
            if self.stats["total_exercises"] > 0:
                total_score = sum(e["quality_score"] for e in self.exercises)
                self.stats["avg_score"] = total_score / self.stats["total_exercises"]

            if cat_stats["count"] > 0:
                cat_total_score = sum(
                    e["quality_score"] for e in self.exercises
                    if e["category"] == category
                )
                cat_stats["avg_score"] = cat_total_score / cat_stats["count"]

            self.stats["last_updated"] = datetime.now().isoformat()

            # Persist to file
            self._save()

    def _save(self):
        """Save metrics to file."""
        try:
            # Calculate metrics for dashboard
            stats_for_dashboard = self.stats.copy()

            # Calculate current hour
            elapsed = (datetime.now() - self.session_start).total_seconds() / 3600
            stats_for_dashboard["current_hour"] = elapsed

            # Calculate success rate and avg quality
            if self.stats["total_exercises"] > 0:
                stats_for_dashboard["success_rate"] = (
                    self.stats["successful"] / self.stats["total_exercises"] * 100
                )
                stats_for_dashboard["avg_quality_score"] = self.stats["avg_score"]
            else:
                stats_for_dashboard["success_rate"] = 0.0
                stats_for_dashboard["avg_quality_score"] = 0.0

            # Add session start
            stats_for_dashboard["session_start"] = self.session_start.isoformat()

            # Keep failed_exercises list updated
            stats_for_dashboard["failed_exercises"] = [
                e for e in self.exercises if not e["success"]
            ]

            data = {
                "exercises": self.exercises[-1000:],
                "stats": stats_for_dashboard
            }
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        return self.stats.copy()

    def get_recent_exercises(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent exercise results."""
        return self.exercises[-limit:]
