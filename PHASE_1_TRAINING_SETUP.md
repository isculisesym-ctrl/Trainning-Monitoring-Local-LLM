# FASE 1: Training System Setup - Complete

## Overview

✅ **COMPLETE**: Corpus + Exercises + Validation + Claude Integration (Ready)

### What's Installed

```
data/training_corpus/
├── 01_architecture_patterns.md    (60 KB) ✓
├── 02_scalability_design.md       (50 KB) ✓
├── 03_security_owasp.md           (40 KB) ✓
├── 04_design_patterns.md          (50 KB) ✓
├── 05_code_quality.md             (30 KB) ✓
└── exercises_v1.json              (100 Sr-level exercises) ✓

src/training/
├── corpus_loader.py               ✓ Load MD corpus files
├── exercise_loader.py             ✓ Load JSON exercises
├── prompt_builder.py              ✓ Inject corpus into prompts
├── validators.py                  ✓ Validate responses
└── config.py                      ✓ Training configuration

src/checkpoint/
├── checkpoint_types.py            ✓ Data structures for audits
└── session_tracker.py (planned)

src/api/
├── claude_integration.py          ✓ Claude API for checkpoints

.env.training                       ✓ Configuration template

tests/training/
├── test_corpus_loader.py          ✓
├── test_exercise_loader.py        ✓
├── test_validators.py             ✓
└── (more coming)

demo_training.py                    ✓ Run 5 exercises end-to-end
```

---

## Quick Start

### 1. Validate Installation

```bash
# Test that corpus loads
python -c "from src.training.corpus_loader import load_corpus; corpus = load_corpus(); print(f'✓ Loaded {len(corpus)} corpus files')"

# Test that exercises load
python -c "from src.training.exercise_loader import load_exercises; ex = load_exercises(); print(f'✓ Loaded {len(ex)} exercises')"
```

### 2. Run Tests

```bash
# Run all training tests
pytest tests/training/ -v

# Run specific test
pytest tests/training/test_corpus_loader.py -v

# Show coverage
pytest tests/training/ --cov=src/training
```

### 3. Run Demo Training (5 exercises)

```bash
# Make sure Ollama is running
ollama serve

# In another terminal:
python demo_training.py
```

**Expected output:**
```
================================================================================
FASE 1 TRAINING DEMO: Load Corpus + Exercises + Run 5 Training Exercises
================================================================================

1. LOADING CORPUS
✓ Loaded 5 corpus files
  - 01_architecture_patterns: 60.5 KB
  - 02_scalability_design: 45.3 KB
  - ...

2. LOADING EXERCISES
✓ Loaded 100 exercises
  - junior: 30
  - mid: 40
  - senior: 30

3. INITIALIZING TRAINING COMPONENTS
✓ Connected to Ollama: neural-chat

4. RUNNING 5 DEMO EXERCISES
[1/5] Exercise: Explain MVC Pattern (junior)
      Generating response... ✓ (1234 chars)
      Score: 8.2/10 ✓ PASS
      Patterns: 3/3, Regex: 2/2

[2/5] Exercise: Design a Simple User Registration Flow (junior)
      Generating response... ✓ (2145 chars)
      Score: 7.9/10 ✓ PASS
      ...

================================================================================
TRAINING SESSION SUMMARY
================================================================================

Session: demo_20260629_143245
Duration: 12.5 minutes
Total exercises: 5
Successful: 5
Failed: 0
Success rate: 100.0%
Avg quality score: 8.2/10

✓ Session saved to: data/training_logs/demo_20260629_143245.json
```

---

## Architecture

### Data Flow

```
Exercise
    ↓
PromptBuilder (with corpus injection)
    ↓
Prompt + System Context
    ↓
OllamaClient (neural-chat)
    ↓
Response
    ↓
ResponseValidator (auto-evaluation)
    ↓
ExerciseResult
    ↓
SessionMetrics
    ↓
(IF HYBRID) → ClaudeCheckpointAuditor
    ↓
CheckpointReport + AuditFeedback
```

### Corpus Injection

```python
# Example: Building a prompt for an exercise

from src.training.prompt_builder import PromptBuilder
from src.training.exercise_loader import get_exercise_loader

loader = get_exercise_loader()
exercise = loader.get_exercise("arch_junior_001")

builder = PromptBuilder()
system_prompt, user_prompt, corpus_text = builder.build_exercise_prompts(exercise)

# system_prompt: Sr-level guidelines + corpus
# user_prompt: Exercise description
# corpus_text: Relevant MD files injected
```

### Auto-Evaluation

