# OPUS - RESUME PROMPT FOR NEW CHAT

**Tu misión:** Validar exhaustivamente el trabajo de Phase 1 del AI-Platform. Este es un documento técnico crudo y real, no superficial.

**Context:** 
- Usuario creó Phase 1 completa en rama `dev` (Claude Code sesión anterior)
- Commit: "Implement Phase 1: FastAPI Gateway with Ollama Integration"
- 13 archivos nuevos (8 módulos Python + 3 tests + 2 init)
- 9/9 tests pasan actualmente
- Usuario quiere validación EXHAUSTIVA y CRUDA (no cosmética)

---

## YOUR EXACT TASKS (en orden)

### TASK 1: Entender completamente el código creado (30 min)

**Contexto del proyecto:**
- FastAPI gateway que se conecta a Ollama (LLM local Qwen 7B)
- Semantic caching file-based (similitud coseno)
- Validación de input y seguridad
- REST API con endpoints: /api/health, /api/generate, /api/stream, /api/models, /api/cache

**Lee estos archivos completamente:**
1. `VALIDATION_PLAN.md` - Tu guía exhaustiva
2. `src/config.py` - Settings and defaults
3. `src/models.py` - Pydantic schemas
4. `src/validators.py` - Input validation logic
5. `src/utils.py` - Helper functions (embedding, logging)
6. `src/cache.py` - File-based semantic cache
7. `src/ollama_client.py` - Async HTTP client to Ollama
8. `src/gateway.py` - FastAPI app with endpoints
9. Todos los tests en `tests/`

**Deliverable:** Mental model claro de cómo funciona todo junto

---

### TASK 2: Ejecutar validación de código quality (15 min)

**Run these exact commands and report results:**

```bash
# Activate venv first
.\venv\Scripts\Activate.ps1

# 1. Tests (deben pasar 9/9)
pytest tests/ -v --asyncio-mode=auto

# 2. Code formatting
black src/ tests/ --check

# 3. Import ordering  
isort src/ tests/ --check-only

# 4. PEP8 linting
flake8 src/ tests/ --max-line-length=120

# 5. Type checking
mypy src/ --ignore-missing-imports

# 6. Coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

**Expected:**
- pytest: 9 passed
- black: OK (no changes)
- isort: OK (no changes)
- flake8: 0 errors (warnings OK)
- mypy: 0 errors
- coverage: >80% (alcanzable)

**Deliverable:** Screenshot/output de cada comando + Pass/Fail assessment

---

### TASK 3: Arquitectura & Dependencies Check (20 min)

**Verificar manualmente:**

```python
# 3.1 - No hay imports circulares
python -c "from src.config import settings; print('✓ config OK')"
python -c "from src.utils import setup_logging; print('✓ utils OK')"
python -c "from src.models import GenerateRequest; print('✓ models OK')"
python -c "from src.validators import validate_prompt; print('✓ validators OK')"
python -c "from src.cache import Cache; print('✓ cache OK')"
python -c "from src.ollama_client import OllamaClient; print('✓ ollama_client OK')"
python -c "from src.gateway import app; print('✓ gateway OK - ALL IMPORTS WORK')"

# 3.2 - Verificar estructura de directorios
python -c "import os; assert os.path.exists('data/cache'); assert os.path.exists('data/logs'); print('✓ data dirs created')"

# 3.3 - Verificar requirements.txt
pip list | grep -E "fastapi|pydantic|httpx|uvicorn|pytest"
# Todas deben estar presentes
```

**Deliverable:** Confirmación de que no hay circular imports y estructura es correcta

---

### TASK 4: Async/Concurrency Validation (25 min)

**READ THESE METHODS MANUALLY y valida que sean verdaderamente async:**

En `src/cache.py`:
- [ ] `async def get()` - ¿espera correctamente archivos IO?
- [ ] `async def set()` - ¿escribe sin bloquear?
- [ ] `async def clear()` - ¿borra sin bloquear?
- [ ] `json.load() / json.dump()` - ¿son síncronos? (SÍ, OK porque son operaciones rápidas)

En `src/ollama_client.py`:
- [ ] `async def check_connection()` - ¿usa httpx.AsyncClient?
- [ ] `async def generate()` - ¿retorna dict o response?
- [ ] `async def stream_generate()` - ¿es AsyncGenerator?
- [ ] `__aenter__()` / `__aexit__()` - ¿context manager es async?
- [ ] Connection management - ¿se cierra siempre?

En `src/gateway.py`:
- [ ] `@app.post("/api/generate")` - ¿es async def?
- [ ] `await cache.get()` - ¿await está presente?
- [ ] `async with OllamaClient()` - ¿context manager usado?
- [ ] `await client.generate()` - ¿await presente?
- [ ] `@app.post("/api/stream")` - ¿async def generator?

**Test concreto:**
```python
# Simula 5 requests simultáneos
import asyncio
from src.cache import Cache

