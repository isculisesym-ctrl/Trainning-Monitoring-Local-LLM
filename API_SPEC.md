# API Specification: AI-Platform
**RESTful API for Local LLM Gateway**

---

## Base URL

```
http://localhost:8000
```

---

## Authentication

**Phase 1:** None (local-only, no auth)
**Phase 4:** JWT tokens (to be added)

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /api/health`

**Purpose:** Verify API and model are running

**Request:**
```bash
curl http://localhost:8000/api/health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "model": "qwen:7b-coder",
  "ollama_version": "0.1.x",
  "timestamp": "2026-06-28T14:30:45Z"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "error",
  "message": "Ollama not responding",
  "model": null
}
```

---

### 2. Generate Text

**Endpoint:** `POST /api/generate`

**Purpose:** Generate code, documentation, or text

**Request:**
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to validate email",
    "temperature": 0.7,
    "max_tokens": 2048,
    "system": "You are a helpful code assistant"
  }'
```

**Request Schema:**
```json
{
  "prompt": "string (required, 1-12000 chars)",
  "temperature": "float (optional, 0-1, default 0.7)",
  "max_tokens": "integer (optional, 1-4096, default 2048)",
  "top_p": "float (optional, 0-1, default 0.9)",
  "system": "string (optional, system message)",
  "stream": "boolean (optional, default false)"
}
```

**Response (200 OK):**
```json
{
  "text": "def validate_email(email: str) -> bool:\n    import re\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n    return re.match(pattern, email) is not None",
  "tokens_used": 45,
  "generation_time_ms": 2340,
  "cached": false,
  "model": "qwen:7b-coder",
  "stop_reason": "length"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "prompt_too_long",
  "message": "Prompt exceeds 12000 character limit",
  "details": {
    "provided": 15000,
    "max": 12000
  }
}
```

**Response (429 Too Many Requests):**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit: 100 requests per minute",
  "retry_after": 45
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "model_error",
  "message": "Model inference failed",
  "details": "CUDA out of memory"
}
```

---

### 3. Stream Response

**Endpoint:** `POST /api/stream`

**Purpose:** Stream response tokens as they're generated

**Request:**
```bash
curl -X POST http://localhost:8000/api/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a function"}'

# Returns Server-Sent Events (SSE)
```

**Response (text/event-stream):**
```
data: {"token": "def", "tokens_generated": 1}
data: {"token": " add", "tokens_generated": 2}
data: {"token": "(", "tokens_generated": 3}
data: {"token": "a", "tokens_generated": 4}
data: {"token": ",", "tokens_generated": 5}
...
data: {"done": true, "total_tokens": 45, "time_ms": 2340}
```

---

### 4. List Models

**Endpoint:** `GET /api/models`

**Purpose:** List available models

**Request:**
```bash
curl http://localhost:8000/api/models
```

**Response (200 OK):**
```json
{
  "available": [
    {
      "name": "qwen:7b-coder",
      "size": "3.8 GB",
      "quantization": "Q4_K_M",
      "loaded": true
    },
    {
      "name": "qwen:14b-coder",
      "size": "8 GB",
      "quantization": "Q4_K_M",
      "loaded": false
    }
  ],
  "current": "qwen:7b-coder"
}
```

---

### 5. Clear Cache

**Endpoint:** `POST /api/cache/clear`

**Purpose:** Clear semantic cache

**Request:**
```bash
curl -X POST http://localhost:8000/api/cache/clear
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "entries_cleared": 127,
  "disk_freed_mb": 45.3
}
```

---

### 6. Get Metrics

**Endpoint:** `GET /api/metrics`

**Purpose:** Prometheus metrics (Phase 2)

**Request:**
```bash
curl http://localhost:8000/api/metrics
```

**Response (text/plain):**
```
# HELP gateway_requests_total Total requests
# TYPE gateway_requests_total counter
gateway_requests_total{endpoint="/api/generate"} 523
gateway_requests_total{endpoint="/api/health"} 1024

# HELP gateway_request_duration_seconds Request duration
# TYPE gateway_request_duration_seconds histogram
gateway_request_duration_seconds_bucket{endpoint="/api/generate",le="0.1"} 45
gateway_request_duration_seconds_bucket{endpoint="/api/generate",le="0.5"} 312
...
```

---

## Examples

### Example 1: Code Generation

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a FastAPI endpoint that returns current time",
    "temperature": 0.7,
    "max_tokens": 1000
  }' | jq .
```

