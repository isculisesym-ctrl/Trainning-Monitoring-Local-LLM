# Installation Guide: AI-Platform
**Phase 1 Setup (Week 1-2)**
**Estimated Time: 2-3 hours (including testing)**

---

## Prerequisites Checklist

- [ ] Windows 10 Pro (you have this ✓)
- [ ] 32GB RAM (you have this ✓)
- [ ] RTX 4060 4GB VRAM (you have this ✓)
- [ ] 6GB free disk space (you have 364GB ✓)
- [ ] Git installed (you have this ✓)
- [ ] Python 3.11+ (you have 3.11.9 ✓)
- [ ] Administrator access
- [ ] 30-60 minutes uninterrupted

---

## Step-by-Step Installation

### Phase 1A: Ollama Setup (15 minutes)

#### 1. Download Ollama

```bash
# Method 1: Graphical Installer (Easiest)
Open: https://ollama.ai/download/windows
Click: Download for Windows
Save to: C:\Users\[YourUsername]\Downloads\

# Method 2: Command Line
curl -L https://ollama.ai/download/windows -o ollama-installer.exe
```

#### 2. Install Ollama

```bash
# Run the installer
C:\Users\[YourUsername]\Downloads\ollama-installer.exe

# Follow prompts:
├─ Accept license
├─ Choose install location (default: C:\Program Files\Ollama)
├─ Let it create shortcuts
└─ Restart may be required

# Verify installation
ollama --version
# Expected output: ollama version 0.1.X
```

#### 3. Verify CUDA Detection

```bash
# Start Ollama server
ollama serve

# In another terminal:
ollama list

# Expected: Should show available models (none yet)
# Look for GPU detection message in serve output
```

**Troubleshooting:**
- If Ollama won't start: Check if port 11434 is available
- If GPU not detected: Update NVIDIA drivers to latest version
- If CUDA missing: Run `ollama serve` again (it handles fallback)

---

### Phase 1B: Download Qwen Model (20-30 minutes)

#### 1. Pull Model from HuggingFace

```bash
# Make sure Ollama service is running
ollama serve

# In another terminal window:
ollama pull qwen:7b-coder

# This downloads ~3.8GB
# Expected output:
# pulling manifest ✓
# pulling 9f8c3f... ✓  [===========] 3.8 GB
# Success!
```

**What happens:**
- Downloads: `~3.8GB` (quantized with Q4_K_M)
- Location: `C:\Users\[YourUsername]\.ollama\models\`
- Time: 15-30 min depending on internet (50Mbps = ~10 min)
- Storage: Model file + metadata

#### 2. Verify Model Downloaded

```bash
# List available models
ollama list

# Expected output:
# NAME                 ID           SIZE      MODIFIED
# qwen:7b-coder        abc123...    3.8 GB    1 minute ago
```

#### 3. Test Model Works

```bash
# Run test inference
ollama run qwen:7b-coder "Write a Python function to add two numbers"

# Expected response:
# def add(a, b):
#     """Add two numbers together."""
#     return a + b

# If this works, Ollama + Model are good ✓
```

**Troubleshooting:**
- Out of memory: Your RTX 4060 (4GB) is at limit but should work
- Model slow to load: Normal (2-3 seconds first time)
- VRAM errors: Try model size check (see below)

---

### Phase 1C: Python Environment Setup (10 minutes)

#### 1. Create Virtual Environment

```bash
# Navigate to project
cd C:\Proyectos\AI-Platform

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see: (venv) in your terminal prompt
```

#### 2. Install Dependencies

```bash
# Make sure you're in venv (see (venv) in prompt)
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Expected: Installs fastapi, httpx, pydantic, etc.
# Time: 2-3 minutes

# Verify installation
pip list | grep fastapi
# Should show: fastapi version

python -c "import fastapi; print(fastapi.__version__)"
# Should output version number
```

---

### Phase 1D: Gateway Setup (15 minutes)

#### 1. Create Project Structure

```bash
# You should already have this from repo, but verify:
C:\Proyectos\AI-Platform\
├── src/
│   ├── __init__.py
│   ├── gateway.py
│   ├── models.py
│   ├── cache.py
│   ├── ollama_client.py
│   └── validators.py
├── data/
│   ├── cache/
│   └── logs/
├── requirements.txt
├── .env.example
└── README.md
```

#### 2. Configure Environment Variables

```bash
# Copy example to actual
cp .env.example .env

