# Ollama Local — Manual de Uso

**Instalación:** Automática (2026-06-28)  
**Modelo:** neural-chat (4.5 GB, balance velocidad/calidad)  
**API endpoint:** http://localhost:11434

---

## 🚀 Quick Start

### Levanta Ollama (hazlo UNA VEZ cada sesión)
```powershell
ollama serve
# Output: Listening on 127.0.0.1:11434
# Déjalo corriendo (no cierres esta terminal)
```

### Test rápido (otra terminal)
```powershell
# Request simple
curl -X POST http://localhost:11434/api/generate `
  -H "Content-Type: application/json" `
  -d '{"model":"neural-chat","prompt":"Hello","stream":false}'

# Ver modelos disponibles
curl http://localhost:11434/api/tags
```

---

## 💻 Python — Manera Recomendada

### Setup (una sola vez)
```bash
pip install requests
```

### Código simple
```python
import requests
import json

OLLAMA_URL = "http://localhost:11434/api"

def generate(prompt: str, model: str = "neural-chat") -> str:
    """Generate text from local Ollama model"""
    response = requests.post(
        f"{OLLAMA_URL}/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
        },
        timeout=60
    )
    return response.json()["response"]

# Test
result = generate("Write a Python function to check if a number is prime")
print(result)
```

### Chat (interfaz mejor)
```python
def chat(message: str, model: str = "neural-chat") -> str:
    """Chat with local Ollama model"""
    response = requests.post(
        f"{OLLAMA_URL}/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "stream": False,
        },
        timeout=60
    )
    return response.json()["message"]["content"]

# Test
result = chat("¿Cómo se crea una lista en Python?")
print(result)
```

### Con parámetros avanzados
```python
def generate_advanced(
    prompt: str,
    model: str = "neural-chat",
    temperature: float = 0.7,
    top_p: float = 0.9,
    num_predict: int = 200,
) -> str:
    """Generate with custom parameters"""
    response = requests.post(
        f"{OLLAMA_URL}/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": num_predict,
        },
        timeout=60
    )
    return response.json()["response"]

# Ejemplo: Más creativo
result = generate_advanced(
    "Write a funny joke about programming",
    temperature=1.0,  # Más creativo
    num_predict=100
)
print(result)

# Ejemplo: Más determinístico
result = generate_advanced(
    "Convert 123 decimal to binary",
    temperature=0.0,  # Respuesta fija
)
print(result)
```

---

## 🔌 Conecta a Claude (API Cloud)

### Opción A: Claude llama a tu Ollama local (Tool Use)

```python
import os
from anthropic import Anthropic
import requests

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
OLLAMA_URL = "http://localhost:11434/api"

def call_ollama(prompt: str, model: str = "neural-chat") -> str:
    """Local Ollama as a tool for Claude"""
    response = requests.post(
        f"{OLLAMA_URL}/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=60
    )
    return response.json()["response"]

# Define tool
tools = [
    {
        "name": "ollama_generate",
        "description": "Generate text using local Ollama model (fast, no API cost)",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Text prompt to generate from"
                },
                "model": {
                    "type": "string",
                    "description": "Model name (default: neural-chat)",
                    "default": "neural-chat"
                }
            },
            "required": ["prompt"]
        }
    }
]

# Chat loop
messages = [
    {
        "role": "user",
        "content": "Use the ollama_generate tool to write a Python decorator. Then explain what you got."
    }
]

print("Claude:", end=" ")
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    tools=tools,
    messages=messages
)

# Handle tool calls
while response.stop_reason == "tool_use":
    tool_use = next(b for b in response.content if b.type == "tool_use")
    
    print(f"\n[Claude uses {tool_use.name}]")
    
    # Call your local Ollama
    result = call_ollama(**tool_use.input)
    
    print(f"[Ollama response]: {result[:100]}...")
    
    # Feed back to Claude
    messages.append({"role": "assistant", "content": response.content})
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result
            }
        ]
    })
    
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

# Print final response
for block in response.content:
    if hasattr(block, "text"):
        print(f"\nClaude: {block.text}")
```

### Opción B: Usa Ollama para pre-procesamiento