**Response:**
```json
{
  "text": "from fastapi import FastAPI\nfrom datetime import datetime\n\napp = FastAPI()\n\n@app.get(\"/time\")\ndef get_time():\n    return {\"current_time\": datetime.now().isoformat()}",
  "tokens_used": 32,
  "generation_time_ms": 1560,
  "cached": false
}
```

### Example 2: SQL Query Generation

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write SQL to find users who purchased in the last 30 days, ordered by purchase amount DESC",
    "system": "You are a SQL expert. Return only the query, no explanation.",
    "max_tokens": 500
  }'
```

### Example 3: Documentation

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write docstring for this function: def calculate_compound_interest(principal, rate, time): return principal * ((1 + rate) ** time)",
    "max_tokens": 300
  }'
```

### Example 4: Streaming

```bash
curl -X POST http://localhost:8000/api/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a poem about coding"}'

# Output streams in real-time
```

---

## Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Invalid JSON, prompt too long |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Model crashed, Ollama offline |
| 503 | Service Unavailable | Ollama not responding |

---

## Rate Limiting

**Current Limit:** 100 requests/minute (per-IP, Phase 1)

**Response Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1656350445
```

**When Exceeded:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit: 100 requests per minute",
  "retry_after": 45
}
```

---

## Response Caching

**Semantic Caching:** Identical or >85% similar prompts return cached responses in <50ms

**Cache Duration:** 24 hours (configurable)

**Cache Hit Detection:**
```json
{
  "cached": true,  // Indicates this was cached response
  "timestamp_cached": "2026-06-27T10:30:00Z"
}
```

---

## Timeout & Limits

| Setting | Value | Notes |
|---------|-------|-------|
| Request Timeout | 5 minutes | Kill long-running requests |
| Max Prompt Length | 12,000 chars | ~3,000 tokens |
| Max Response Tokens | 4,096 | Adjustable per request |
| Max Concurrent Requests | 10 | Phase 1 limit |
| Model Idle Time | 5 minutes | Auto-unload from VRAM |

---

## Error Handling

**All errors return JSON:**
```json
{
  "error": "error_code",
  "message": "Human-readable message",
  "details": "Optional: additional context",
  "timestamp": "2026-06-28T14:30:45Z"
}
```

**Common Error Codes:**
- `prompt_too_long` - Prompt exceeds limit
- `rate_limit_exceeded` - Too many requests
- `invalid_json` - Malformed JSON
- `model_error` - Model inference failed
- `ollama_offline` - Ollama not responding
- `cache_error` - Cache operation failed
- `validation_error` - Input failed validation

---

## Python Client Example

```python
import requests

class AIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def health(self):
        """Check API health"""
        response = requests.get(f"{self.base_url}/api/health")
        return response.json()
    
    def generate(self, prompt, temperature=0.7, max_tokens=2048):
        """Generate text"""
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload
        )
        return response.json()
    
    def stream(self, prompt):
        """Stream response"""
        payload = {"prompt": prompt, "stream": True}
        response = requests.post(
            f"{self.base_url}/api/stream",
            json=payload,
            stream=True
        )
        for line in response.iter_lines():
            if line:
                yield line.decode()

# Usage
client = AIClient()

# Health check
print(client.health())

# Generate code
response = client.generate("Write a hello world function")
print(response["text"])

# Stream output
for token in client.stream("Write a poem"):
    print(token, end="")
```

---

## JavaScript/Node Example

```javascript
// ai-client.js
class AIClient {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async health() {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }

  async generate(prompt, options = {}) {
    const payload = {
      prompt,
      temperature: options.temperature || 0.7,
      max_tokens: options.maxTokens || 2048,
      ...options
    };
    
    const response = await fetch(`${this.baseUrl}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    return response.json();
  }

  async *stream(prompt) {
    const response = await fetch(`${this.baseUrl}/api/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      yield decoder.decode(value);
    }
  }
}

// Usage
const client = new AIClient();
const response = await client.generate("Write a hello world function");
console.log(response.text);
```

---

## Testing

**Manual Testing:**
```bash
# Health
curl http://localhost:8000/api/health

# Generate
curl -X POST http://localhost:8000/api/generate \
  -d '{"prompt":"test"}' \
  -H "Content-Type: application/json"

# List models
curl http://localhost:8000/api/models
```

**Performance Testing:**
```bash
# Time a request
time curl -X POST http://localhost:8000/api/generate \
  -d '{"prompt":"test"}' \
  -H "Content-Type: application/json"

# Expected: 6-7 seconds (includes TTFT + streaming)
```

---

**Last Updated:** June 28, 2026
**Version:** 1.0
**Status:** Phase 1 Specification
