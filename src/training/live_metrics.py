"""
Live metrics collector - writes streaming metrics during training
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict


class LiveMetricsCollector:
    """Collects and updates metrics in real-time during training"""

    def __init__(self, output_file: str = "data/training_logs/live_metrics.json"):
        self.output_file = Path(output_file)
        self.start_time = datetime.now()
        self.metrics = {
            "session_start": self.start_time.isoformat(),
            "total_exercises": 0,
            "successful_exercises": 0,
            "failed_exercises": 0,
            "success_rate": 0.0,
            "avg_quality_score": 0.0,
            "current_hour": 0.0,
            "exercises_by_type": {},
            "quality_by_type": {},
            "latest_exercises": [],
            "failures": [],
            "last_updated": datetime.now().isoformat()
        }
        self._ensure_output_dir()
        self._save_metrics()

    def _ensure_output_dir(self):
        """Ensure output directory exists"""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def _save_metrics(self):
        """Save current metrics to JSON"""
        self.metrics["last_updated"] = datetime.now().isoformat()
        with open(self.output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

    def record_exercise(self,
                       exercise_id: str,
                       quality_score: float,
                       success: bool,
                       patterns_found: int,
                       patterns_total: int,
                       regex_matched: int,
                       regex_total: int,
                       response_length: int):
        """Record a single exercise result"""

        # Update totals
        self.metrics["total_exercises"] += 1
        if success:
            self.metrics["successful_exercises"] += 1
        else:
            self.metrics["failed_exercises"] += 1

        # Update rates
        self.metrics["success_rate"] = (
            100 * self.metrics["successful_exercises"] / self.metrics["total_exercises"]
        )

        # Update quality average
        if self.metrics["total_exercises"] == 1:
            self.metrics["avg_quality_score"] = quality_score
        else:
            total_quality = self.metrics["avg_quality_score"] * (self.metrics["total_exercises"] - 1)
            self.metrics["avg_quality_score"] = (total_quality + quality_score) / self.metrics["total_exercises"]

        # Update elapsed time
        elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
        self.metrics["current_hour"] = round(elapsed, 2)

        # Track by type
        ex_type = exercise_id.rsplit('_', 1)[0]

        if ex_type not in self.metrics["exercises_by_type"]:
            self.metrics["exercises_by_type"][ex_type] = {
                "count": 0,
                "success": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_quality": 0.0
            }

        type_stats = self.metrics["exercises_by_type"][ex_type]
        type_stats["count"] += 1

        if success:
            type_stats["success"] += 1
        else:
            type_stats["failed"] += 1

        type_stats["success_rate"] = 100 * type_stats["success"] / type_stats["count"]

        # Update quality by type
        if ex_type not in self.metrics["quality_by_type"]:
            self.metrics["quality_by_type"][ex_type] = []

        self.metrics["quality_by_type"][ex_type].append(quality_score)

        # Calculate average quality for type
        avg_quality = sum(self.metrics["quality_by_type"][ex_type]) / len(self.metrics["quality_by_type"][ex_type])
        type_stats["avg_quality"] = round(avg_quality, 2)

        # Track latest exercises (last 20)
        exercise_record = {
            "exercise_id": exercise_id,
            "quality_score": quality_score,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "patterns": f"{patterns_found}/{patterns_total}",
            "regex": f"{regex_matched}/{regex_total}"
        }

        self.metrics["latest_exercises"].append(exercise_record)
        if len(self.metrics["latest_exercises"]) > 20:
            self.metrics["latest_exercises"] = self.metrics["latest_exercises"][-20:]

        # Track failures
        if not success:
            failure_record = {
                "exercise_id": exercise_id,
                "quality_score": quality_score,
                "timestamp": datetime.now().isoformat(),
                "patterns": f"{patterns_found}/{patterns_total}",
                "regex": f"{regex_matched}/{regex_total}"
            }
            self.metrics["failures"].append(failure_record)

        # Save to disk (every exercise)
        self._save_metrics()

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            "elapsed_hours": self.metrics["current_hour"],
            "total_exercises": self.metrics["total_exercises"],
            "success_rate": round(self.metrics["success_rate"], 2),
            "avg_quality": round(self.metrics["avg_quality_score"], 2),
            "failures": self.metrics["failed_exercises"]
        }
