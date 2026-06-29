#!/usr/bin/env python3
"""
Test script for local Ollama setup.
Run after: ollama pull neural-chat
"""

import requests
import json
import time
import sys

OLLAMA_URL = "http://localhost:11434/api"
MODEL = "neural-chat"

def test_connection():
    """Test if Ollama server is running"""
    print("1️⃣  Testing connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        print("   ✓ Server responding")
        models = response.json().get("models", [])
        print(f"   ✓ Available models: {len(models)}")
        for m in models:
            print(f"     - {m['name']}")
        return len(models) > 0
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return False

def test_generate():
    """Test text generation"""
    print(f"\n2️⃣  Testing /api/generate endpoint...")
    prompt = "Write a Python function to check if a number is prime"

    try:
        start = time.time()
        response = requests.post(
            f"{OLLAMA_URL}/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
            },
            timeout=120
        )
        elapsed = time.time() - start

        result = response.json()
        generated = result["response"]

        print(f"   ✓ Generated {len(generated)} chars in {elapsed:.1f}s")
        print(f"   Prompt: {prompt}")
        print(f"   Response (first 200 chars):")
        print(f"   {generated[:200]}...")
        return True
    except Exception as e:
        print(f"   ✗ Generation failed: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print(f"\n3️⃣  Testing /api/chat endpoint...")

    try:
        start = time.time()
        response = requests.post(
            f"{OLLAMA_URL}/chat",
            json={
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": "¿Cómo se crea una lista en Python?"}
                ],
                "stream": False,
            },
            timeout=120
        )
        elapsed = time.time() - start

        result = response.json()
        message = result["message"]["content"]

        print(f"   ✓ Chat response {len(message)} chars in {elapsed:.1f}s")
        print(f"   Response (first 200 chars):")
        print(f"   {message[:200]}...")
        return True
    except Exception as e:
        print(f"   ✗ Chat failed: {e}")
        return False

def test_parameters():
    """Test custom parameters"""
    print(f"\n4️⃣  Testing custom parameters...")

    try:
        # Low temperature (deterministic)
        response = requests.post(
            f"{OLLAMA_URL}/generate",
            json={
                "model": MODEL,
                "prompt": "Convert 255 to binary",
                "stream": False,
                "temperature": 0.0,
                "num_predict": 50,
            },
            timeout=120
        )

        result = response.json()
        print(f"   ✓ temperature=0.0 (deterministic)")
        print(f"   Response: {result['response']}")
        return True
    except Exception as e:
        print(f"   ✗ Parameters test failed: {e}")
        return False

def test_claude_tool():
    """Example: Use as Claude tool"""
    print(f"\n5️⃣  Example: Using as Claude tool...")

    try:
        from anthropic import Anthropic
        import os

        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        # Define tool
        tools = [{
            "name": "ollama_generate",
            "description": "Generate text using local Ollama",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"}
                },
                "required": ["prompt"]
            }
        }]

        # Make request
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=256,
            tools=tools,
            messages=[{
                "role": "user",
                "content": "Use the ollama tool to write a haiku about programming"
            }]
        )

        print(f"   ✓ Claude request successful")
        print(f"   Response type: {response.stop_reason}")

        # Check if Claude used the tool
        for block in response.content:
            if block.type == "tool_use":
                print(f"   ✓ Claude called: {block.name}")
                print(f"   Input: {block.input}")

        return True
    except Exception as e:
        print(f"   ⚠ Claude tool test skipped: {e}")
        return False

def main():
    print("=" * 50)
    print("OLLAMA LOCAL TEST SUITE")
    print("=" * 50)

    tests = [
        ("Connection", test_connection),
        ("Generation", test_generate),
        ("Chat", test_chat),
        ("Parameters", test_parameters),
        ("Claude Tool", test_claude_tool),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except KeyboardInterrupt:
            print("\n⏸ Interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, p in results:
        status = "✓" if p else "✗"
        print(f"{status} {name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Ollama is ready to use.")
        return 0
    else:
        print("\n⚠ Some tests failed. Check Ollama setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
