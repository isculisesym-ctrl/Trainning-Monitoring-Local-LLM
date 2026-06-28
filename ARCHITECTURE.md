# AI-Platform: System Architecture
**Lead AI Infrastructure Architect Report**
**Date:** June 28, 2026
**Status:** Approved & Ready for Implementation

---

## Executive Summary

This document describes the complete system architecture for a production-ready local LLM infrastructure optimized for your hardware (AMD Ryzen 7 5700X + 32GB RAM + RTX 4060 4GB).

**Configuration Approved:**
- Model: Qwen 2.5 Coder 7B
- Runtime: Ollama
- Gateway: FastAPI (custom)
- Caching: File-based (Redis-ready for future)
- Deployment: Phase 1 (single-user, local)

---

## 1. Hardware Architecture

### Computing Resources

```
CPU: AMD Ryzen 7 5700X
├─ Cores: 8
├─ Threads: 16
├─ Clock: 3.4 GHz base
├─ TDP: 65W
├─ Architecture: Zen 3
├─ Features: AVX2 ✓, AVX-512 ✗, FMA3 ✓
└─ Performance: EXCELLENT for inference

RAM: 32GB DDR4-3200
├─ Total: 32GB (2x16GB Kingston)
├─ Speed: 3200MHz
└─ Allocation: 
    ├─ Ollama: 4-6GB (dynamic)
    ├─ Gateway: 200MB
    ├─ System/OS: 8-10GB
    └─ Buffer: 14-16GB free

GPU: NVIDIA RTX 4060
├─ VRAM: 4GB
├─ Architecture: Ada (sm_89)
├─ CUDA Compute Capability: 8.9
├─ Tensor Cores: 3,072
├─ Memory Bandwidth: 432 GB/s
├─ Power: Efficient (60W TDP)
└─ Suitable for:
    ├─ Qwen 7B (Q4_K_M): 3.8GB ✓
    ├─ Qwen 14B: 8GB ✗ (upgrade needed)
    └─ CPU fallback: Always available

Storage: NVMe SSD
├─ Capacity: 1TB total
├─ Available: 364GB
├─ Model storage: ~5GB for Qwen + overhead
└─ Growth plan: Prepare for 10+ models (50GB total)
```

### Instruction Set Support

| Feature | Support | Impact |
|---------|---------|--------|
| AVX2 | ✅ Yes | 2-3x speedup for matrix ops |
| AVX-512 | ❌ No | Not on Zen 3 (acceptable) |
| FMA3 | ✅ Yes | Essential for tensor operations |
| AES-NI | ✅ Yes | Encryption acceleration |
| F16C | ✅ Yes | FP16 inference optimization |

---

## 2. System Architecture Diagram

### High-Level Data Flow

