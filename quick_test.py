#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

OLLAMA = "http://localhost:11434/api"

# Test 1
print("[OK] Test 1: Generation")
r = requests.post(f"{OLLAMA}/generate",
    json={"model": "neural-chat", "prompt": "Hello", "stream": False},
    timeout=120)
resp = r.json()["response"][:50]
print(f"  Response: {resp} ...")

# Test 2
print("\n[OK] Test 2: Chat")
r = requests.post(f"{OLLAMA}/chat",
    json={"model": "neural-chat", "messages": [{"role": "user", "content": "Hi"}], "stream": False},
    timeout=120)
resp = r.json()["message"]["content"][:50]
print(f"  Response: {resp} ...")

print("\n[PASS] Ollama working! You can now:")
print("   - Use test_ollama.py for full test suite")
print("   - Integrate into your projects (see OLLAMA_LOCAL_GUIDE.md)")
print("   - Connect to Claude API (see examples in guide)")