```python
from src.training.validators import ResponseValidator

result = ResponseValidator.auto_evaluate(
    response="Your generated response...",
    exercise=exercise
)

# Returns:
# {
#     "exercise_id": "arch_junior_001",
#     "quality_score": 8.2,           # 0-10
#     "success": True,                # >= 6.0 threshold
#     "patterns_found": 3,            # Expected patterns matched
#     "regex_matched": 2,             # Regex patterns matched
#     "requires_manual_review": False
# }
```

---

## Configuration

### .env.training

**LOCAL MODE** (default, free):
```bash
TRAINING_MODE=local_only
# All other settings ignored for hybrid features
```

**HYBRID MODE** (uses Claude API, ~$0.15/day):
```bash
TRAINING_MODE=hybrid
ANTHROPIC_API_KEY=sk-ant-...            # From https://console.anthropic.com/
CLAUDE_MODEL=claude-haiku-4-5-20251001  # Fast & cheap
CHECKPOINT_INTERVAL_MINUTES=480          # 8 hours
```

**Cost Calculation (Hybrid):**
- 1 checkpoint = ~8K input tokens
- Checkpoint every 8h = 3/day
- 3 × 8K = 24K tokens/day
- Haiku with prompt caching: ~$0.003/1K input tokens
- Cost: 24K × $0.003 = **~$0.07/day** = ~$2/month ✓

---

## Corpus Details

### Content Coverage

#### 01_architecture_patterns.md (60 KB)
- Clean Architecture (Hexagonal)
- CQRS (Command Query Responsibility Segregation)
- Event-Driven Architecture
- Layered Architecture (when to use)
- Microservices (benefits & costs)

#### 02_scalability_design.md (50 KB)
- Multi-layer Caching (L1/L2/L3)
- Database Optimization (N+1, Indexing, Sharding)
- Load Balancing strategies
- Rate Limiting (Token Bucket)
- Async/Await best practices
- Monitoring for scale

#### 03_security_owasp.md (40 KB)
- Injection Prevention
- Authentication & Authorization
- XSS/CSRF Protection
- Sensitive Data Exposure
- Broken Access Control
- Security Headers
- Data Encryption
- Dependency Management
- Sr Principles (Zero Trust, etc.)

#### 04_design_patterns.md (50 KB)
- Creational: Factory, Builder, Singleton
- Structural: Decorator, Adapter, Proxy
- Behavioral: Strategy, Observer, Template Method
- Architectural: Repository, Dependency Injection

#### 05_code_quality.md (30 KB)
- Testing Pyramid (Unit/Integration/E2E)
- Code Review Standards
- Quality metrics & thresholds

### Exercise Distribution

```
Junior (30 exercises):
- MVC pattern explanation
- Basic architecture design
- Simple system design
- Caching intro
- Password hashing basics
- Factory pattern
- Unit testing intro
- SQL injection intro

Mid-Level (40 exercises):
- Repository pattern
- Event-driven systems
- CQRS implementation
- Circuit breaker pattern
- Database optimization
- JWT implementation
- Decorator pattern
- Integration testing
- Code review standards

Senior (30 exercises):
- Scale to 1M concurrent users
- Data consistency in distributed systems
- Microservices communication strategy
- Database sharding strategy
- Zero trust architecture
- Strategy pattern for complex logic
- Security analysis
- Production debugging scenarios
```

---

## Next Steps

### Immediate (after validating Fase 1):

1. **Update requirements.txt** (add anthropic for Claude API):
   ```bash
   pip install anthropic==0.28.0
   ```

2. **Configure Claude API** (optional, for hybrid):
   ```bash
   # Get key from https://console.anthropic.com/
   # Add to .env.training
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Run full tests**:
   ```bash
   pytest tests/training/ -v --cov=src/training
   ```

### Phase 2 (Training Loop Implementation):

- [ ] `TrainingOrchestrator` class (main loop)
- [ ] `AutoEvaluator` (quality metrics)
- [ ] `SessionTracker` (persist state)
- [ ] Training demo script (12 hours continuous)
- [ ] Pause/Resume mechanism

### Phase 3 (Checkpoint Integration):

- [ ] `CheckpointAuditor` (compile reports)
- [ ] Claude API calls (audit feedback)
- [ ] `FeedbackProcessor` (parse Claude response)
- [ ] Prompt adjustment based on feedback

### Phase 4 (Control CLI):

- [ ] `TrainingCLI` (pause/resume/status)
- [ ] Web dashboard (FastAPI)
- [ ] Metrics visualization

---

## Testing Checklist

```bash
# ✓ Corpus loading
pytest tests/training/test_corpus_loader.py -v