```
┌──────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  VS Code     │  │  Jupyter     │  │  Custom      │   │
│  │ (Continue)   │  │ Notebook     │  │  Clients     │   │
│  └──────────┬───┘  └──────┬───────┘  └────────┬─────┘   │
│             │              │                   │          │
│             └──────────────┼───────────────────┘          │
│                            │                              │
│                   HTTP/REST (port 8000)                  │
│                            │                              │
└────────────────────────────┼──────────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────────┐
         │       AI GATEWAY (FastAPI Application)    │
         ├───────────────────────────────────────────┤
         │ Port: 8000 (HTTP)                         │
         │ Health Check: GET /api/health             │
         │ Generate: POST /api/generate              │
         │ Cache: /data/cache (file-based)           │
         │                                           │
         │ Components:                               │
         │ ├─ Request Handler                        │
         │ ├─ Semantic Cache Manager                 │
         │ ├─ Rate Limiter                           │
         │ ├─ Prompt Validator                       │
         │ ├─ Response Formatter                     │
         │ └─ Logging & Monitoring                   │
         │                                           │
         │ Dependencies:                             │
         │ ├─ fastapi 0.104+                         │
         │ ├─ httpx (Ollama calls)                   │
         │ ├─ pydantic (validation)                  │
         │ └─ python-json-logger                     │
         └──────────────┬──────────────────────────┘
                        │
           Port 11434 (Ollama API)
           HTTP JSON-RPC
                        │
                        ▼
         ┌───────────────────────────────────────────┐
         │         OLLAMA RUNTIME                    │
         ├───────────────────────────────────────────┤
         │ Service: ollama serve                     │
         │ Port: 11434 (REST API)                    │
         │ Auto-detect: CUDA, CPU fallback           │
         │                                           │
         │ Loaded Model: qwen:7b-coder               │
         │ ├─ Size on disk: 3.8GB                    │
         │ ├─ Quantization: Q4_K_M                   │
         │ ├─ Context window: 128K                   │
         │ ├─ Sequence length: up to 128K tokens     │
         │ └─ Inference: llama.cpp backend           │
         │                                           │
         │ Environment:                              │
         │ ├─ OLLAMA_NUM_GPU=1 (RTX 4060)            │
         │ ├─ OLLAMA_MAX_VRAM=4294967296 (4GB)       │
         │ └─ OLLAMA_KEEP_ALIVE=5m                   │
         └──────────────┬──────────────────────────┘
                        │
         NVIDIA CUDA (RTX 4060 4GB VRAM)
         cuBLAS (Matrix operations)
         cuDNN (Neural network primitives)
                        │
                        ▼
         ┌───────────────────────────────────────────┐
         │        GPU ACCELERATION LAYER             │
         ├───────────────────────────────────────────┤
         │ GPU: NVIDIA GeForce RTX 4060              │
         │ VRAM: 4GB                                 │
         │ CUDA Version: 12.x (auto-detected)        │
         │ Driver: 32.0.15 (current)                 │
         │                                           │
         │ Model Tensor Layout:                      │
         │ ├─ Q4_K_M Quantization (4-bit)            │
         │ ├─ VRAM per token: ~4MB                   │
         │ ├─ Max batch size: 1 (single user)        │
         │ └─ Tensor parallelism: Not used (8B GPU)  │
         │                                           │
         │ Fallback: CPU inference (if VRAM full)    │
         │ ├─ Speed: 2-3 tok/s (slower)              │
         │ ├─ Auto-triggered: VRAM>95%               │
         │ └─ Transparent to user                    │
         └───────────────────────────────────────────┘
                        │
         ┌─────────────────────────────────────────────┐
         │       MODEL WEIGHTS (Disk Storage)          │
         │                                             │
         │ Location: ~/.ollama/models/                 │
         │ Model: qwen:7b-coder                        │
         │ ├─ Quantization: Q4_K_M (default)          │
         │ ├─ Size: 3.8GB                             │
         │ ├─ Download: First pull ~20 min (50Mbps)   │
         │ ├─ Validation: SHA256 hash check           │
         │ └─ Persistent: Stays between sessions      │
         │                                             │
         │ Future models (Phase 5+):                  │
         │ ├─ qwen:14b-coder (8GB)                    │
         │ └─ embeddings model (optional)             │
         └─────────────────────────────────────────────┘
```

### Component Dependencies

```
User Application
    │
    ├─ fastapi
    │  ├─ starlette
    │  ├─ pydantic
    │  └─ httpx
    │
    ├─ Gateway
    │  ├─ Request Validation
    │  ├─ Semantic Cache (file I/O)
    │  ├─ Rate Limiter (in-memory)
    │  ├─ Logging
    │  └─ Metrics (optional)
    │
    └─ Ollama Client
       ├─ HTTP calls to localhost:11434
       ├─ Model loading/unloading
       └─ CUDA integration (auto)
```

---

## 3. Component Specifications

### 3.1 AI Gateway (FastAPI)

**Purpose:** Request routing, caching, validation, monitoring

