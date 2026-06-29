#!/usr/bin/env python3
"""Debug script to identify training issues"""

import asyncio
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)

sys.path.insert(0, str(Path(__file__).parent))

from src.training.exercise_loader import get_exercise_loader
from src.training.prompt_builder import PromptBuilder
from src.training.corpus_loader import get_corpus_loader
from src.training.config import get_training_config
from src.ollama_client import OllamaClient


async def debug():
    print("\n" + "="*80)
    print("DEBUG: Training System")
    print("="*80 + "\n")

    # 1. Config
    print("[1/7] Loading config...")
    try:
        config = get_training_config()
        print(f"[OK] Config loaded")
        print(f"     Ollama: {config.OLLAMA_BASE_URL}")
        print(f"     Model: {config.OLLAMA_MODEL}")
    except Exception as e:
        print(f"[ERROR] Config: {e}")
        return

    # 2. Corpus
    print("\n[2/7] Loading corpus...")
    try:
        corpus_loader = get_corpus_loader()
        corpus = corpus_loader.load()
        print(f"[OK] Corpus loaded: {len(corpus)} files")
    except Exception as e:
        print(f"[ERROR] Corpus: {e}")
        return

    # 3. Exercises
    print("\n[3/7] Loading exercises...")
    try:
        exercise_loader = get_exercise_loader()
        exercises = exercise_loader.load()
        print(f"[OK] Exercises loaded: {len(exercises)} items")

        # Check specific exercise
        ex = exercise_loader.get_exercise("arch_junior_001")
        if ex:
            print(f"     Sample: {ex.id} - {ex.title}")
        else:
            print("[ERROR] Exercise 'arch_junior_001' not found!")
    except Exception as e:
        print(f"[ERROR] Exercises: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Prompt builder
    print("\n[4/7] Testing prompt builder...")
    try:
        builder = PromptBuilder(corpus_loader)
        ex = exercise_loader.get_exercise("arch_junior_001")
        system_prompt, user_prompt, corpus_text = builder.build_exercise_prompts(ex)
        print(f"[OK] Prompts built")
        print(f"     System prompt: {len(system_prompt)} chars")
        print(f"     User prompt: {len(user_prompt)} chars")
        print(f"     Corpus: {len(corpus_text)} chars")
    except Exception as e:
        print(f"[ERROR] Prompt builder: {e}")
        import traceback
        traceback.print_exc()
        return

    # 5. Ollama connection
    print("\n[5/7] Checking Ollama connection...")
    try:
        ollama = OllamaClient(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL,
            timeout=30
        )
        connected = await ollama.check_connection()
        if connected:
            print(f"[OK] Connected to Ollama")
        else:
            print(f"[ERROR] Ollama responded but check failed")
            return
    except Exception as e:
        print(f"[ERROR] Ollama connection: {e}")
        print(f"       Make sure: ollama serve is running")
        return

    # 6. Generate test response
    print("\n[6/7] Testing generation...")
    try:
        async with OllamaClient(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL,
            timeout=30
        ) as ollama:
            ex = exercise_loader.get_exercise("arch_junior_001")
            _, user_prompt, _ = builder.build_exercise_prompts(ex)

            print(f"       Sending prompt to Ollama...")
            print(f"       Prompt: {user_prompt[:100]}...")

            response_data = await ollama.generate(
                prompt=user_prompt,
                temperature=0.7,
                top_p=0.9,
                max_tokens=500  # Shorter for testing
            )

            # Extract text from response dict
            response_text = response_data.get("text", "")
            tokens_in = response_data.get("tokens_input", 0)
            tokens_out = response_data.get("tokens_output", 0)

            print(f"[OK] Generated response: {len(response_text)} chars ({tokens_out} tokens)")
            print(f"     Response preview: {response_text[:200]}...")

            # 7. Validation
            print("\n[7/7] Testing validation...")
            from src.training.validators import ResponseValidator
            result = ResponseValidator.auto_evaluate(response_text, ex)
            print(f"[OK] Validation passed")
            print(f"     Quality score: {result['quality_score']:.1f}/10")
            print(f"     Success: {result['success']}")
            print(f"     Patterns found: {result['patterns_found']}/{result['patterns_total']}")

    except asyncio.TimeoutError:
        print(f"[ERROR] Generation timeout (Ollama slow or hanging)")
        return
    except Exception as e:
        print(f"[ERROR] Generation: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*80)
    print("DEBUG: ALL CHECKS PASSED")
    print("="*80 + "\n")
    print("System is ready for training!")
    print("Run: python training_12h.py")


if __name__ == "__main__":
    try:
        asyncio.run(debug())
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
