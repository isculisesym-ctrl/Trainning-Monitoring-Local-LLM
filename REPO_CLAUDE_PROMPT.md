# Repository Claude Prompt — Template Reutilizable

**Para usar en cualquier repo. Copia esto en tu CLAUDE.md o como system prompt.**

---

## 📋 Context Section (Fill in your own)

```markdown
# [Project Name] — Claude Instructions

## Overview
- **Repo:** [github URL or local path]
- **Language:** [Python / TypeScript / Go / etc.]
- **Framework:** [FastAPI / Flask / React / etc.]
- **Testing:** [pytest / jest / go test / etc.]
- **Quality gates:** [black, isort, flake8, mypy? eslint? etc.]

## Current state
- **Branch:** [main / dev / etc.]
- **Recent work:** [1-2 sentences on what was just completed]
- **Next phase:** [what's being worked on now]

## How to validate your work

### Tests
```bash
[paste your test command]
# Expected: "N passed"
```

### Quality gates
```bash
[paste your format/lint/type-check commands]
# Expected: all pass
```

### Server (if applicable)
```bash
[paste how to start your server]
# Expected: listens on [port]

# Test your endpoint:
[paste curl/http command to test]
```

### Offline validation (if applicable)
```bash
[paste any offline-path checks]
# Expected: responds 503 (if service unavailable) or works gracefully
```

## Model-specific guidance

- **Haiku:** Use for smoke tests, verification. ~5-10 min.
- **Sonnet:** Use for feature work, PRs, debugging. ~15-30 min.
- **Opus:** Use for validation, deep fixes, architecture. ~1-2 hours.

## Common gotchas
- [List 1-2 bugs/patterns that happened before]
- [How to spot them]
- [How to prevent them]

## Handoff criteria

When handing off to next phase/model:
- [ ] All tests pass
- [ ] All quality gates pass
- [ ] Server starts and endpoints respond
- [ ] Cache/performance verified (if applicable)
- [ ] Logs are clean (no encoding errors, no crash stacks in normal flow)
- [ ] Coverage ≥ 80% (if you have gates)

---
```

---

## 🚀 Phase-Based Workflow Template

Use this structure for multi-phase projects:

### Phase N Template

```markdown
# Phase N: [Title]

## Goal
[1-2 sentences: what does this phase build?]

## Validator
[Haiku — smoke test] / [Sonnet — feature] / [Opus — deep validation]

## Success criteria
- [ ] [Specific thing #1]
- [ ] [Specific thing #2]
- [ ] Tests pass: [N expected]
- [ ] Gates pass: [which ones]

## Changes
- [list of files you expect to change]

## Handoff checklist
```bash
# Copy from PHASE_VALIDATION_PROMPT.md and adapt
pytest tests/ -q --tb=short
git log --oneline -1
[your quality gates]
[your server + endpoints test]
```

## Blockers / Recommendations
[Any known issues or warnings for the next phase]

---
```

---

## 📊 Multi-Team Workflow (Copy as-is)

If multiple teams/models work on the same repo:

### How to structure handoffs

1. **Opus (Phases 1, deep validation):**
   - Validates everything
   - Documents all bugs + fixes
   - Creates VALIDATION_REPORT.md with detailed findings
   - Leaves code on branch (not committed yet)

2. **Sonnet (Phases 2-3, feature work):**
   - Reads VALIDATION_REPORT.md from prior phase
   - Implements feature
   - Runs full checklist
   - Leaves code on branch with PR draft

3. **Haiku (Smoke test, before merge):**
   - Runs full checklist one more time
   - Verifies cache hits, offline paths, logs
   - Reports PASS/FAIL

### Branch strategy
```bash
main (stable, tested)
  └── dev (staging)
      ├── phase-1-semantic-cache (Opus validated)
      ├── phase-2-prometheus (Sonnet feature)
      └── phase-3-deploy (Haiku smoke test)
```

Each phase merges back to `dev` after validation.

---

## 🎓 Common Patterns by Project Type

### FastAPI + pytest + black + mypy

