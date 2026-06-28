# Project Folder Structure
**AI-Platform Directory Organization**

---

## Complete Directory Tree

```
C:\Proyectos\AI-Platform\
│
├── README.md                      # Project overview & quick start
├── PROJECT.md                     # Original project spec
├── ARCHITECTURE.md                # System design & components
├── INSTALLATION.md                # Step-by-step setup guide
├── ROADMAP.md                     # 7-phase implementation plan
├── API_SPEC.md                    # REST API specification
├── DEPLOYMENT_CHECKLIST.md        # Weekly progress tracking
├── FOLDER_STRUCTURE.md            # This file
│
├── requirements.txt               # Python dependencies (pip)
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
│
├── src/                           # Main application code
│   ├── __init__.py               # Package initialization
│   ├── gateway.py                # FastAPI application (main)
│   ├── models.py                 # Pydantic request/response schemas
│   ├── cache.py                  # Semantic caching logic
│   ├── ollama_client.py          # Ollama API integration
│   ├── validators.py             # Input validation & sanitization
│   ├── config.py                 # Configuration management
│   ├── security.py               # Security & auth logic (Phase 4)
│   ├── metrics.py                # Prometheus metrics (Phase 2)
│   └── utils.py                  # Helper functions
│
├── data/                          # Runtime data & storage
│   ├── cache/                    # Semantic cache (file-based)
│   │   └── *.json                # Cached responses (auto-generated)
│   ├── logs/                     # Application logs
│   │   └── ai_gateway.log        # Daily rotating log file
│   └── templates/                # Prompt templates (Phase 3)
│       ├── crud.json             # CRUD operation template
│       ├── sql.json              # SQL query template
│       ├── documentation.json    # Documentation template
│       ├── testing.json          # Unit test template
│       └── refactoring.json      # Code refactoring template
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_gateway.py           # Gateway tests (Phase 2)
│   ├── test_cache.py             # Cache tests
│   ├── test_validators.py        # Validation tests
│   ├── test_security.py          # Security tests (Phase 4)
│   ├── test_api.py               # API integration tests
│   └── conftest.py               # Pytest fixtures & config
│
├── docs/                          # Documentation (Phase 7)
│   ├── API_EXAMPLES.md           # API usage examples
│   ├── TROUBLESHOOTING.md        # Common issues & solutions
│   ├── UPGRADE_GUIDE.md          # GPU upgrade instructions
│   ├── PERFORMANCE_TUNING.md     # Performance optimization
│   └── OPERATIONAL_RUNBOOK.md    # Day-to-day operations
│
├── docker/                        # Docker files (Phase 5, optional)
│   ├── Dockerfile                # Container definition
│   └── .dockerignore              # Docker ignore rules
│
├── docker-compose.yml             # Docker compose (optional)
│
├── venv/                          # Python virtual environment
│   ├── Scripts/                  # Windows executables
│   │   └── activate              # Activation script
│   ├── Lib/                       # Python packages
│   └── pyvenv.cfg                # Config
│
└── .git/                          # Git repository (if using git)
    └── ...
```

---

## Directory Descriptions

### `/src` - Main Application Code

**Purpose:** Core gateway application

```
src/
├── gateway.py (400-500 lines)
│   ├── FastAPI app initialization
│   ├── Route definitions (@app.post, @app.get)
│   ├── Request/response handling
│   ├── Error middleware
│   └── Startup/shutdown events
│
├── models.py (80-100 lines)
│   ├── GenerateRequest (Pydantic model)
│   ├── GenerateResponse
│   ├── HealthResponse
│   └── ErrorResponse
│
├── cache.py (200-250 lines)
│   ├── SemanticCache class
│   ├── Similarity matching (cosine)
│   ├── File I/O (JSON)
│   ├── TTL management
│   └── Cache statistics
│
├── ollama_client.py (100-150 lines)
│   ├── OllamaClient class
│   ├── Health check
│   ├── Generate request
│   ├── Stream response
│   └── Error handling
│
├── validators.py (80-120 lines)
│   ├── Prompt length validation
│   ├── Injection detection
│   ├── Character set validation
│   └── JSON schema validation
│
├── config.py (80-100 lines)
│   ├── Settings class
│   ├── Environment loading
│   ├── Defaults
│   └── Validation
│
├── security.py (100-150 lines, Phase 4)
│   ├── JWT handling
│   ├── Rate limiter
│   ├── Audit logging
│   └── Input sanitization
│
├── metrics.py (80-120 lines, Phase 2)
│   ├── Prometheus metrics
│   ├── Request counter
│   ├── Latency histogram
│   └── Cache hit rate gauge
│
└── utils.py (50-100 lines)
    ├── Helper functions
    ├── Token counting
    ├── Logging setup
    └── Text processing
```

