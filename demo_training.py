#!/usr/bin/env python3
"""Demo: Train with 5 exercises locally to validate Fase 1."""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.training.corpus_loader import load_corpus, get_corpus_loader
from src.training.exercise_loader import load_exercises, get_exercise_loader, Level
from src.training.prompt_builder import PromptBuilder
from src.training.validators import ResponseValidator
from src.training.config import get_training_config
from src.checkpoint.checkpoint_types import SessionMetrics, ExerciseResult, CheckpointReport
from src.ollama_client import OllamaClient


async def demo_training():
    """Run demo training with 5 exercises."""

    print("\n" + "="*80)
    print("FASE 1 TRAINING DEMO: Load Corpus + Exercises + Run 5 Training Exercises")
    print("="*80 + "\n")

    # Load configuration
    try:
        config = get_training_config()
        print(f"✓ Configuration loaded: {config.TRAINING_MODE} mode")
        print(f"  - Corpus: {config.CORPUS_DIR}")
        print(f"  - Exercises: {config.EXERCISES_FILE}")
        print(f"  - Ollama: {config.OLLAMA_BASE_URL}/{config.OLLAMA_MODEL}\n")
    except Exception as e:
        print(f"✗ Configuration error: {e}\n")
        return

    # 1. Load corpus
    print("1. LOADING CORPUS")
    print("-" * 80)
    try:
        corpus_loader = get_corpus_loader()
        corpus = corpus_loader.load()
        print(f"✓ Loaded {len(corpus)} corpus files")
        for key in corpus_loader.get_available_keys():
            size_kb = len(corpus_loader.get_corpus_content(key)) / 1024
            print(f"  - {key}: {size_kb:.1f} KB")
        print()
    except Exception as e:
        print(f"✗ Failed to load corpus: {e}\n")
        return

    # 2. Load exercises
    print("2. LOADING EXERCISES")
    print("-" * 80)
    try:
        exercise_loader = get_exercise_loader()
        exercises = exercise_loader.load()
        print(f"✓ Loaded {len(exercises)} exercises")

        # Count by level
        by_level = {level.value: 0 for level in Level}
        for ex in exercises.values():
            by_level[ex.level.value] += 1

        for level, count in by_level.items():
            print(f"  - {level}: {count}")
        print()
    except Exception as e:
        print(f"✗ Failed to load exercises: {e}\n")
        return

    # 3. Initialize training components
    print("3. INITIALIZING TRAINING COMPONENTS")
    print("-" * 80)

    prompt_builder = PromptBuilder(corpus_loader)

    # Initialize Ollama client
    ollama_client = OllamaClient(
        base_url=config.OLLAMA_BASE_URL,
        model=config.OLLAMA_MODEL,
        timeout=config.OLLAMA_TIMEOUT
    )

    # Check Ollama connection
    try:
        connected = await ollama_client.check_connection()
        if connected:
            print(f"✓ Connected to Ollama: {config.OLLAMA_MODEL}\n")
        else:
            print(f"✗ Failed to connect to Ollama\n")
            return
    except Exception as e:
        print(f"✗ Ollama connection error: {e}\n")
        print(f"  Make sure Ollama is running: ollama serve\n")
        return

    # 4. Run 5 demo exercises
    print("4. RUNNING 5 DEMO EXERCISES")
    print("-" * 80)

    session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_metrics = SessionMetrics(
        session_id=session_id,
        started_at=datetime.now()
    )

    # Get 5 exercises: mix of levels
    exercise_ids = [
        "arch_junior_001",
        "arch_junior_002",
        "arch_mid_010",
        "arch_mid_011",
        "arch_senior_025",
    ]

    demo_exercises = []
    for ex_id in exercise_ids:
        ex = exercise_loader.get_exercise(ex_id)
        if ex:
            demo_exercises.append(ex)
        else:
            print(f"✗ Exercise not found: {ex_id}")

    if not demo_exercises:
        print("✗ No exercises found!")
        return

    for i, exercise in enumerate(demo_exercises, 1):
        print(f"\n[{i}/{len(demo_exercises)}] Exercise: {exercise.title} ({exercise.level.value})")
        print(f"      Category: {exercise.category}")

        try:
            # Build prompt with corpus injection
            system_prompt, user_prompt, corpus_text = prompt_builder.build_exercise_prompts(exercise)

            # Generate response from Ollama
            print(f"      Generating response... ", end="", flush=True)
            response = await ollama_client.generate(
                prompt=user_prompt,
                temperature=config.GENERATION_TEMPERATURE,
                top_p=config.GENERATION_TOP_P,
                num_predict=config.GENERATION_MAX_TOKENS
            )
            print(f"✓ ({len(response)} chars)")

            # Evaluate response
            result_dict = ResponseValidator.auto_evaluate(response, exercise)

            # Record result
            result = ExerciseResult(
                exercise_id=exercise.id,
                quality_score=result_dict["quality_score"],
                success=result_dict["success"],
                timestamp=datetime.now(),
                patterns_found=result_dict["patterns_found"],
                patterns_total=result_dict["patterns_total"],
                regex_matched=result_dict["regex_matched"],
                regex_total=result_dict["regex_total"],
                requires_manual_review=result_dict["requires_manual_review"],
                response_length=len(response)
            )

            session_metrics.add_result(result)

            # Print evaluation
            status = "✓ PASS" if result.success else "✗ FAIL"
            print(f"      Score: {result.quality_score:.1f}/10 {status}")
            print(f"      Patterns: {result.patterns_found}/{result.patterns_total}, Regex: {result.regex_matched}/{result.regex_total}")

        except Exception as e:
            print(f"      ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            session_metrics.total_exercises += 1

    # 5. Summary
    print("\n" + "="*80)
    print("TRAINING SESSION SUMMARY")
    print("="*80)

    session_metrics.ended_at = datetime.now()
    duration = (session_metrics.ended_at - session_metrics.started_at).total_seconds() / 60

    print(f"\nSession: {session_id}")
    print(f"Duration: {duration:.1f} minutes")
    print(f"Total exercises: {session_metrics.total_exercises}")
    print(f"Successful: {session_metrics.successful_exercises}")
    print(f"Failed: {session_metrics.failed_exercises}")
    print(f"Success rate: {session_metrics.success_rate:.1%}")
    print(f"Avg quality score: {session_metrics.avg_quality_score:.1f}/10")

    # Save session metrics
    session_file = config.TRAINING_LOGS_DIR / f"{session_id}.json"
    session_metrics_data = session_metrics.to_dict()

    with open(session_file, "w") as f:
        json.dump(session_metrics_data, f, indent=2)

    print(f"\n✓ Session saved to: {session_file}")

    # 6. Corpus injection example
    print("\n" + "="*80)
    print("CORPUS INJECTION EXAMPLE")
    print("="*80)

    example_exercise = exercise_loader.get_exercise("arch_senior_025")
    system_prompt, user_prompt, corpus_text = prompt_builder.build_exercise_prompts(example_exercise)

    print(f"\nExercise: {example_exercise.title}")
    print(f"\nSystem Prompt ({len(system_prompt)} chars):")
    print(system_prompt[:500] + "...\n")

    print(f"Corpus Context Injected ({len(corpus_text)} chars):")
    print(corpus_text[:300] + "...\n")

    print("\n✓ FASE 1 DEMO COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Run tests: pytest tests/training/")
    print("2. Configure Claude API (optional, for hybrid mode)")
    print("3. Start Phase 2: Implement training loop")


if __name__ == "__main__":
    try:
        asyncio.run(demo_training())
    except KeyboardInterrupt:
        print("\n\n✗ Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
