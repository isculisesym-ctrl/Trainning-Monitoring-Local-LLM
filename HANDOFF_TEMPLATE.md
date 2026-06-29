# Handoff Template — Phase-Based Validation & Model Selection

**Purpose:** Reutilizable por cualquier equipo. Captura lecciones de Fase 1: semantic cache real, smoke test, gates de calidad, model selection.

---

## 🎯 Model Selection Quick Guide

### Use **Haiku 4.5** when:
- **Smoke test / validation** (what you just did) — rápido, suficiente para tests + endpoints
- Task es deterministic (tests pasan/fallan, endpoint es 200 o 503)
- Time-sensitive (5-10 min task windows)
- Cost matters (Haiku es 3x cheaper)

**Ejemplo Phase 1:** smoke test completo en 3 min con Haiku.

---

### Use **Sonnet 4.6** when:
- **Incremental feature work** — moderada complejidad, no arquitectura
- Code review / debugging (requiere context but no multi-file reasoning)
- Refactoring known scope
- Time: 10-30 min tasks

**Típico:** "fix this bug", "add this endpoint", "optimize this function"

---

### Use **Opus 4.8** when:
- **Validation exhaustiva** — necesitas descubrir bugs ocultos no en tests
- **Arquitectura / design decisions** — multi-file trade-offs
- **Fixing broken stuff** → necesitas el razonamiento más profundo
- Code que nunca fue validado en vivo
- Time: 20 min — 2 hours, o "unlimited" context needed

**Ejemplo Phase 1:** Opus validó el código, encontró 4 bugs ocultos + lo arregló. Haiku solo hubiera pasado los tests (fake cache).

---

### Use **Claude 4.X models** (current LLM family):
- Latest = más barato + rápido: **Sonnet 4.6** (go-to para Feature work)
- Fallback si Sonnet falla: **Opus 4.8** (el más inteligente)
- Offline/edge: ninguno (requieren API)

---

## ✅ Handoff Checklist (Aplicable a cualquier repo)

Cuando cierres una fase y le pases el código al siguiente equipo/model:

### 1️⃣ **Verify the commit**
```bash
git log --oneline -1
# Debe mostrar el commit que documentaste
```

### 2️⃣ **Run all tests**
```bash
pytest tests/ -q --tb=short
# ✓ Expected: "N passed"
```

### 3️⃣ **Run quality gates** (si los tienes)
```bash
# Formato, linting, type checking
black . --check --line-length=120
isort . --check-only --profile black
flake8 --max-line-length=120
mypy src/ --ignore-missing-imports
```

### 4️⃣ **If you have a dev server:**
```bash
python -m uvicorn main:app --port 8000 &
sleep 2

# Test health
curl http://localhost:8000/api/health

# Test a main flow (2x to check cache/idempotence)
curl -X POST http://localhost:8000/api/your-endpoint ...
curl -X POST http://localhost:8000/api/your-endpoint ...
# Second response should show `cached=true` or instant response

# Check logs are clean (no encoding errors, no stack traces)
cat logs/app.log | head -5

kill %1
```

### 5️⃣ **If offline paths exist (no external service):**
```bash
curl http://localhost:8000/api/health
# status="degraded" is OK (expected when service unavailable)

curl http://localhost:8000/api/stats
# Should respond 200 with empty/zero data (not 503)
```

### 6️⃣ **Report & Document**
```
PASS: N tests, [Service: AVAILABLE | DEGRADED], cache-hit verified, logs clean.
Token usage: ~XXX tokens
```

---

## 📋 Lecciones desde Phase 1

### 🔴 Bug Patterns We Fixed (learn from our mistakes)

| Bug | How to spot | How to prevent |
|-----|-------------|----------------|
| **Fake semantic cache** | Tests pass but feature doesn't work in vivo | Run actual endpoints + measure cache hit (2x identical request) |
| **Cache never served** | `cached=false` every time | Trace path: is `if cached_response:` actually there? |
| **Type errors on None** | `temp or default` snaps `0.0→0.7` | Use `... if x is not None else ...` |
| **Bare exceptions** | `except:` hides real bugs | Use `except SpecificError:` only |
| **Log corruption** | `patr?n` instead of `patrón` | Set `encoding="utf-8"` on file handlers |
| **Unlinked gates** | black passes but flake8 fails | Run all 4 (black, isort, flake8, mypy) together |

### ✅ What Worked Well

- **Layered testing:** Unit tests (37) + offline paths + live server flow
- **Conservative thresholds:** semantic_similarity=0.95 (not 0.5) → no false positives
- **Graceful degradation:** offline mode returns 503 for /generate (no crash), but /health and /stats work
- **Clear docstrings & type hints:** mypy found 30+ bugs that tests missed
- **Coverage target (80%):** forces you to test error branches, not just happy path

---

## 📦 How to Adapt This Template

**For your repo:**
1. Copy checklist items 1–6 above
2. Replace `N` with your test count
3. Replace `your-endpoint` with an actual endpoint
4. Adjust log path, port, endpoints for your project
5. Document any project-specific gates or offline flows

**Commit message:**
```
Handoff: Phase N complete, smoke test verified
- N tests pass, X% coverage
- All gates green (black/isort/flake8/mypy)
- [Service]: AVAILABLE / DEGRADED
- Ready for Phase N+1 (Opus)
```

---

## 🚀 Next Phase Template

When you're ready for the next phase, your handoff should look like:

```markdown
# Phase N+1 Handoff

**Validator:** [Opus | Sonnet | Haiku] (fresh chat, role: [describe])
**Branch:** `[your-branch]`
**Status:** [describe what this phase builds]

**Quick checks:**
[copy checklist items 1-6 with actual numbers]

**Blockers & recommendations:**
- [If any issues exist]

**Sign-off:** 
Code ready for Phase N+1. [Role] to take over.
```

---

## 💡 Pro Tips

- **Use Haiku for smoke tests** (the pattern you just validated works)
- **Use Opus for deep fixes** (when something is wrong and tests don't catch it)
- **Always verify gates** (they catch bugs tests miss)
- **Test offline paths** (services fail; your code shouldn't)
- **Cache verification** (2x identical call must show `cached=true`)
- **Logs must be clean** (encoding, no stack traces in happy path)

---

**Document everything in the handoff. The next person (or model) needs to know:**
- What was the goal
- How do you know it works
- What were the gotchas
- What to try next