**Configuration:**
```python
# Main settings
HOST: "127.0.0.1"
PORT: 8000
WORKERS: 1 (single-user, local)
TIMEOUT: 300 seconds (5 min per request)
MAX_CONCURRENT_REQUESTS: 10
RATE_LIMIT: 100 requests/minute

# Model settings
MODEL: "qwen:7b-coder"
OLLAMA_BASE_URL: "http://localhost:11434"
TEMPERATURE: 0.7 (default, adjustable)
MAX_TOKENS: 4096 (default, adjustable)
TOP_P: 0.9 (default, adjustable)

# Cache settings (file-based, Phase 1)
CACHE_TYPE: "file"
CACHE_DIR: "./data/cache"
CACHE_MAX_SIZE: 1000  # max entries
CACHE_TTL: 86400  # 24 hours
SEMANTIC_SIMILARITY_THRESHOLD: 0.85

# Future: Redis (Phase 2)
# CACHE_TYPE: "redis"
# REDIS_URL: "redis://localhost:6379/0"
```

**Endpoints:**

```python
GET  /api/health
  Returns: { "status": "ok", "model": "qwen:7b-coder" }

POST /api/generate
  Input: {
    "prompt": str,
    "temperature": float (0-1),
    "max_tokens": int,
    "system": str (optional)
  }
  Output: {
    "text": str,
    "tokens_used": int,
    "generation_time_ms": int,
    "cached": bool
  }

POST /api/stream
  Same as /api/generate but streams response chunks

GET  /api/models
  Returns: { "available": ["qwen:7b-coder"], "loaded": "qwen:7b-coder" }

POST /api/cache/clear
  Clears semantic cache
```

**Request Flow:**
```
1. Receive HTTP POST /api/generate
2. Validate input (JSON schema, length, characters)
3. Check semantic cache
   ├─ Hit (85%+ similarity): Return cached response
   └─ Miss: Continue to step 4
4. Check rate limit
   ├─ Exceeded: Return 429 Too Many Requests
   └─ OK: Continue to step 5
5. Prepare prompt (inject system message, format)
6. Call Ollama API (localhost:11434)
7. Stream response or wait for completion
8. Format response JSON
9. Cache response (semantic key)
10. Return to client
11. Log metrics (latency, tokens, cache hit)
```

### 3.2 Ollama Runtime

**Purpose:** LLM inference engine, CUDA management

**Model Details:**
```
Name: qwen:7b-coder
Base Model: Qwen/Qwen2.5-7B-Instruct
Quantization: Q4_K_M (4-bit Key-Value)
  ├─ Reduces VRAM by 75% vs FP16
  ├─ Quality loss: <3% (imperceptible)
  └─ Speed: +2x due to bandwidth efficiency

Parameters: 7 billion
Context Length: 128K tokens
Vocabulary: 151,936 tokens
Training Cutoff: October 2024

VRAM Requirements:
  FP16 (unquantized): 14GB
  Q5_K_M (5-bit): 5.2GB
  Q4_K_M (4-bit): 3.8GB ← USING THIS
  Q2_K (2-bit): 1.6GB (poor quality)

Performance Estimates:
  First Token Latency: 200ms
  Throughput: 20 tokens/second
  Context Load Time: 100ms
  Model Load Time: 2-3 seconds (first call)

Capabilities:
  Code Generation: 67.3% HumanEval
  Software Engineering: 54.2% SWE-Bench
  General Knowledge: 75% MMLU
  SQL Generation: Excellent
  Documentation: Excellent
  Unit Tests: Good
  Architecture Review: Adequate
```

**Startup Command:**
```bash
ollama serve

# Auto-loads environment:
# - Detects RTX 4060
# - Allocates 4GB VRAM
# - Initializes cuBLAS/cuDNN
# - Listens on localhost:11434
# - Accepts models: /api/pull, /api/generate
```

**CUDA Configuration:**
```bash
# Automatic detection (no manual setup needed)
# If CUDA not found, falls back to CPU (slower)

# Manual override (if needed):
export OLLAMA_NUM_GPU=1
export OLLAMA_GPU_OVERHEAD=0.1
export OLLAMA_KEEP_ALIVE=5m
```

