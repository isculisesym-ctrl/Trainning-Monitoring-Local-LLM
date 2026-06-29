# Phase 1 Validation Plan - Exhaustive & Real

**Objetivo:** Validación cruda y exhaustiva del trabajo implementado en Phase 1. No superficial, sino deep dive en todos los aspectos técnicos, arquitectónicos y funcionales.

**Estado al inicio de validación:**
- Rama: `dev`
- Último commit: "Implement Phase 1: FastAPI Gateway with Ollama Integration"
- Tests: 9/9 PASSED
- Archivos creados: 13 (8 src + 3 tests + 2 init)

---

## SECCIÓN 1: VALIDACIÓN DE ARQUITECTURA

### 1.1 - Estructura del Código

**Verificar:**
- [ ] Todos los módulos siguen patrón correcto (imports, responsabilidades únicas)
- [ ] No hay imports circulares que rompan el código
- [ ] Las dependencias entre módulos son unidireccionales (DAG)
- [ ] El orden de imports es correcto (stdlib → third-party → local)

**Checklist detallado:**
```python
# config.py debe ser importable primero (no depende de nada)
# utils.py puede importar config (y es importado por casi todo)
# models.py debe ser limpio (solo Pydantic, sin lógica)
# validators.py importa models y config (correcto)
# cache.py importa config y utils (correcto)
# ollama_client.py importa config (correcto)
# gateway.py es el que junta todo (imports finales)
```

**Test:**
```bash
python -c "from src.config import settings; print('✓ config imports OK')"
python -c "from src import gateway; print('✓ all imports OK')"
python -c "import src.gateway; print('✓ no circular imports')"
```

### 1.2 - Responsabilidades de Cada Módulo

**config.py:**
- [ ] Settings válida todos los parámetros con Pydantic
- [ ] Crea directorios automáticamente (data/cache, data/logs)
- [ ] Carga desde .env si existe, sino usa defaults
- [ ] No contiene lógica de negocio (SOLO config)

**models.py:**
- [ ] GenerateRequest valida min_length=1, max_length=10000 para prompt
- [ ] GenerateRequest acepta mode válido (generate, stream, cached)
- [ ] GenerateResponse incluye todos los campos: id, prompt, response, tokens, mode, cached
- [ ] HealthResponse tiene enum estricto para status (healthy, degraded, unhealthy)
- [ ] ModelInfo tiene structure correcta para metadata de modelos
- [ ] No hay lógica más allá de Pydantic validation

**validators.py:**
- [ ] validate_prompt() limpia whitespace y detecta patrones peligrosos
- [ ] validate_temperature() normaliza a 2 decimales
- [ ] validate_generate_request() aplica defaults de config cuando son None
- [ ] Todas las excepciones son ValidationError (consistente)

**utils.py:**
- [ ] setup_logging() crea archivo data/logs/app.log
- [ ] simple_embedding() genera exactamente 128 dimensiones
- [ ] cosine_similarity() maneja edge cases (mag=0)
- [ ] hash_text() usa SHA256 (no MD5)
- [ ] generate_id() usa UUID4 truncado (8 caracteres)

