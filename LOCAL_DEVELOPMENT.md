# Local Development Guide

## Quick Start

### Windows (PowerShell)
```powershell
cd C:\Proyectos\training-dashboard-monitoring
.\setup-local.ps1
```

### Linux/macOS (Bash)
```bash
cd C:\Proyectos\training-dashboard-monitoring
chmod +x setup-local.sh
./setup-local.sh
```

## Project Structure

```
training-dashboard-monitoring/
├── community/              # ⭐ PUBLIC - synced to GitHub
│   ├── src/               # Python source code
│   ├── examples/          # Example scripts
│   ├── config/            # Configuration templates
│   ├── README.md          # User documentation
│   ├── LICENSE            # MIT License
│   └── CONTRIBUTING.md    # Contribution guidelines
│
├── src/                   # 💻 LOCAL DEVELOPMENT
│   ├── server/           # Extended server features
│   ├── metrics/          # Advanced metrics collection
│   └── config/           # Development configuration
│
├── data/                 # 📊 DATA (local only, gitignored)
│   └── logs/            # Training metrics JSON files
│
├── tests/                # 🧪 TESTS (local only)
│   └── *.py            # Test files
│
├── CLAUDE.md            # ⭐ Claude Code context
├── LOCAL_DEVELOPMENT.md # This file
├── setup-local.sh       # Bash setup script
├── setup-local.ps1      # PowerShell setup script
├── .gitignore          # Git ignore rules
└── .env.local          # Local secrets (gitignored)
```

## Workflow

### 1. Make Code Changes

#### For Public Release (GitHub)
```bash
# Edit files in /community/
cd community/src/
# Make changes...

# Test locally
python src/server/app.py
```

#### For Local Development Only
```bash
# Edit files in /src/ (root)
cd src/
# Make changes...

# Won't be synced to GitHub
```

### 2. Run Tests

```bash
# From root directory
python -m pytest tests/

# Or run specific test
python -m pytest tests/test_metrics.py -v
```

### 3. Test Dashboard

**Terminal 1 - Start server:**
```bash
python src/server/app.py
# Or for public version:
python community/src/server/app.py
```

**Terminal 2 - Run training simulator:**
```bash
python community/examples/training_simulator.py
```

**Browser:**
```
http://localhost:3000 (or shown port)
```

### 4. Commit & Push

#### Commit locally:
```bash
git add .
git commit -m "Your message here"
```

#### Push to GitHub (community only):
```bash
git push origin main
```

## File Sync Rules

| Directory | Local Dev | GitHub | Notes |
|-----------|-----------|--------|-------|
| `/community/` | ✓ | ✓ | Public code - always synced |
| `/src/` | ✓ | ✗ | Local extensions only |
| `/data/logs/` | ✓ | ✗ | Training output (gitignored) |
| `/tests/` | ✓ | ✗ | Local tests |
| `.env.local` | ✓ | ✗ | Secrets (gitignored) |
| `.git/` | ✓ | - | Git repo |

## Development Environment

### Python Version
- **Minimum**: Python 3.8
- **Recommended**: Python 3.10+
- **Check**: `python --version`

### Dependencies
- **Zero external dependencies!**
- Only Python stdlib

### Virtual Environment
```bash
# Create
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Linux/macOS)
source venv/bin/activate

# Deactivate (all platforms)
deactivate
```

## Configuration

### Local Settings (`.env.local`)
```bash
DEBUG=true
LOG_LEVEL=DEBUG
DASHBOARD_PORT=3000
```

### Training Config (`config/training_session.json`)
```json
{
  "session_name": "My Training",
  "description": "Testing new metrics",
  "model_name": "neural-chat",
  "training_categories": ["architecture", "patterns"],
  "target_success_rate": 99.6,
  "target_quality_score": 8.85
}
```

Edit anytime - dashboard auto-reloads!

## Common Tasks

### Start Fresh Development
```bash
# Clear logs
rm data/logs/*.json

# Restart server
python src/server/app.py

# Restart training
python community/examples/training_simulator.py
```

### Test Public Version
```bash
# Use community/ directly
python community/src/server/app.py
python community/examples/training_simulator.py
```

### Debug Metrics
```python
# From Python REPL
from src.metrics.client import MetricsCollector

collector = MetricsCollector()
metrics = collector.get_metrics()
print(f"Success rate: {metrics['success_rate']:.2f}%")
print(f"Quality: {metrics['avg_quality_score']:.2f}/10")
```

### Check Git Status
```bash
git status
git log --oneline -10
git diff HEAD
```

### Push Changes to GitHub
```bash
# Only community/ will be tracked
git add community/
git commit -m "Update: [description]"
git push origin main
```

## Troubleshooting

### Port Already in Use
```bash
# Server will auto-detect next available port (5000, 5001, 8001, etc.)
# Or specify manually in .env.local:
DASHBOARD_PORT=8080
```

### Virtual Environment Issues
```bash
# Recreate venv
rm -rf venv
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/macOS
```

### Metrics Not Updating
```bash
# Check if metrics file exists
ls data/logs/metrics.json

# Force refresh in browser
Ctrl+F5 (or Cmd+Shift+R)
```

### Git Issues
```bash
# Check remote
git remote -v

# Verify tracking
git branch -vv

# Pull latest from GitHub
git fetch origin
git pull origin main
```

## Git Workflow

### Daily Development

1. **Sync with GitHub:**
   ```bash
   git fetch origin
   git pull origin main
   ```

2. **Create feature branch (optional):**
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make changes:**
   - Edit files in `/community/` for public
   - Edit files in `/src/` for local-only

4. **Test locally:**
   ```bash
   python src/server/app.py
   python community/examples/training_simulator.py
   ```

5. **Commit:**
   ```bash
   git add community/  # or git add . for all
   git commit -m "Your message"
   ```

6. **Push:**
   ```bash
   git push origin main
   ```

## GitHub Sync

### What Gets Synced
- `/community/` - Always
- Main documentation, LICENSE, config templates

### What Stays Local
- `/src/` - Your extensions
- `/data/logs/` - Training outputs
- `/tests/` - Test files
- `.env.local` - Secrets

## Best Practices

1. **Always test before pushing**
   ```bash
   python src/server/app.py
   python community/examples/training_simulator.py
   ```

2. **Use meaningful commit messages**
   ```bash
   # Good
   git commit -m "Feature: Add custom metrics collection"
   git commit -m "Fix: Dashboard graph rendering issue"
   
   # Bad
   git commit -m "fix stuff"
   git commit -m "updates"
   ```

3. **Keep community/ public-ready**
   - No debugging code
   - No sensitive data
   - Works out-of-the-box

4. **Document changes**
   - Update README if behavior changes
   - Add examples for new features
   - Keep CONTRIBUTING.md current

5. **Regular commits**
   - Don't wait to commit
   - Small, focused commits are better
   - Use branches for major features

## Resources

- **CLAUDE.md** - Claude Code context
- **community/README.md** - User documentation
- **community/CONTRIBUTING.md** - Contribution guidelines
- **setup-local.sh/ps1** - Environment setup
- **GitHub**: https://github.com/isculisesym-ctrl/Trainning-Monitoring-Local-LLM

---

**Happy coding!** 🚀