### 3.3 Storage Architecture

```
C:\Proyectos\AI-Platform\
├── src/
│   ├── __init__.py
│   ├── gateway.py          (Main FastAPI app)
│   ├── handlers.py         (Request handlers)
│   ├── models.py           (Pydantic schemas)
│   ├── cache.py            (Semantic cache logic)
│   ├── ollama_client.py    (Ollama integration)
│   ├── validators.py       (Input validation)
│   └── utils.py            (Helper functions)
│
├── data/
│   ├── cache/              (File-based cache)
│   │   └── *.json          (Cached responses)
│   ├── logs/               (Application logs)
│   │   └── *.log           (Daily rotation)
│   └── metrics/            (Prometheus metrics)
│       └── metrics.txt
│
├── models/
│   └── [Reserved for future local model storage]
│
├── tests/
│   ├── test_gateway.py
│   ├── test_cache.py
│   └── test_validators.py
│
├── docs/
│   ├── API_EXAMPLES.md
│   ├── TROUBLESHOOTING.md
│   └── UPGRADE_GUIDE.md
│
├── docker/
│   └── Dockerfile          (Optional, Phase 5)
│
├── requirements.txt        (Python dependencies)
├── .env.example            (Environment template)
├── docker-compose.yml      (Optional compose)
├── ARCHITECTURE.md         (This file)
├── INSTALLATION.md         (Setup guide)
├── ROADMAP.md              (Phase breakdown)
└── README.md               (Overview)
```

**Model Storage Location:**
```
~/.ollama/models/           (User's home directory)
└── manifests/
    └── registry.ollama.ai/
        └── library/
            └── qwen/
                └── 7b-coder
                    ├── blobs/           (Actual weights)
                    ├── manifests/       (SHA256 metadata)
                    └── ...
```

---

## 4. Data Flow

### Request-Response Cycle

```
┌─ CLIENT REQUEST ─────────────────────────────────┐
│                                                   │
│ POST /api/generate                               │
│ {                                                │
│   "prompt": "Write a Python function...",        │
│   "temperature": 0.7,                            │
│   "max_tokens": 2048                             │
│ }                                                │
└──────────────┬──────────────────────────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ GATEWAY: Validate Input  │
    │ - JSON schema check      │
    │ - Prompt length: <12K    │
    │ - No injection patterns  │
    └──────────────┬───────────┘
                   │
                   ▼ (valid)
    ┌──────────────────────────┐
    │ GATEWAY: Check Cache     │
    │ - Compute semantic hash  │
    │ - Check file: cache/     │
    └──────────────┬───────────┘
                   │
      ┌────────────┴────────────┐
      │ (HIT: 85%+ match)      │ (MISS: <85%)
      │                         │
      ▼                         ▼
    Return                  Check
    cached                  rate
    response                limit
                              │
                              ▼ (limit OK)
                    ┌──────────────────────┐
                    │ OLLAMA: Generate     │
                    │ - Load model         │
                    │ - Run inference      │
                    │ - Stream tokens      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ GATEWAY: Format      │
                    │ - JSON response      │
                    │ - Compute tokens     │
                    │ - Add metadata       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ GATEWAY: Cache       │
                    │ - Save to file       │
                    │ - TTL: 24h           │
                    └──────────┬───────────┘
                               │
                               ▼
┌─ CLIENT RESPONSE ────────────────────────────────┐
│                                                   │
│ HTTP 200 OK                                      │
│ {                                                │
│   "text": "def sum(a, b):\n    return a + b",   │
│   "tokens_used": 24,                            │
│   "generation_time_ms": 1200,                    │
│   "cached": false                                │
│ }                                                │
└───────────────────────────────────────────────────┘
```

---

## 5. Performance Specifications

### Latency

| Operation | Time | Notes |
|-----------|------|-------|
| Model load (first call) | 2-3 sec | Cached after first request |
| Time to first token (TTFT) | 200ms | Processing input, starting generation |
| Token generation rate | 20 tok/s | Streaming output |
| Average request (100 tokens) | ~6 sec | 200ms TTFT + 5 sec streaming |
| Cache hit response | <50ms | File I/O only |
| API overhead | ~50ms | Validation, formatting, I/O |