**cache.py:**
- [ ] TTL = 24 horas (verificar hardcoded)
- [ ] Similitud threshold = 0.85 (configurable desde settings)
- [ ] Cache files en data/cache/*.json
- [ ] Expiration check es correcto (UTC datetime comparison)
- [ ] get() retorna None si not found O expired O low similarity
- [ ] set() calcula embedding con simple_embedding()

**ollama_client.py:**
- [ ] Timeout = 300 segundos (5 min, configurable)
- [ ] check_connection() usa GET /api/tags
- [ ] generate() soporta stream=True/False
- [ ] stream_generate() es AsyncGenerator (yield por chunk)
- [ ] get_models() retorna lista de modelos
- [ ] Todos los métodos async (no bloquean)
- [ ] Context manager (__aenter__, __aexit__) cierra conexión

**gateway.py:**
- [ ] FastAPI app con título y descripción
- [ ] CORS permitido (allow_origins=["*"])
- [ ] Startup/shutdown handlers loguean eventos
- [ ] POST /api/generate valida request y maneja excepciones
- [ ] Cache check ANTES de llamar a Ollama
- [ ] POST /api/stream retorna StreamingResponse (SSE)
- [ ] GET /api/health retorna status + connección estado
- [ ] DELETE /api/cache limpia archivos
- [ ] GET /api/cache/stats retorna conteo
- [ ] Global exception handler captura todo

---

## SECCIÓN 2: VALIDACIÓN FUNCIONAL

### 2.1 - Comportamiento de Endpoints

**GET /api/health**
```bash
# Expected behavior:
# - Status: "healthy" si Ollama conecta + cache existe
# - Status: "degraded" si uno falla
# - Status: "unhealthy" si ambos fallan
# - Respuesta 200 siempre (no 503)
```

**POST /api/generate**
```bash
# Flujo correcto:
# 1. Valida request (ValidationError → 400)
# 2. Intenta cache.get(prompt)
# 3. Si hit + mode != "generate" → retorna cached
# 4. Si miss → llama ollama_client.generate()
# 5. Guarda en cache con await cache.set()
# 6. Retorna GenerateResponse completa

# Edge cases a probar:
# - Prompt vacío → 422 (Pydantic)
# - Prompt > 10000 chars → 400 (ValidationError)
# - Prompt con "ignore previous" → 400 (ValidationError)
# - Ollama no disponible → 503
# - Cache hit exacto → modo "cached"
# - Cache similar (>0.85 similarity) → modo "cached"
# - Cache disimilar (<0.85 similarity) → modo "generate"
```

**POST /api/stream**
```bash
# Debe ser SSE (Server-Sent Events)
# Content-Type: text/event-stream
# Formato: data: {json}\n\n
# Streaming real (no buffering)
# Async generator (no bloquea)
```

**GET /api/models**
```bash
# Si Ollama conecta: 200 + lista de modelos
# Si Ollama no conecta: 503
# Nunca 404 o 400
```

**DELETE /api/cache**
```bash
# Borra todos los *.json en data/cache/
# Retorna 200
# Siguiente cache.get() retorna None
```

**GET /api/cache/stats**
```bash
# Retorna: {total_entries, cache_dir, ttl_hours}
# total_entries = count de *.json files
# Funciona aunque cache esté vacío
```

### 2.2 - Flujo de Cache

**Scenario 1: Primer request**
```
request("Write hello") 
→ cache.get() = None 
→ ollama_client.generate() 
→ cache.set() 
→ response.cached = False
```

**Scenario 2: Request idéntico**
```
request("Write hello")  [again]
→ cache.get() 
→ embedding match > 0.85 
→ return cached
→ response.cached = True
→ response.mode = "cached"
```

**Scenario 3: Request similar (>0.85 similarity)**
```
request("Please write a hello")  [similar a "Write hello"]
→ cache.get() 
→ check embedding similarity 
→ if > 0.85: return cached
→ else: call ollama
```

**Scenario 4: Cache expirado (>24h)**
```
prompt data: timestamp = 1 día ago + 23h
→ cache.get()
→ check _is_expired() 
→ True → unlink file 
→ return None
→ call ollama (nuevo)
```

### 2.3 - Validación de Parámetros

**Temperature:**
- [ ] Input range: 0.0 - 2.0 (Pydantic valida)
- [ ] Default: 0.7 (desde settings)
- [ ] Normaliza a 2 decimales
- [ ] Se pasa correctamente a Ollama payload

**Top P:**
- [ ] Input range: 0.0 - 1.0 (Pydantic valida)
- [ ] Default: 0.9 (desde settings)
- [ ] Se pasa correctamente a Ollama payload

**Max Tokens:**
- [ ] Input range: 1 - 4096 (Pydantic valida)
- [ ] Default: 2048 (desde settings)
- [ ] Se convierte a "num_predict" en Ollama

**Prompt:**
- [ ] min_length: 1 (Pydantic)
- [ ] max_length: 10000 (Pydantic)
- [ ] Limpia whitespace extremo
- [ ] Rechaza "ignore previous", "system prompt", "jailbreak"

---

## SECCIÓN 3: VALIDACIÓN DE TESTING

### 3.1 - Test Suite Coverage

**test_gateway.py:**
- [ ] test_health_check: Verifica status in [healthy, degraded, unhealthy]
- [ ] test_generate_invalid_prompt: Rechaza prompt vacío con 422
- [ ] test_generate_request_model: Pydantic valida tipos correctamente
- [ ] test_models_endpoint: Status code in [200, 503]

**test_cache.py:**
- [ ] test_cache_set_get: set() → get() = mismo contenido
- [ ] test_cache_not_found: get() nonexistent = None
- [ ] test_cache_clear: clear() → get() = None

**test_ollama_client.py:**
- [ ] test_ollama_client_init: default model = "qwen:7b-coder"
- [ ] test_ollama_connection_check: retorna bool (no error)

**Gaps a considerar:**
- [ ] No hay test de stream_generate() (funcionalidad asincrónica compleja)
- [ ] No hay test de cache expiration (temporal)
- [ ] No hay test de Ollama error handling (necesita mock)
- [ ] No hay test de embedding similarity (lógica de cache)
- [ ] No hay test de concurrent requests (race conditions)

### 3.2 - Test Execution

```bash
# Debe correr sin error
pytest tests/ -v --asyncio-mode=auto

# Debe retornar 9 passed, 0 failed
# Puede haber warnings sobre deprecated Pydantic config (OK)
```

---

## SECCIÓN 4: VALIDACIÓN DE CÓDIGO QUALITY

### 4.1 - Linting & Formatting

**Black (code formatting):**
```bash
black src/ tests/ --check
# Debe pasar sin cambios (sintaxis homogénea)
```

**isort (import sorting):**
```bash
isort src/ tests/ --check-only
# Debe pasar sin cambios (imports ordenados)
```

**flake8 (style & errors):**
```bash
flake8 src/ tests/ --max-line-length=120
# Debe pasar sin errores (PEP8 compliance)
```

**mypy (type checking):**
```bash
mypy src/ --ignore-missing-imports
# Debe pasar (type hints correctos)
# OK si retorna 0 errors
```

### 4.2 - Code Smell Checks

**Verificar:**
- [ ] No hay print() statements (solo logging)
- [ ] No hay hardcoded secrets (.env.example como guía)
- [ ] No hay TODOs pendientes sin contexto
- [ ] No hay funciones >50 líneas (demasiado complejas)
- [ ] No hay variables sin usar
- [ ] No hay imports no usados
- [ ] No hay excepciones bare (except:)

---

## SECCIÓN 5: VALIDACIÓN DE CONFIGURACIÓN

### 5.1 - Environment Variables

**Verificar que settings.py carga:**
```
GATEWAY_HOST, GATEWAY_PORT, DEBUG, LOG_LEVEL
OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT
TEMPERATURE, TOP_P, MAX_TOKENS
CACHE_TYPE, CACHE_MAX_SIZE, SEMANTIC_SIMILARITY_THRESHOLD, CACHE_DIR
RATE_LIMIT_REQUESTS, RATE_LIMIT_PERIOD
PROMETHEUS_ENABLED
```

**Verificar defaults (si no hay .env):**
- [ ] gateway_host = "127.0.0.1"
- [ ] gateway_port = 8000
- [ ] ollama_model = "qwen:7b-coder"
- [ ] temperature = 0.7
- [ ] semantic_similarity_threshold = 0.85
- [ ] cache_dir = "data/cache"

### 5.2 - Directory Creation

**Verificar que al iniciar settings:**
```bash
python -c "from src.config import settings; import os; assert os.path.exists('data/cache'); assert os.path.exists('data/logs')"
```

**Estructura esperada:**
```
data/
├── cache/        (vacío al inicio)
├── logs/         (vacío al inicio)
└── templates/    (vacío al inicio, para Phase 3)
```

---

## SECCIÓN 6: VALIDACIÓN DE ASYNC/CONCURRENCY

### 6.1 - Async Correctness

**Verificar en cache.py:**
- [ ] get() es async
- [ ] set() es async
- [ ] clear() es async
- [ ] get_stats() es async

**Verificar en ollama_client.py:**
- [ ] __aenter__ y __aexit__ son async
- [ ] check_connection() es async
- [ ] generate() es async
- [ ] stream_generate() es AsyncGenerator
- [ ] get_models() es async
- [ ] Usa httpx.AsyncClient (no requests)

**Verificar en gateway.py:**
- [ ] Todos los endpoints son async def
- [ ] await usado correctamente en cache.get(), cache.set()
- [ ] await usado correctamente en ollama_client.generate()
- [ ] async for usado en stream_generate()

### 6.2 - Resource Management

**Verificar OllamaClient context manager:**
```python
async with OllamaClient() as client:
    result = await client.generate(...)
# client debe cerrarse automáticamente
```

**Verificar que no hay connection leaks:**
- [ ] AsyncClient se crea en __aenter__
- [ ] AsyncClient se cierra en __aexit__
- [ ] check_connection() crea su propio client temporal
- [ ] No hay clients globales sin cerrar

---

## SECCIÓN 7: VALIDACIÓN DE ERRORES & EDGES

### 7.1 - Error Handling

**En gateway.py, endpoint /api/generate:**
- [ ] ValidationError → HTTPException(400, detail)
- [ ] OllamaClientError → HTTPException(503, detail)
- [ ] Generic Exception → HTTPException(500, detail)
- [ ] Global exception handler captura todo

**En cache.py:**
- [ ] JSON read errors → return None
- [ ] File delete errors → log pero no raise
- [ ] Embedding calculation errors → graceful fallback

**En ollama_client.py:**
- [ ] httpx.HTTPError → OllamaClientError
- [ ] Timeout errors → handled
- [ ] Connection refused → handled

### 7.2 - Edge Cases

**Prompt validation:**
- [ ] "" (vacío) → ValidationError
- [ ] "   " (solo espacios) → ValidationError
- [ ] > 10000 chars → ValidationError
- [ ] Con newlines/tabs → limpia a espacios simples

**Cache:**
- [ ] cache.get() con file corrupto → return None
- [ ] cache.set() sin permisos → log error, no crash
- [ ] cache_dir no existe → mkdir (model_post_init)

**Ollama:**
- [ ] No conecta → check_connection() = False
- [ ] Modelo no existe → error en generate()
- [ ] Timeout 300s → httpx timeout

---

## SECCIÓN 8: VALIDACIÓN DE LOGGING

### 8.1 - Logging Setup

**Verificar:**
- [ ] setup_logging() crea data/logs/app.log
- [ ] Formato JSON: {"timestamp": ..., "level": ..., "message": ...}
- [ ] Log level configurable desde settings
- [ ] Logger name = "ai_platform"

### 8.2 - Log Messages

**Debe loguear:**
- [ ] startup_event: "AI-Platform Gateway starting..."
- [ ] shutdown_event: "AI-Platform Gateway shutting down..."
- [ ] cache hit: "Cache hit with X.XX similarity"
- [ ] cache.set(): "Cached response for prompt hash ..."
- [ ] cache.clear(): "Cache cleared"
- [ ] Errores con contexto

**NO debe loguear (seguridad):**
- [ ] Prompts completos (datos sensibles)
- [ ] Respuestas completas (datos sensibles)
- [ ] Tokens de autenticación (si hubiera)

---

## SECCIÓN 9: VALIDACIÓN DE DEPENDENCIES

### 9.1 - requirements.txt

**Verificar:**
- [ ] FastAPI==0.104.1
- [ ] uvicorn[standard]==0.24.0
- [ ] pydantic==2.5.0
- [ ] pydantic-settings==2.1.0
- [ ] httpx==0.25.2
- [ ] pytest==7.4.3
- [ ] pytest-asyncio==0.21.1
- [ ] Todas las librerías tienen pinned versions

**Verificar instalación:**
```bash
pip list | grep -E "fastapi|pydantic|httpx|uvicorn"
# Todas deben estar presentes con versiones correctas
```

---

## SECCIÓN 10: VALIDACIÓN DE DOCUMENTACIÓN

### 10.1 - Docstrings

**Verificar cada función:**
- [ ] cache.py: get(), set(), clear(), get_stats()
- [ ] ollama_client.py: generate(), stream_generate(), get_models()
- [ ] gateway.py: todos los endpoints
- [ ] validators.py: validate_prompt(), validate_temperature()

**Standard:**
```python
async def get(self, prompt: str) -> Optional[Dict[str, Any]]:
    """Una línea corta si es simple
    
    Multipárrafo solo si complejo:
    - Descripción clara
    - Retorna...
    - Raises...
    """
```

### 10.2 - Type Hints

**Verificar completitud:**
- [ ] Todos los parámetros tienen hints
- [ ] Todos los retornos tienen hints
- [ ] Async functions retornan Awaitable o específico
- [ ] Optional usado cuando retorna None

---

## SECCIÓN 11: VALIDACIÓN DE GIT

### 11.1 - Commit & Branch

**Verificar:**
- [ ] Branch es "dev" (no master)
- [ ] Último commit mensaje describe cambios (no vacío)
- [ ] Commit tiene autor correcto
- [ ] .gitignore protege secrets (venv/, .env, __pycache__)

**Verificar files en commit:**
```bash
git diff HEAD~1 --name-only
# Debe incluir: src/*, tests/*, requirements.txt
# NO debe incluir: venv/, .env, __pycache__
```

---

## SECCIÓN 12: MANUAL SMOKE TESTS

**Si Ollama está disponible:**

```bash
# 1. Health check
curl http://localhost:8000/api/health

# 2. Generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello world", "mode": "generate"}'

# 3. Models
curl http://localhost:8000/api/models

# 4. Cache stats (debe estar vacío)
curl http://localhost:8000/api/cache/stats

# 5. Cache hit test (mismo prompt dos veces)
# Primera vez: cached=False
# Segunda vez: cached=True
```

**Si Ollama NO está disponible:**
- [ ] /api/health retorna degraded
- [ ] /api/generate retorna 503 (LLM service unavailable)
- [ ] /api/models retorna 503

---

## SCORING RÚBRICA

| Aspecto | Peso | Verificado | Status |
|---------|------|-----------|--------|
| Arquitectura & Imports | 15% | | |
| Funcionalidad Endpoints | 25% | | |
| Cache Logic | 15% | | |
| Error Handling | 15% | | |
| Testing | 15% | | |
| Code Quality | 10% | | |
| Documentation | 5% | | |
| **TOTAL** | **100%** | | **?/100** |

---

## INSTRUCCIONES PARA VALIDATOR (OPUS)

1. **Lee completamente** este documento (todas las 12 secciones)
2. **Crea un checklist ejecutable** con comandos bash/python específicos
3. **Ejecuta TODOS los tests** (pytest)
4. **Corre linting tools** (black, isort, flake8, mypy)
5. **Revisa manualmente** los puntos críticos (async/await, error handling)
6. **Prueba endpoints** (curl o cliente HTTP)
7. **Valida edge cases** (prompts vacíos, caracteres especiales, etc.)
8. **Verifica git state** (branch, commits, archivos staged)
9. **Genera reporte** con resultado de CADA punto
10. **Asigna score final** basado en rúbrica

---

**Plan Status:** Ready for validation
**Target Validator:** Opus (fresh chat)
**Expected Duration:** 2-3 hours (exhaustive validation)
**Acceptable Pass Rate:** 95%+ (algunos warnings OK)
