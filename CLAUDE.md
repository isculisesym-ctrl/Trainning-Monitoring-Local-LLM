# Training Dashboard Monitoring - Development Context

## Project Overview

**Training Dashboard Monitoring** is a real-time monitoring dashboard for local LLM training sessions.

- **Repo**: https://github.com/isculisesym-ctrl/Trainning-Monitoring-Local-LLM
- **Status**: Production Ready
- **Type**: Python library + Web Dashboard
- **Python**: 3.8+ (No external dependencies)

## Folder Structure

```
training-dashboard-monitoring/
├── community/                 # PUBLIC (synced to git)
│   ├── README.md
│   ├── LICENSE (MIT)
│   ├── src/                  # All source code
│   ├── examples/
│   ├── config/
│   ├── requirements.txt
│   └── CONTRIBUTING.md
│
├── src/                       # Development (local only)
├── data/logs/               # Training output (local only, gitignored)
├── tests/                   # Test files
├── .env.local               # Local secrets (gitignored)
└── CLAUDE.md               # This file
```

## Workflow

### Public Code (community/ → GitHub)
- All shareable code goes in `/community/`
- Synced to GitHub: `git push origin main` pushes only `/community`
- No sensitive data, no inhouse code

### Local Development (root → local only)
- Development, testing, debugging in root
- `.env.local` for any local secrets
- Not synced to git
- Full freedom for experimentation

## How to Use

### Start Development
```bash
cd C:\Proyectos\training-dashboard-monitoring

# Create local environment
python -m venv venv
.\venv\Scripts\activate

# Start dashboard
python src/server/app.py

# In another terminal, run training
python examples/training_simulator.py
```

### Push Updates to GitHub
```bash
# Only community/ folder is synced to git
git add community/
git commit -m "Update: ..."
git push origin main
```

## Key Files

### `/community/` - Public
- `src/web/dashboard.html` - Frontend dashboard
- `src/server/app.py` - HTTP server
- `src/metrics/client.py` - Metrics collector
- `examples/training_simulator.py` - Example training script
- `config/training_session.json` - Configuration template
- `README.md` - User documentation
- `LICENSE` - MIT License

### `/src/` - Local Development
- Extended dashboards
- Advanced monitoring
- Custom metrics
- Private utilities

### Data & Logs
- `data/logs/` - Training metrics (generated at runtime)
- `tests/` - Unit and integration tests

## Development Notes

### No External Dependencies
Uses Python stdlib only:
- `http.server` - HTTP server
- `json` - Metrics serialization
- `pathlib` - File handling
- `datetime` - Timestamps

### Key Components

1. **Server** (`src/server/app.py`)
   - Serves dashboard HTML
   - Serves metrics JSON
   - Auto-detects available port
   - CORS enabled

2. **Metrics Collector** (`src/metrics/client.py`)
   - Records training exercises
   - Aggregates statistics
   - Persists to JSON
   - Real-time updates

3. **Dashboard** (`src/web/dashboard.html`)
   - Real-time metrics display
   - Chart.js graphs
   - Auto-refresh every 2 seconds
   - Table of latest exercises

4. **Configuration** (`config/training_session.json`)
   - Session metadata
   - Target metrics
   - Training categories
   - Auto-reload on save

## Integration

### For Your Training Script
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

### Access Metrics
```python
# Get current metrics
metrics = collector.get_metrics()

# Get summary
summary = collector.get_summary()
# Returns: elapsed_hours, total_exercises, success_rate, avg_quality, failures
```

## Testing

### Run Simulator
```bash
python examples/training_simulator.py
```

Generates 100 realistic training exercises with:
- 99% success rate
- Quality scores 7.5-9.8
- 5 training categories
- Real-time dashboard updates

### Unit Tests
```bash
python -m pytest tests/
```

## Contributing

Guidelines in `community/CONTRIBUTING.md`:
- Fork the repository
- Create feature branch
- Submit pull request
- No external dependencies
- Keep stdlib-only approach

## Security Notes

⚠️ **Local Development Only**
- No authentication
- No encryption
- Listens on localhost only
- For production: use behind firewall/VPN

## Next Steps

1. **Development**
   - Extend metrics types
   - Add custom visualizations
   - Improve validation

2. **Community**
   - Share improvements to `community/`
   - Document features in README
   - Keep code examples updated

3. **Integration**
   - Test with real training pipelines
   - Validate metric accuracy
   - Optimize performance

## Resources

- **Main README**: `community/README.md`
- **Examples**: `community/examples/`
- **Configuration**: `config/training_session.json`
- **GitHub**: https://github.com/isculisesym-ctrl/Trainning-Monitoring-Local-LLM

---

**Last Updated**: 2026-06-30  
**Version**: 1.0.0  
**Status**: Production Ready