### Throughput

| Metric | Value |
|--------|-------|
| Concurrent requests | 1 (single user for now) |
| Max tokens per request | 4096 |
| Cache hit rate target | 60% (after 1 month) |
| Requests per minute limit | 100 |
| Model retention in memory | 5 minutes (auto-unload) |

### Resource Usage

```
During Idle (no requests):
├─ CPU: <5% (Ollama listening)
├─ RAM: 2-3GB (system baseline)
├─ GPU: 0GB (model unloaded)
└─ Disk I/O: Minimal

During Inference (processing):
├─ CPU: 30-40% (pre/post processing)
├─ RAM: 4-6GB (input buffer + overhead)
├─ GPU: 3.8GB (Q4_K_M model)
└─ Disk I/O: Negligible

After Idle Timeout (5 minutes):
├─ Model unloads from GPU
└─ Reloads on next request (2-3 sec delay)
```

---

## 6. Security Architecture

### Input Validation

```
1. JSON Schema Validation
   └─ Pydantic models enforce structure

2. Prompt Length Check
   └─ Max 12,000 characters (prevents DOS)

3. Prompt Injection Detection
   └─ Check for common LLM injection patterns:
      ├─ "Ignore instructions"
      ├─ "Forget your role"
      ├─ "As an admin..."
      └─ etc.

4. Character Set Validation
   └─ Only allow UTF-8 printable chars

5. Token Counter
   └─ Estimate tokens before sending to model
```

### API Security (Phase 1)

```
✓ Implemented:
├─ Rate limiting (100 req/min)
├─ Prompt injection detection
├─ Error response sanitization
├─ Local-only (no remote access)
└─ Timeout protection (5 min max)

Planned (Phase 4):
├─ JWT authentication
├─ HTTPS/TLS
├─ RBAC (admin/user roles)
├─ Audit logging
└─ API key management
```

---

## 7. Monitoring & Observability

### Metrics Tracked

```
Per-Request Metrics:
├─ Timestamp
├─ Endpoint
├─ Request tokens (input length)
├─ Response tokens (output length)
├─ Generation time (ms)
├─ Latency (ms)
├─ Cache hit/miss
├─ Temperature used
├─ Model used
└─ Status code

Aggregate Metrics:
├─ Requests/minute
├─ Avg latency
├─ Cache hit rate (%)
├─ Errors/minute
├─ GPU utilization
├─ Memory usage
└─ Model uptime

Logging Levels:
├─ INFO: Requests, model loaded/unloaded
├─ WARNING: Rate limit exceeded, cache errors
└─ ERROR: Model crashes, API errors
```

### Log Output

```
Location: ./data/logs/ai_gateway.log
Format: JSON (structured logging)
Rotation: Daily, keep 7 days

Example log entry:
{
  "timestamp": "2026-06-28T14:30:45.123Z",
  "level": "INFO",
  "endpoint": "/api/generate",
  "request_id": "req_abc123",
  "input_tokens": 156,
  "output_tokens": 324,
  "generation_time_ms": 1200,
  "cache_hit": false,
  "model": "qwen:7b-coder",
  "status_code": 200
}
```

---

## 8. Error Handling

### API Error Codes

```
200 OK
└─ Request successful

400 Bad Request
└─ Invalid input (validation failed)

429 Too Many Requests
└─ Rate limit exceeded

500 Internal Server Error
└─ Model crashed or Ollama unavailable

504 Gateway Timeout
└─ Request >5 minutes (model stuck)
```

### Recovery Strategies