# Edit .env file:
notepad .env

# Set these values:
OLLAMA_BASE_URL=http://localhost:11434
GATEWAY_HOST=127.0.0.1
GATEWAY_PORT=8000
CACHE_TYPE=file
CACHE_DIR=./data/cache
CACHE_TTL=86400
DEBUG=False
```

#### 3. Create Cache & Log Directories

```bash
# These should exist, but make sure:
mkdir -p data\cache
mkdir -p data\logs

# Verify:
dir data\
# Should show: cache  logs
```

---

### Phase 1E: Start Gateway (5 minutes)

#### 1. Activate Virtual Environment

```bash
# If not already active:
cd C:\Proyectos\AI-Platform
venv\Scripts\activate
```

#### 2. Start the Gateway

```bash
# Run the gateway
python src/gateway.py

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

#### 3. Verify Gateway Responds

**In another terminal (NEW window):**

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Expected response:
# {"status":"ok","model":"qwen:7b-coder","timestamp":"..."}

# Or in PowerShell:
Invoke-WebRequest http://localhost:8000/api/health | ConvertFrom-Json
```

**Troubleshooting:**
- Port already in use: Change port in .env and restart
- Gateway won't start: Check Python version (`python --version`)
- No response: Check Ollama is running on port 11434

---

### Phase 1F: Test API (10 minutes)

#### Test 1: Simple Generation

```bash
# Make a request to the API
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a simple Python function to check if a number is even"}'

