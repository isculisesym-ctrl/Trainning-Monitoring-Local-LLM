# Phase Validation Prompt — Reutilizable

**Copia esto al iniciar cada fase. Adapta según tu proyecto.**

---

## 🎯 Instrucciones Base (Copiar & Adaptar)

### Contexto (En N líneas — mantén conciso)
- Repo: [nombre]
- Rama actual: [branch]
- Objetivo: [qué hace esta fase]
- Cambios: [cuántos archivos, qué módulos]
- Commits: [git log últimos 2-3]

### Tu rol
- **Si eres Haiku:** smoke test rápido (tests + endpoints). ~5-10 min.
- **Si eres Sonnet:** feature work + code review. ~15-30 min.
- **Si eres Opus:** deep validation, bug-hunting, remediation. ~1-2 hours.

---

## ✅ Checklist Universal (Copia tal cual, rellena números reales)

```
1. pytest tests/ -q --tb=short
   → debe decir "N passed"

2. git log --oneline -1
   → verifica que es el commit esperado

3. [SI tienes gates de calidad]:
   black . --check --line-length=120
   isort . --check-only --profile black
   flake8 --max-line-length=120
   mypy src/ --ignore-missing-imports
   → todos deben pasar (no ✗)

4. [SI tienes servidor]:
   python -m [tu-server] --port [port] &
   sleep 2
   
   a) curl http://localhost:[port]/api/health
      → debe responder 200 (status: healthy | degraded | unhealthy)
   
   b) Dos requests idénticos a tu endpoint principal:
      curl -X POST http://localhost:[port]/api/[main-endpoint]
      Primera vez: [registra response time + cualquier flag de "cached"]
      Segunda vez: [registra response time, debe ser más rápida o mostrar cached=true]
   
   c) Verifica logs limpios:
      cat logs/[tu-log-file] | head -5
      → debe ser JSON limpio, no encoding errors, no stack traces
   
   d) Estadísticas (si aplica):
      curl http://localhost:[port]/api/stats
      → responde 200 con datos esperados
   
   e) kill %1

5. [SI NO tienes servidor, o es offline-only]:
   pytest tests/ --cov=src --cov-report=html
   → verifica que coverage ≥ 80%
   
   coverage report
   → lista qué líneas no se cubren (error branches, edge cases)

6. **Reporte final** (UNA línea):
   "PASS: N tests, gates=[✓ or ✗], [Server: AVAILABLE | DEGRADED | N/A], 
    [cache validated | N/A], logs clean, coverage X%"
```

---

## 🎓 Model-Specific Guidance

### Haiku: Smoke Test Role
**Cuándo:** Después de que Opus/Sonnet "dice" que está listo.  
**Qué hacer:** Ejecuta el checklist completo. Si algo falla → reporta, no fixes.  
**Reporte:** `PASS` o `FAIL + reason`.  
**Duración:** ~5-10 min.

**Ejemplo real:**
```
Ejecuté Phase 1 smoke test:
✓ 37 tests pass
✓ Commit 65c4595
✓ Health: degraded (esperado, no Ollama)
✓ Cache-hit: 2da llamada idéntica → cached=true
✓ Logs: JSON limpio, UTF-8 ok
→ PASS: 37 tests, gates green, cache verified, logs clean
```

---

### Sonnet: Feature Work Role
**Cuándo:** Trabajas en feature nuevos, bug fixes, refactor.  
**Qué hacer:** 
1. Lee VALIDATION_REPORT.md / HAIKU_HANDOFF.md (context previo)
2. Implementa la feature
3. Ejecuta checklist antes de handoff

**Reporte:** Describe qué se cambió, por qué, y verifica el checklist.

**Ejemplo:**
```
Feature: Added caching layer to /api/search

Cambios:
- src/cache.py: new LRU cache (1000 entries max)
- src/api.py: @cache_decorator on /search

Verificación:
✓ 45 tests pass (nuevos: 8)
✓ Coverage: 82% → 85%
✓ Gates: all green
✓ Cache hit verified (2x identical query)
→ Ready for Opus review
```

---

### Opus: Validation & Deep Fix Role
**Cuándo:** Código está "casi listo" pero podrían haber bugs no capturados por tests.  
**Qué hacer:**
1. Lee el contexto (commit messages, VALIDATION_REPORT)
2. **Ejecuta el checklist** (con comentarios sobre qué esperas ver)
3. Si algo falla → diagnostica + fixes con rigor
4. Re-ejecuta checklist hasta que pase
5. Documenta qué se arregló y por qué

**Reporte:** `PASS` con detalles, o `FAIL` + lista de fixes necesarios.

**Ejemplo (Phase 1):**
```
Validación Phase 1:

Initial: 9 tests pass, pero semantic cache es fake.
Diagnosis: lookup() es exact-hash, embedding() es roto.
Fixes:
- Rewrote embedding con signed feature hashing
- Fixed cache.get() para semantic scan
- Fixed gateway.generate() para servir cache
- Added 28 tests (coverage 66% → 83%)
- Arreglé 4 bugs adicionales (type errors, log encoding, etc.)

Final: ✓ 37 tests, 83% coverage, 97/100 score, all gates green
```