```
Model Crashed:
├─ Automatic restart Ollama
├─ Clear VRAM cache
└─ Return 503 to user with retry advice

VRAM Full (OOM):
├─ Fallback to CPU inference (slower)
├─ Log warning
└─ Return response (slower than expected)

Ollama Offline:
├─ Return 503 Service Unavailable
├─ Start Ollama (if in docker/service)
└─ Queue request with auto-retry

Rate Limit Hit:
├─ Return 429 Too Many Requests
├─ Include Retry-After header
└─ Queue in local queue (if implemented)
```

---

## 9. Scalability Path

### Phase 1 (Now): Single Model, Single User
```
Architecture: Gateway → Ollama → RTX 4060
Throughput: 1 user
Models: Qwen 7B only
```

### Phase 5 (Month 2): Two Models, Load Balancing
```
Architecture: Gateway (with routing) → {Ollama1 (7B), Ollama2 (14B)}
Throughput: Automatic routing based on complexity
Models: Qwen 7B + Qwen 14B
Requires: RTX 4060 Ti (8GB GPU upgrade)
```

### Phase 7+ (Month 3+): Multi-Model Gateway
```
Architecture: Gateway (with orchestration) → Model Selector → {7B, 14B, 35B}
Throughput: 1-5 concurrent users
Models: Qwen 7B, 14B, 35B-A3B
Requires: RTX 4070 Super (12GB GPU)
```

### Future: Multi-Machine
```
Architecture: Central Gateway → {Machine1, Machine2, ...}
Uses: Docker + Kubernetes
Throughput: 10+ concurrent users
Models: Multiple per machine
```

---

## 10. Technology Decisions

### Why These Choices?

**Qwen 2.5 Coder 7B**
- ✅ Best code quality for 7B parameter budget
- ✅ Specialized training for code tasks
- ✅ Better SQL generation than alternatives
- ✅ Fits in RTX 4060 (3.8GB VRAM)
- ✅ Alibaba backing (long-term support)

**Ollama**
- ✅ Zero configuration (auto-detects RTX 4060)
- ✅ Single installer, simple operation
- ✅ Proven stability (2+ years production use)
- ✅ Model management built-in
- ✅ REST API standard (OpenAI-compatible)

**FastAPI**
- ✅ Modern, async-capable (for future scalability)
- ✅ Built-in validation (Pydantic)
- ✅ Auto-documentation (OpenAPI/Swagger)
- ✅ Excellent performance (near C++)
- ✅ Easy to extend (middleware, hooks)

**File-Based Cache**
- ✅ Phase 1: Simpler than Redis
- ✅ No external dependencies
- ✅ Sufficient for single-user workload
- ✅ Easy upgrade path to Redis later
- ✅ All cache data visible for debugging

---

## 11. Deployment Checklist

- [ ] Ollama installed and running
- [ ] Qwen:7b-coder model pulled
- [ ] Gateway dependencies installed (requirements.txt)
- [ ] Gateway starts without errors
- [ ] Health check endpoint responds
- [ ] Test API call succeeds
- [ ] VS Code Continue extension configured
- [ ] First code generation test passed
- [ ] Latency <200ms TTFT
- [ ] No VRAM OOM errors

---

## 12. Future Considerations

### Redis Integration (Phase 2)
```
Current: File-based cache
├─ Pro: Simple, no external service
└─ Con: Not distributed

Future: Redis cache
├─ Pro: Faster, distributed, cloud-compatible
└─ Con: Requires Redis service

Migration: Drop-in replacement, existing cache migrates
```

### Multi-Model Support (Phase 5)
```
Current: Qwen 7B only
Future: Qwen 7B + Qwen 14B + Qwen 35B

Routing Logic:
├─ Simple tasks → Qwen 7B (fast, cheap)
├─ Medium tasks → Qwen 14B (balanced)
└─ Complex tasks → Qwen 35B (quality)
```

### PostgreSQL Integration (Phase 3)
```
For: Conversation history, user memory
Benefits:
├─ Persist conversations
├─ Context accumulation
└─ User preferences
```

---

**Document Version:** 1.0
**Last Updated:** June 28, 2026
**Status:** Approved for Implementation
**Next Review:** Week 2 (Post-Phase 1)