### `/data` - Runtime Data

**Purpose:** Store cache, logs, and templates

```
data/
├── cache/
│   ├── [auto-created JSON files]
│   ├── cache_metadata.json
│   └── [removed after 24h TTL]
│
├── logs/
│   ├── ai_gateway.log         # Current day
│   ├── ai_gateway.2026-06-27.log
│   └── ai_gateway.2026-06-26.log
│
└── templates/
    ├── crud.json              # CRUD template
    ├── sql.json               # SQL template
    ├── documentation.json     # Documentation template
    ├── testing.json           # Testing template
    └── refactoring.json       # Refactoring template
```

### `/tests` - Test Suite

**Purpose:** Unit & integration tests

```
tests/
├── test_gateway.py (200-250 lines)
│   ├── Test /api/health
│   ├── Test /api/generate
│   ├── Test /api/models
│   └── Test error cases
│
├── test_cache.py (150-180 lines)
│   ├── Test cache hit/miss
│   ├── Test TTL expiration
│   ├── Test similarity matching
│   └── Test file I/O
│
├── test_validators.py (100-130 lines)
│   ├── Test prompt length
│   ├── Test injection detection
│   ├── Test character validation
│   └── Test edge cases
│
├── test_security.py (150-200 lines, Phase 4)
│   ├── Test injection attacks
│   ├── Test rate limiting
│   ├── Test JWT validation
│   └── Test error sanitization
│
├── test_api.py (120-150 lines)
│   ├── Integration tests
│   ├── End-to-end tests
│   └── Load tests
│
└── conftest.py (50-80 lines)
    ├── Pytest fixtures
    ├── Mock setup
    └── Test configuration
```

### `/docs` - Documentation

**Purpose:** Detailed user & operational documentation

```
docs/
├── API_EXAMPLES.md
│   ├── Code generation examples
│   ├── SQL examples
│   ├── Documentation examples
│   └── Client library examples
│
├── TROUBLESHOOTING.md
│   ├── Common errors
│   ├── Diagnostic steps
│   ├── Recovery procedures
│   └── Support resources
│
├── UPGRADE_GUIDE.md
│   ├── GPU upgrade steps
│   ├── Model switching
│   ├── Backup procedures
│   └── Rollback plan
│
├── PERFORMANCE_TUNING.md
│   ├── Latency optimization
│   ├── Throughput optimization
│   ├── Memory optimization
│   └── GPU optimization
│
└── OPERATIONAL_RUNBOOK.md
    ├── Daily operations
    ├── Monitoring
    ├── Alerts
    └── Maintenance schedule
```

### `/docker` - Containerization

**Purpose:** Docker deployment (optional, Phase 5)

```
docker/
├── Dockerfile
│   ├── Base image: python:3.11-slim
│   ├── Install dependencies
│   ├── Copy application
│   ├── Expose port 8000
│   └── CMD: python src/gateway.py
│
└── .dockerignore
    ├── venv/
    ├── __pycache__/
    ├── .git/
    └── .env
```

### `venv/` - Virtual Environment

**Purpose:** Isolated Python packages

```
venv/
├── Scripts/
│   ├── activate.bat        # Activation script (Windows)
│   ├── python.exe         # Python interpreter
│   └── pip.exe            # Package manager
│
├── Lib/
│   └── site-packages/     # Installed packages
│       ├── fastapi/
│       ├── pydantic/
│       ├── httpx/
│       └── ...
│
└── pyvenv.cfg            # Configuration
```

---

## File Size Expectations

### Source Code
```
src/gateway.py           ~ 400-500 lines (~15 KB)
src/cache.py             ~ 200-250 lines (~8 KB)
src/models.py            ~ 80-100 lines (~3 KB)
src/ollama_client.py     ~ 100-150 lines (~4 KB)
src/validators.py        ~ 80-120 lines (~3 KB)
src/config.py            ~ 80-100 lines (~3 KB)
src/utils.py             ~ 50-100 lines (~2 KB)
TOTAL:                   ~1,100 lines (~40 KB)
```

### Tests
```
test_gateway.py          ~ 200-250 lines (~8 KB)
test_cache.py            ~ 150-180 lines (~6 KB)
test_validators.py       ~ 100-130 lines (~4 KB)
test_api.py              ~ 120-150 lines (~5 KB)
TOTAL:                   ~600 lines (~23 KB)
```