---

## 🔧 Cómo Adaptar para Tu Proyecto

**Paso 1:** Copia el checklist arriba.

**Paso 2:** Reemplaza estos placeholders:
- `[tu-server]`: e.g., `uvicorn main:app` o `flask run`
- `[port]`: e.g., `8000`, `5000`
- `[main-endpoint]`: e.g., `/api/search`, `/users`
- `[tu-log-file]`: e.g., `logs/app.log` o `var/log/app.log`
- `src/`: reemplaza con tu actual source dir

**Paso 3:** Si tienes gates especiales (lint, format, security scans), agrégalos:
```bash
# Ejemplo: bandit para security
bandit -r src/ --exit-code 0  # solo reporting, no falla

# Ejemplo: pytest plugins especiales
pytest tests/ --cov=src --cov-threshold=80
```

**Paso 4:** Documenta expectativas offline:
```bash
# Si tu server tiene modo degradado
curl http://localhost:8000/api/health
# Esperado: status="degraded" + service_available=false (es OK, no error)
```

---

## 📝 Ejemplo Completo Adaptado: FastAPI Project

Supongamos que tienes un FastAPI project con tests, black, mypy.

**Checklist adaptado:**

```bash
# 1. Tests
cd /path/to/project
source venv/bin/activate
pytest tests/ -q --tb=short
# ✓ Expected: "42 passed"

# 2. Commit
git log --oneline -1
# ✓ Expected: "Implement search cache" or whatever you named it

# 3. Gates
black src/ tests/ --check --line-length=120
isort . --check-only --profile black
flake8 --max-line-length=120
mypy src/ --ignore-missing-imports
# ✓ Expected: all silent (no errors)

# 4. Server + endpoints
python -m uvicorn src.main:app --port 8000 &
sleep 2

# 4a. Health
curl http://localhost:8000/api/health
# ✓ Expected: {"status":"healthy"}

# 4b. Cache hit (search endpoint)
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"q":"test"}'
# Registra: response time, cached flag

curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"q":"test"}'
# Debe ser más rápido + cached=true

# 4c. Logs
cat logs/app.log | head -3
# ✓ Expected: JSON, no encoding errors

# 4d. Stats
curl http://localhost:8000/api/cache/stats
# ✓ Expected: {"entries": N, "hit_rate": X%}

kill %1
```

**Final report:**
```
PASS: 42 tests, gates=✓, Server=AVAILABLE, cache-hit verified, logs clean, coverage=85%
```

---

## 🚨 Red Flags (Si ves alguno, investiga antes de marcar PASS)

- ❌ Tests pass pero endpoint returns error
- ❌ `black` passes pero `mypy` fails (gates deslinked)
- ❌ Cache hit not verified (2x request no muestran `cached=true`)
- ❌ Log encoding error (`patr?n` instead of `patrón`)
- ❌ Server crashes when external service unavailable (debe degrade gracefully)
- ❌ Coverage < 80% (coverage es gate también)
- ❌ Commit message não relacionado ao work (sign-off missing o confuso)

---

## 💾 Handoff Format

Cuando pases código al siguiente phase/model:

```markdown
# Phase N Handoff

**Branch:** dev  
**Commit:** [sha] — [message]  
**Validated by:** [Haiku | Sonnet | Opus]  
**Date:** [YYYY-MM-DD]

**Summary:**
[1-2 líneas: qué se hizo]

**Test results:**
- Tests: N passed ✓
- Coverage: X% ✓
- Gates (black/isort/flake8/mypy): ✓ / ✗
- Server: [AVAILABLE | DEGRADED | N/A]
- Cache (if applicable): [verified | N/A]

**Blockers:** [none | list if any]

**Next phase:** [Role + what to do]
```

---

## 🎯 TL;DR — Máximo Template

```bash
# Copy-paste this for a quick smoke test:

cd /your/repo
source venv/bin/activate

pytest tests/ -q --tb=short                                      # 1
git log --oneline -1                                             # 2
black . --check --line-length=120 && isort . --check-only && flake8 --max-line-length=120 && mypy src/ --ignore-missing-imports  # 3
python -m uvicorn src.main:app --port 8000 &; sleep 2            # 4 start
curl http://localhost:8000/api/health; curl -X POST http://localhost:8000/api/[your-endpoint] -d '{"key":"value"}'; curl -X POST http://localhost:8000/api/[your-endpoint] -d '{"key":"value"}'; kill %1  # 4 test

# Report:
echo "PASS: X tests, gates=✓, cache verified, logs clean"
```

---

**Remember:** Good validation is what separates "tests pass" from "this actually works." Take 10 min to run the checklist. It pays dividends.