```python
import requests

# Paso 1: Ollama procesa local (rápido, gratis)
def preprocess_with_ollama(text: str) -> str:
    """Use local Ollama to summarize/process text"""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "neural-chat",
            "prompt": f"Summarize in 2 sentences:\n\n{text}",
            "stream": False,
        }
    )
    return response.json()["response"]

# Paso 2: Claude refina (poderoso)
from anthropic import Anthropic
client = Anthropic()

text = "Long article about AI..."
summary = preprocess_with_ollama(text)

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=500,
    messages=[
        {
            "role": "user",
            "content": f"Refine this summary:\n\n{summary}"
        }
    ]
)

print(response.content[0].text)
```

---

## 📊 Parámetros Explicados

| Parámetro | Rango | Efecto |
|-----------|-------|--------|
| `temperature` | 0.0-2.0 | 0.0=determinístico, 1.0=normal, 2.0=caótico |
| `top_p` | 0.0-1.0 | Diversidad (1.0=all tokens, 0.1=top 10%) |
| `num_predict` | 1-∞ | Tokens máximos en respuesta |
| `stream` | true/false | false=respuesta completa en 1 request |

**Recomendaciones:**
- Código/matemática: `temp=0.0` (preciso)
- Escritura creativa: `temp=1.0-1.5` (variado)
- Chat general: `temp=0.7` (balance)

---

## 🎯 Casos de Uso

### Caso 1: Completar código (local es suficiente)
```python
def complete_code(snippet: str) -> str:
    return generate(f"Complete this code:\n\n{snippet}")

result = complete_code("def fibonacci(n):")
print(result)
```

### Caso 2: Code review (Claude + Ollama)
```python
# Ollama sugiere mejoras rápidas
code = "def sum(a, b): return a + b"
suggestions = generate(f"Improve:\n\n{code}")

# Claude lo refina
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": f"Refine:\n\n{suggestions}"}
    ]
)
```

### Caso 3: Traducción (local = rápido)
```python
def translate(text: str, to_lang: str = "Spanish") -> str:
    return generate(f"Translate to {to_lang}:\n\n{text}")

print(translate("Hello world", "Spanish"))
```

---

## ⚙️ Troubleshooting

### "Connection refused"
```powershell
# Ollama no está corriendo
ollama serve
# Espera 2 seg, intenta de nuevo
```

### "Model not found"
```powershell
ollama list  # Ver modelos disponibles
ollama pull neural-chat  # Descargar si falta
```

### Muy lento
```powershell
# neural-chat es 4.5 GB, puede ser lento en CPU vieja
# Alternativa rápida:
ollama pull mistral  # 4.1 GB, más rápido
# Luego en código: model="mistral"
```

### Falta memoria
```powershell
# Si ves "out of memory", reduce tamaño modelo
ollama pull phi  # Más pequeño (2.7 GB)
```

---

## 🔗 Modelos Disponibles

```powershell
ollama pull neural-chat    # ✓ Instalado (recomendado)
ollama pull mistral        # Más rápido
ollama pull phi            # Más pequeño
ollama pull llama2         # Más poderoso
ollama pull dolphin-mixtral # Mejor (26 GB, requiere GPU)
```

Cambiar en código:
```python
generate("...", model="mistral")  # En lugar de neural-chat
```

---

## 💰 Ahorro de Costos

**Sin Ollama local:**
- Cada request a Claude = $$$
- 1000 requests = ~$1-10 (según modelo)

**Con Ollama local:**
- Generación simple: gratis (local)
- Claude solo para refinamiento: 50% ahorro
- Pre-procesamiento: gratis

**ROI:** Vale la pena si haces >100 requests/semana.

---

## 🚀 Próximos Pasos

1. **Abre 2 terminales:**
   - Terminal 1: `ollama serve`
   - Terminal 2: código Python

2. **Test rápido:**
   ```bash
   cd C:\Proyectos\AI-Platform
   python -c "
   import requests
   r = requests.post('http://localhost:11434/api/generate',
     json={'model':'neural-chat','prompt':'Hello','stream':False})
   print(r.json()['response'])
   "
   ```

3. **Integra a tu proyecto:**
   - Copia funciones de este manual
   - Adapta según tu caso de uso
   - Mide: tiempo, costo, calidad

---

**Versión:** 1.0  
**Fecha:** 2026-06-28  
**Modelo:** neural-chat (4.5 GB)  
**API:** http://localhost:11434  
**Documentación oficial:** https://ollama.ai/library