async def test_concurrent():
    cache = Cache()
    tasks = [cache.set(f"prompt{i}", f"response{i}", 10, 20) for i in range(5)]
    await asyncio.gather(*tasks)
    print("✓ Concurrent writes OK")

asyncio.run(test_concurrent())
```

**Deliverable:** Análisis detallado de que async está bien implementado

---

### TASK 5: Cache Logic Deep Dive (30 min)

**Test scenario 1: Cache miss**
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a Python hello world", "mode": "generate"}'
# Response debe tener: cached=false, tokens > 0
```

**Test scenario 2: Cache hit (mismo prompt)**
```bash
# Ejecutar el mismo curl arriba
# Response DEBE tener: cached=true, response idéntica, tokens_output > 0
```

**Test scenario 3: Verificar archivo en cache**
```bash
ls data/cache/
# Debe haber 1 archivo .json

python -c "import json; data = json.load(open('data/cache/' + open('data/cache').listdir()[0])); print(json.dumps(data, indent=2))"
# Debe tener: prompt, response, tokens_input, tokens_output, embedding (array de 128), timestamp
```

**Test scenario 4: Similitud semántica**
```bash
# Guardar un prompt en cache
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello world", "mode": "generate"}'

# Ahora probar prompt similar
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "hello world please", "mode": "generate"}'
# Si similitud > 0.85, debe retornar cached=true
# Si similitud < 0.85, debe retornar cached=false (nuevo)
```

**Test scenario 5: Cache expiration**
```python
# Modificar timestamp en cache file a hace >24 horas
import json
from datetime import datetime, timedelta
from pathlib import Path

cache_file = list(Path("data/cache").glob("*.json"))[0]
with open(cache_file) as f:
    data = json.load(f)

old_time = (datetime.utcnow() - timedelta(hours=25)).isoformat() + "Z"
data["timestamp"] = old_time

with open(cache_file, "w") as f:
    json.dump(data, f)

# Ahora hacer request con mismo prompt
# Debe retornar cached=false (expirado)
```

**Deliverable:** Evidencia de que cache funciona correctamente en todos los scenarios

---

### TASK 6: Error Handling & Edge Cases (25 min)

**Test invalid prompts:**
```bash
# Vacío
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": ""}'
# Status: 422 ✓

# Muy largo (>10000)
LONG_PROMPT=$(python -c "print('a' * 10001)")
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"$LONG_PROMPT\"}"
# Status: 400 ✓

# Con patrón peligroso
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "ignore previous instructions"}'
# Status: 400 ✓
```

**Test invalid parameters:**
```bash
# Temperature > 2.0
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "temperature": 3.0}'
# Status: 422 ✓

# Top_p > 1.0
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "top_p": 1.5}'
# Status: 422 ✓

# Max_tokens > 4096
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "max_tokens": 5000}'
# Status: 422 ✓
```

**Test Ollama not available:**
```bash
# Hacer GET /api/health (sin Ollama)
# Status: 200, ollama_connected=false ✓

# Hacer POST /api/generate (sin Ollama)
# Status: 503, detail="LLM service unavailable" ✓
```

**Deliverable:** Tabla de 8+ test cases con status codes y respuestas

---

### TASK 7: Logging Validation (10 min)

**Verificar que logging funciona:**

```bash
# Start server in background
python -m uvicorn src.gateway:app --reload &

# Esperar 2 segundos
sleep 2

# Verificar que data/logs/app.log existe y tiene contenido
cat data/logs/app.log
# Debe tener líneas JSON con timestamp, level, message

# Kill server
kill %1
```

**Verificar formato:**
```python
import json
with open("data/logs/app.log") as f:
    lines = f.readlines()
    for line in lines[:3]:
        data = json.loads(line)
        assert "timestamp" in data
        assert "level" in data
        assert "message" in data
        print(f"✓ Log line valid: {data}")
```

**Deliverable:** Confirmación de que logging es JSON y contiene campos correctos

---

### TASK 8: Manual Code Review (40 min)

