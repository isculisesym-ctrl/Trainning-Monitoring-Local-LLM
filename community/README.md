# Training Dashboard Monitoring

**Real-time monitoring dashboard for local LLM training sessions**

Monitor your local model training with live metrics, real-time graphs, and failure detection. Built to work with any local LLM training pipeline.

## Quick Start

```bash
git clone https://github.com/isculisesym-ctrl/Trainning-Monitoring-Local-LLM.git
cd training-dashboard-monitoring
python src/server/app.py
```

Open your browser at: **http://localhost:3000**

## Features

✅ Real-time metrics tracking  
✅ Interactive analytics graphs  
✅ Failure detection & monitoring  
✅ Multi-training support  
✅ Framework agnostic design  
✅ No external dependencies  

## Usage

### Configure Training Session

Edit `config/training_session.json`:

```json
{
  "session_name": "MyModel-Training",
  "description": "Fine-tuning my local LLM",
  "model_name": "neural-chat",
  "training_categories": ["architecture", "patterns", "quality"],
  "target_success_rate": 99.6,
  "target_quality_score": 8.85
}
```

### Integrate with Your Training Script

```python
from src.metrics.client import MetricsCollector

collector = MetricsCollector()

for exercise in training_data:
    result = model.train(exercise)
    collector.record_exercise(
        exercise_id=exercise['id'],
        quality_score=result['quality'],
        success=result['success'],
        category=exercise['type']
    )
```

### Test with Simulator

```bash
python examples/training_simulator.py
```

## Documentation

- [README.md](README.md) - Full documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [examples/](examples/) - Example integrations

## Architecture

```
training-dashboard-monitoring/
├── src/
│   ├── web/              # Frontend dashboard
│   ├── server/           # HTTP server
│   ├── metrics/          # Metrics collection
│   └── config/           # Configuration
├── config/               # User config
├── data/                 # Training logs
├── examples/             # Example scripts
└── tests/                # Unit tests
```

## Requirements

- Python 3.8+
- Web browser
- No external dependencies!

## License

MIT - See [LICENSE](LICENSE)

---

**Status**: ✅ Production Ready  
**Community**: Growing - Star ⭐ if helpful!