### Documentation
```
README.md                ~300 lines (~12 KB)
ARCHITECTURE.md          ~600 lines (~25 KB)
INSTALLATION.md          ~400 lines (~16 KB)
ROADMAP.md               ~500 lines (~20 KB)
API_SPEC.md              ~400 lines (~16 KB)
TOTAL:                   ~2,200 lines (~89 KB)
```

### Data (Runtime)
```
Cache files              ~10-50 entries (~1-5 MB)
Log files                ~1-10 MB/day (rotate daily)
Model weights            3.8 GB (Qwen 7B)
TOTAL:                   ~3.8-3.85 GB
```

---

## File Creation Checklist

### Phase 1 (Weeks 1-2)
- [x] README.md
- [x] ARCHITECTURE.md
- [x] INSTALLATION.md
- [x] API_SPEC.md
- [x] requirements.txt
- [x] .env.example
- [x] src/gateway.py (basic)
- [x] src/models.py
- [x] src/ollama_client.py
- [x] src/validators.py
- [x] .gitignore

### Phase 2 (Weeks 2-3)
- [ ] src/cache.py
- [ ] src/config.py
- [ ] src/metrics.py
- [ ] src/security.py (basic)
- [ ] tests/test_gateway.py
- [ ] tests/test_cache.py
- [ ] tests/test_validators.py
- [ ] tests/conftest.py

### Phase 3 (Weeks 3-4)
- [ ] data/templates/*.json
- [ ] src/templates.py
- [ ] docs/API_EXAMPLES.md

### Phase 4 (Week 4)
- [ ] tests/test_security.py
- [ ] docs/TROUBLESHOOTING.md

### Phase 5+ (Month 2+)
- [ ] docker/Dockerfile
- [ ] docker-compose.yml
- [ ] docs/UPGRADE_GUIDE.md
- [ ] docs/OPERATIONAL_RUNBOOK.md

---

## Naming Conventions

### Python Files
- Snake case: `gateway.py`, `ollama_client.py`
- Descriptive names: `models.py`, `validators.py`, not `util.py`
- Module organization: Group related functions

### Test Files
- Prefix: `test_*.py`
- Match source: `test_gateway.py` for `gateway.py`
- Clear names: `test_cache_hit`, not `test_1`

### Data Files
- JSON templates: Lowercase, underscore: `crud.json`, `sql.json`
- Log files: `.log` extension, dated: `ai_gateway.2026-06-28.log`
- Cache files: Auto-generated, hash-based: `cache_abc123def.json`

### Documentation
- UPPERCASE.md for major docs: `README.md`, `ARCHITECTURE.md`
- Descriptive names: `INSTALLATION.md`, not `SETUP.md`
- Consistent format: Markdown (.md) for all

---

## .gitignore Entries

```
# Python
venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage/
htmlcov/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Application
data/cache/
data/logs/
data/*.log

# Build
dist/
build/
*.egg-info/

# Models (large, don't commit)
~/.ollama/models/
```

---

## Access Patterns

### Daily Development
```
Working directory: C:\Proyectos\AI-Platform\
Source code: src/
Tests: tests/
Configuration: .env (in root)
Logs: data/logs/ (check daily)
```

### During Debugging
```
Check logs: data/logs/ai_gateway.log
Check cache: data/cache/ (inspect files)
Run tests: pytest tests/ -v
Check metrics: curl http://localhost:8000/api/metrics
```

### During Deployment
```
Verify structure: Complete checklist above
Check dependencies: pip install -r requirements.txt
Set environment: cp .env.example .env && edit
Start service: python src/gateway.py
Verify endpoints: curl http://localhost:8000/api/health
```

---

## Storage Planning

### Phase 1 (Now)
```
Source code: ~50 KB
Installed packages: ~200 MB
Model weights: 3.8 GB
Cache (24h): ~5-10 MB
Logs (1 week): ~50-100 MB
TOTAL: ~4 GB
```

### Phase 5 (With 14B model)
```
Models: 3.8 GB (7B) + 8 GB (14B) = 11.8 GB
Cache: 10-50 MB
Logs: 50-100 MB
TOTAL: ~12 GB
```

### Phase 7 (Full maturity)
```
Models: 3.8 + 8 + optional = ~12+ GB
Cache: 100+ MB
Logs: 100-500 MB (archive old)
Docs: 1-2 MB
TOTAL: ~12.5-13 GB
```

---

**Last Updated:** June 28, 2026
**Status:** Phase 1 Structure Ready