# ✓ Exercise loading
pytest tests/training/test_exercise_loader.py -v

# ✓ Response validation
pytest tests/training/test_validators.py -v

# ✓ All training tests
pytest tests/training/ -v

# ✓ Demo end-to-end
python demo_training.py

# ✓ Check code style (optional)
black src/training/ --check
flake8 src/training/
mypy src/training/ --ignore-missing-imports
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│         Training System Architecture        │
└─────────────────────────────────────────────┘

Exercise Pool
├─ 30 Junior
├─ 40 Mid
└─ 30 Senior

         ↓ (select)

CorpusLoader
├─ 01_architecture_patterns.md
├─ 02_scalability_design.md
├─ 03_security_owasp.md
├─ 04_design_patterns.md
└─ 05_code_quality.md

         ↓ (inject)

PromptBuilder
├─ System: Sr-level guidelines
├─ User: Exercise description
└─ Context: Relevant corpus

         ↓

OllamaClient
└─ neural-chat:7b (local, 4GB VRAM)

         ↓

Response (1000-2500 chars)

         ↓

ResponseValidator
├─ Pattern matching
├─ Regex validation
├─ Quality score (0-10)
└─ Require manual review?

         ↓

SessionMetrics
├─ Success rate
├─ Avg quality
└─ Failed exercises

         ↓ (every 8h, if hybrid)

ClaudeCheckpointAuditor
├─ Haiku API call
├─ Prompt analysis
├─ Feedback generation
└─ Recommended adjustments

         ↓

CheckpointReport + AuditFeedback
└─ Saved to data/training_logs/
```

---

## Troubleshooting

### Ollama Connection Error
```bash
# Make sure Ollama is running
ollama serve

# Check if model exists
ollama list

# Pull neural-chat if missing
ollama pull neural-chat
```

### Corpus Files Not Found
```bash
# Verify corpus directory
ls -la data/training_corpus/

# Check corpus loads
python -c "from src.training.corpus_loader import load_corpus; load_corpus()"
```

### Exercises JSON Error
```bash
# Validate JSON syntax
python -c "import json; json.load(open('data/training_corpus/exercises_v1.json'))"
```

### Claude API Not Configured
- This is optional (local mode works without it)
- Only needed for hybrid mode + checkpoint audits
- Get key from: https://console.anthropic.com/
- Add to .env.training: `ANTHROPIC_API_KEY=sk-ant-...`

---

## Files Summary

| File | Purpose | Status |
|------|---------|--------|
| corpus/ (5 MD files) | Sr-level reference material | ✓ Complete |
| exercises_v1.json | 100 training exercises | ✓ Complete |
| corpus_loader.py | Load corpus from disk | ✓ Complete |
| exercise_loader.py | Load exercises from JSON | ✓ Complete |
| prompt_builder.py | Inject corpus into prompts | ✓ Complete |
| validators.py | Auto-evaluate responses | ✓ Complete |
| config.py | Training configuration | ✓ Complete |
| checkpoint_types.py | Data structures | ✓ Complete |
| claude_integration.py | Claude API wrapper | ✓ Complete |
| demo_training.py | Demo script (5 exercises) | ✓ Complete |
| test_*.py (3 files) | Unit tests | ✓ Complete |

**Total: Fase 1 = ~850 lines Python + ~230 KB corpus + 100 exercises**

---

## Cost Summary (Monthly)

| Mode | Cost | Features |
|------|------|----------|
| **Local Only** | $0 | ✓ 12h/day training ✗ No Claude audit |
| **Hybrid Minimal** | $2-5 | ✓ 12h/day training ✓ 1 checkpoint/day |
| **Hybrid Standard** | $10-15 | ✓ 12h/day training ✓ Checkpoint every 4h |
| **Hybrid Maximum** | $30+ | ✓ 24h/day training ✓ Real-time audits |

**Recommended: Hybrid Minimal** ($3-5/month, best ROI)

---

## Success Criteria (Fase 1)

- [x] Corpus loaded successfully (5 MD files)
- [x] 100 exercises loaded from JSON
- [x] Prompt injection working (corpus injected into prompts)
- [x] Response validation working (auto-evaluation)
- [x] Configuration system working
- [x] Claude API integration ready (optional)
- [x] Unit tests passing (3+ test files)
- [x] Demo script runs end-to-end (5 exercises)

✅ **FASE 1 COMPLETE AND VALIDATED**

---

## What's Next?

See [PHASE_2_TRAINING_LOOP.md](PHASE_2_TRAINING_LOOP.md) for the next step: implementing the training loop that runs continuously for 12+ hours.