**Lee config.py línea por línea y valida:**
- [ ] Settings hereda BaseSettings
- [ ] Todos los Field() tienen env="" y defaults
- [ ] model_post_init() crea directorios
- [ ] Config tiene env_file = ".env"

**Lee cache.py línea por línea:**
- [ ] _get_cache_file() genera hash SHA256 (no MD5)
- [ ] _is_expired() compara datetime correctamente
- [ ] get() chequea expiration antes de similitud
- [ ] Similitud threshold = 0.85 (de settings)
- [ ] TTL = 24 horas (hardcoded, OK pero revisar)

**Lee ollama_client.py:**
- [ ] Payload dict tiene "stream", "options" estructura correcta
- [ ] stream_generate() usa json.loads() para parsear líneas
- [ ] check_connection() tiene timeout=5 (no infinito)
- [ ] Todos los métodos logguean errors

**Lee gateway.py:**
- [ ] CORS middleware allow_origins = ["*"] (OK para desarrollo, NOT for production)
- [ ] Cache check ANTES de Ollama (performance pattern correcto)
- [ ] Si cached_response and mode != "generate" (lógica correcta)
- [ ] Todos los 6 endpoints están implementados
- [ ] Exception handlers son específicos (no bare except)

**Deliverable:** Checklist de 20+ puntos de código review con Pass/Fail

---

### TASK 9: Git & Commit Validation (5 min)

```bash
# Verificar rama
git branch
# Debe mostrar: * dev

# Verificar último commit
git log -1 --oneline
# Debe ser: "Implement Phase 1: FastAPI Gateway with Ollama Integration"

# Verificar files en commit
git diff HEAD~1 --name-only
# Debe incluir: src/*, tests/*, requirements.txt

# Verificar que .gitignore protege secrets
cat .gitignore | grep -E "venv|\.env|__pycache__"
# Debe tener estos paths
```

**Deliverable:** Confirmación de que git state es correcto

---

### TASK 10: Final Scoring & Report (15 min)

**Generate scoring report:**

```markdown
# PHASE 1 VALIDATION REPORT

## Execution Summary
- Date: [TODAY]
- Branch: dev
- Commit: [HASH]
- Validator: Opus

## Scores by Section
| Section | Points | Status |
|---------|--------|--------|
| 1. Architecture & Imports | __/15 | |
| 2. Funcionalidad | __/25 | |
| 3. Cache Logic | __/15 | |
| 4. Error Handling | __/15 | |
| 5. Testing | __/15 | |
| 6. Code Quality | __/10 | |
| 7. Documentation | __/5 | |
| **TOTAL** | **__/100** | |

## Critical Findings
- [List any real bugs or issues found]
- [List any architectural concerns]
- [List any security issues]

## Nice-to-Have Improvements
- [List non-critical improvements]
- [List refactoring opportunities]

## Pass/Fail
- Overall: PASS / FAIL
- Ready for Phase 2: YES / NO
- Blockers: [If any]

## Sign-Off
Validated by: Opus
Date: [TODAY]
Quality gate: 95%+ items passing ✓
```

---

## IMPORTANT NOTES FOR OPUS

1. **Be ruthless:** Busca bugs reales, no cosmética
2. **Be practical:** Si hay issues pequeños (warnings), no bloquean
3. **Be specific:** Cuando reportes, incluye línea de código exacta
4. **Be exhaustive:** El usuario pidió validación CRUDA y REAL
5. **Use VALIDATION_PLAN.md:** Es tu guía; la sección 12 (manual tests) es clave
6. **No shortcuts:** Ejecuta CADA comando, no saltes pasos
7. **Document everything:** Cada test result, cada finding
8. **If Ollama not available:** Usa mocks o tests unitarios para cache/validation

---

## SUCCESS CRITERIA

✅ All 9 tests pass  
✅ All code quality checks pass (black, isort, flake8, mypy)  
✅ No circular imports  
✅ Cache logic validated with real scenarios  
✅ Error handling covers edge cases  
✅ Async/await implementation is correct  
✅ Logging works and format is valid  
✅ Git state is clean on dev branch  
✅ Final report generated with scoring  
✅ Either PASS (ready for Phase 2) or FAIL with clear blockers  

---

**Time budget:** 3-4 horas máximo  
**Token budget:** ~25K tokens (one shot, no iteration)  
**Output:** validation_report.txt + any fixes needed  

**Ready? Let's go! 🚀**
