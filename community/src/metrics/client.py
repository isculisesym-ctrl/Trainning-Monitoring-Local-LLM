"""Metrics Collector Client for training scripts"""

import json
from datetime import datetime
from pathlib import Path

class MetricsCollector:
    def __init__(self, output_file="data/logs/metrics.json"):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.metrics = {
            "session_start": datetime.now().isoformat(),
            "total_exercises": 0,
            "successful_exercises": 0,
            "failed_exercises": 0,
            "success_rate": 0.0,
            "avg_quality_score": 0.0,
            "exercises_by_category": {},
            "latest_exercises": [],
            "failures": [],
            "last_updated": datetime.now().isoformat()
        }
        self._load_or_create()
    
    def record_exercise(self, exercise_id, quality_score, success, category="general", details=None):
        self.metrics["total_exercises"] += 1
        if success:
            self.metrics["successful_exercises"] += 1
        else:
            self.metrics["failed_exercises"] += 1
        
        self.metrics["success_rate"] = 100 * self.metrics["successful_exercises"] / self.metrics["total_exercises"]
        
        total_quality = self.metrics["avg_quality_score"] * (self.metrics["total_exercises"] - 1)
        self.metrics["avg_quality_score"] = (total_quality + quality_score) / self.metrics["total_exercises"]
        
        if category not in self.metrics["exercises_by_category"]:
            self.metrics["exercises_by_category"][category] = {
                "count": 0, "success": 0, "failed": 0, "success_rate": 0.0, "avg_quality": 0.0
            }
        
        cat = self.metrics["exercises_by_category"][category]
        cat["count"] += 1
        if success:
            cat["success"] += 1
        else:
            cat["failed"] += 1
        cat["success_rate"] = 100 * cat["success"] / cat["count"]
        
        ex = {
            "exercise_id": exercise_id,
            "quality_score": round(quality_score, 2),
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "details": details or {}
        }
        
        self.metrics["latest_exercises"].append(ex)
        if len(self.metrics["latest_exercises"]) > 20:
            self.metrics["latest_exercises"] = self.metrics["latest_exercises"][-20:]
        
        if not success:
            self.metrics["failures"].append(ex)
        
        self.metrics["last_updated"] = datetime.now().isoformat()
        self._save()
    
    def _save(self):
        with open(self.output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def _load_or_create(self):
        if self.output_file.exists():
            try:
                with open(self.output_file) as f:
                    self.metrics.update(json.load(f))
            except:
                self._save()
        else:
            self._save()