# Expected response (should take ~6 seconds):
{
  "text": "def is_even(n):\n    return n % 2 == 0",
  "tokens_used": 24,
  "generation_time_ms": 5800,
  "cached": false
}
```

#### Test 2: PowerShell Version

```powershell
# If using PowerShell:
$body = @{
    prompt = "Write a FastAPI endpoint that returns the current time"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/generate `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body | ConvertFrom-Json
```

#### Test 3: Repeated Request (Cache Test)

```bash
# Make same request twice
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a simple Python function to check if a number is even"}'

# Second request should be MUCH faster (<100ms)
# Response should show: "cached": true
```

---

### Phase 1G: IDE Integration (10 minutes)

#### Option A: VS Code with Continue Extension

```bash
# 1. Open VS Code
code .

# 2. Open Extensions (Ctrl+Shift+X)
# 3. Search: "Continue"
# 4. Install: Continue - Code Autocompletion

# 5. Configure Continue:
# Create/edit: ~/.continue/config.json
{
  "models": [
    {
      "title": "Local Qwen",
      "provider": "openai",
      "model": "qwen:7b-coder",
      "apiBase": "http://localhost:8000/api"
    }
  ]
}

# 6. Test:
# - Open any Python file
# - Highlight code, press Ctrl+Shift+A
# - Should show autocomplete from local model
```

#### Option B: Alternative IDEs

```bash
# Jupyter Notebook:
jupyter notebook
# Then use ai_platform Python client

# Command line:
# Use curl commands from tests above
```

---

## Verification Checklist

After installation, verify each step:

- [ ] **Ollama installed:** `ollama --version` shows version
- [ ] **Model downloaded:** `ollama list` shows qwen:7b-coder
- [ ] **Model works:** `ollama run qwen:7b-coder "test"` generates code
- [ ] **Python venv created:** `(venv)` shows in prompt
- [ ] **Dependencies installed:** `pip list` shows fastapi
- [ ] **Gateway starts:** `python src/gateway.py` shows "Uvicorn running"
- [ ] **Health check works:** `curl http://localhost:8000/api/health` responds
- [ ] **Generation works:** API test returns code (takes ~6 sec)
- [ ] **Caching works:** Second API test faster (<100ms)
- [ ] **IDE integration:** Continue extension installed

---

## Common Issues & Solutions

### Issue: "CUDA out of memory"

**Symptoms:**
- Error: `CUDA out of memory` or `OOM`
- Gateway returns 500 error
- Ollama crashes

**Solutions:**
1. Reduce batch size (already 1, can't reduce)
2. Use Q2_K quantization (lower quality): `ollama pull qwen:7b-coder-q2`
3. Restart Ollama to clear VRAM: `ollama serve` (kill and restart)
4. Plan GPU upgrade (Phase 5)

**Workaround:** Use CPU inference (slower, ~2 tok/s)
```bash
export OLLAMA_NUM_GPU=0
ollama serve
```

---

### Issue: "Connection refused localhost:11434"

**Symptoms:**
- Error: `Connection refused`
- Cannot reach Ollama server

**Solutions:**
1. Check Ollama is running: `ollama serve` (in separate terminal)
2. Verify port: Check if 11434 is open
3. Restart Ollama:
```bash
# Kill any Ollama processes
taskkill /IM ollama.exe /F

# Restart fresh
ollama serve
```

---

### Issue: "Model not found"

**Symptoms:**
- Error: `model not found`
- `ollama list` shows no models

**Solutions:**
1. Pull the model again:
```bash
ollama pull qwen:7b-coder
```

2. If slow download:
   - Check internet (test: `ping 8.8.8.8`)
   - Use different mirror (see Ollama docs)

3. If storage full:
   - Check: `dir C:\Users\[name]\.ollama\`
   - Free up space and retry

---

### Issue: "Gateway won't start / Port 8000 in use"

**Symptoms:**
- Error: `Address already in use: ('127.0.0.1', 8000)`

**Solutions:**
1. Find what's using port 8000:
```bash
netstat -ano | findstr :8000
```

2. Kill the process:
```bash
taskkill /PID [PID] /F
```

3. Or change port:
   - Edit `.env`: `GATEWAY_PORT=8001`
   - Restart gateway

---

### Issue: "GPU not detected"

**Symptoms:**
- Ollama running on CPU only
- Output shows: `Using CPU only`
- Inference very slow (~2 tok/s)

**Solutions:**
1. Update NVIDIA drivers:
   - Device Manager → Display adapters → RTX 4060
   - Update driver → Restart

2. Check CUDA installation:
```bash
# This should show your GPU:
wmic path win32_videocontroller get name
```

3. If still no GPU, use CPU (acceptable for Phase 1)

---

### Issue: "Download very slow / stuck"

**Symptoms:**
- `ollama pull` hangs at 50%
- Download speed <1Mbps

**Solutions:**
1. Check internet:
```bash
speedtest  # or use speedtest.net
```

2. Change Ollama mirror:
```bash
$env:OLLAMA_MODELS = "C:\custom\path"
ollama pull qwen:7b-coder
```

3. Resume download:
```bash
ollama pull qwen:7b-coder  # Run again, continues from where it left off
```

---

## Performance Baseline

After successful installation, measure performance:

```bash
# Latency test
time curl -X POST http://localhost:8000/api/generate \
  -d '{"prompt":"Hello world"}' 2>/dev/null

# Expected: Total ~6-7 seconds
#   - First token: 200ms
#   - Streaming: 5+ seconds
#   - Total: ~6000ms

# Token throughput
# Expected: 20 tokens/second
# = 6000ms / 120 tokens ≈ 50ms per token

# Resource usage
# GPU: 3.8GB used (your RTX 4060 limit)
# RAM: 4-6GB used
# CPU: 30-40% during inference
```

---

## Next Steps After Installation

1. **Read:** [ROADMAP.md](./ROADMAP.md) - Understand 7-phase plan
2. **Setup:** Continue extension in VS Code
3. **Test:** Generate 5 code snippets, verify quality
4. **Document:** Note any issues for troubleshooting
5. **Track:** Use [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for Phase 1 progress

---

## Support

**If stuck:**
1. Check error message against "Common Issues" section above
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) to understand components
3. Test each component independently:
   - Ollama: `ollama list`
   - Gateway: `curl http://localhost:8000/api/health`
   - API: `curl -X POST http://localhost:8000/api/generate ...`

**Estimate to working system: 2-3 hours total**

---

**Installation Completed:** ✓ Ready for Phase 2 (Gateway hardening)

Next: See [ROADMAP.md](./ROADMAP.md) for Week 2-4 tasks
