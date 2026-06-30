#!/usr/bin/env python3
"""Training Simulator - Test the dashboard"""

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.metrics.client import MetricsCollector

def simulate():
    collector = MetricsCollector("data/logs/metrics.json")
    categories = ["architecture", "patterns", "quality", "security", "scalability"]
    
    print("\nTraining Simulator - 100 exercises\n")
    
    for i in range(100):
        category = random.choice(categories)
        success = random.random() > 0.01
        quality = random.gauss(8.8, 0.4) if success else random.uniform(5, 7)
        quality = max(5, min(10, quality))
        
        collector.record_exercise(
            exercise_id=f"{category}_{i:03d}",
            quality_score=quality,
            success=success,
            category=category
        )
        
        summary = collector.metrics
        status = "OK" if success else "FAIL"
        print(f"[{i+1:03d}] {status} {category:12} | Quality: {quality:5.2f} | "
              f"Success: {summary['success_rate']:6.2f}%")
        
        time.sleep(0.05)
    
    print("\nSimulation complete!")

if __name__ == "__main__":
    simulate()