```markdown
## Validation

### Tests
```bash
pytest tests/ -q --tb=short
```

### Quality gates
```bash
black src/ tests/ --check --line-length=120
isort . --check-only --profile black
flake8 --max-line-length=120
mypy src/ --ignore-missing-imports
```

### Server
```bash
python -m uvicorn src.main:app --port 8000 &
sleep 2

curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/main-endpoint \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

kill %1
```

---
```

### Flask + pytest + black + mypy

```markdown
## Validation

### Tests
```bash
pytest tests/ --tb=short -v
```

### Quality gates
```bash
black app/ tests/ --check --line-length=120
isort . --check-only --profile black
flake8 --max-line-length=120
mypy app/ --ignore-missing-imports
```

### Server
```bash
export FLASK_ENV=development
flask run --port 8000 &
sleep 2

curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/endpoint -d '{"key":"value"}'

kill %1
```

---
```

### TypeScript + jest + eslint + ts-check

```markdown
## Validation

### Tests
```bash
npm test -- --passWithNoTests --coverage
```

### Quality gates
```bash
npm run lint
npm run type-check
npm run format:check
```

### Server (if applicable)
```bash
npm start &
sleep 2

curl http://localhost:3000/api/health

kill $!
```

---
```

---

## 🔄 Issue/Task Template for Claude

When you file work, use this structure so Claude understands scope:

```markdown
# [Scope] Feature / Bug / Validation

## Context
[1-2 lines: why are we doing this?]

## What
[Clear description of the change]

## How to validate
```bash
[the exact commands to verify it works]
```

## Dependencies
[Any prior phases / external services needed]

## Model suggestion
[Haiku | Sonnet | Opus — based on complexity]

## Estimates
- Haiku: ~X min
- Sonnet: ~Y min
- Opus: ~Z min (if deep fix needed)
```

---

## 💡 Best Practices (Copied from Phase 1 validation)

### Do's
- ✅ Run the full checklist (tests + gates + live server)
- ✅ Test cache hits (2x identical request)
- ✅ Verify offline graceful degradation (no crashes)
- ✅ Check logs for encoding errors (UTF-8)
- ✅ Document what you fixed and why
- ✅ Use conservative defaults (semantic_similarity=0.95, not 0.5)
- ✅ Clear docstrings + type hints (mypy will catch bugs)

### Don'ts
- ❌ Merge code that only passed tests (tests miss things)
- ❌ Trust a single gate (black + mypy catch different bugs)
- ❌ Assume external service always available (offline paths matter)
- ❌ Use bare `except:` (catch specific exceptions)
- ❌ Use `x or default` for booleans (snaps 0.0 to 0.7)
- ❌ Skip handoff documentation (next phase needs context)

---

## 📝 Sign-off Template

When you complete a phase:

```markdown
## Sign-off

**Phase:** N  
**Validator:** [Model name]  
**Date:** YYYY-MM-DD  

**Status:** ✅ PASS

**Results:**
- Tests: N passed, X% coverage
- Gates: all green
- Server: [AVAILABLE | DEGRADED | N/A]
- Cache: [verified | N/A]
- Logs: clean

**Blockers:** [none | list]

**Next:** [Phase N+1 ready for [Model name]]

**Token usage:** ~XXX tokens

---
```

---

## 🚦 Quick Decision Tree

**How do I know which model to use?**

```
Is it a smoke test (just run checklist)?
  → Haiku ✓

Is it a new feature or bug fix?
  → Sonnet ✓

Is the code broken or validation uncertain?
  → Opus ✓

Do I need architectural advice?
  → Opus ✓

Am I blocked and need second opinion?
  → Opus ✓

Else → Sonnet (safe default)
```

---

## 📚 Related docs

- [PHASE_VALIDATION_PROMPT.md](PHASE_VALIDATION_PROMPT.md) — detailed checklist + model roles
- [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md) — how to document phases
- [VALIDATION_REPORT.md](VALIDATION_REPORT.md) — example of deep validation (Phase 1)

---

**Version:** 1.0  
**Based on:** Phase 1 (AI-Platform) validation learnings  
**Applicable to:** Any repo, any team, any model  
**Last updated:** 2026-06-28
