#!/usr/bin/env python3
"""Phase 2: 12-Hour Continuous Training Loop - Ready to Run Overnight"""

import asyncio
import logging
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import time

# Setup logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/training_logs/training_12h.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

from src.training.corpus_loader import get_corpus_loader
from src.training.exercise_loader import get_exercise_loader
from src.training.prompt_builder import PromptBuilder
from src.training.validators import ResponseValidator
from src.training.config import get_training_config
from src.checkpoint.checkpoint_types import SessionMetrics, ExerciseResult
from src.ollama_client import OllamaClient


class TrainingLoop:
    """12-hour continuous training loop"""

    def __init__(self, duration_hours=12):
        self.duration_hours = duration_hours
        self.config = get_training_config()
        self.session_id = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_metrics = SessionMetrics(
            session_id=self.session_id,
            started_at=datetime.now()
        )

    async def run(self):
        """Run 12-hour training loop"""
        logger.info('='*80)
        logger.info(f'PHASE 2: STARTING 12-HOUR TRAINING LOOP')
        logger.info(f'Session: {self.session_id}')
        logger.info(f'Mode: {self.config.TRAINING_MODE}')
        logger.info('='*80)

        try:
            logger.info('Loading corpus...')
            corpus_loader = get_corpus_loader()
            corpus = corpus_loader.load()
            logger.info(f'✓ Loaded {len(corpus)} corpus files')

            logger.info('Loading exercises...')
            exercise_loader = get_exercise_loader()
            exercises = exercise_loader.load()
            logger.info(f'✓ Loaded {len(exercises)} exercises')

            prompt_builder = PromptBuilder(corpus_loader)

            ollama_client = OllamaClient(
                base_url=self.config.OLLAMA_BASE_URL,
                model=self.config.OLLAMA_MODEL,
                timeout=self.config.OLLAMA_TIMEOUT
            )

            connected = await ollama_client.check_connection()
            if not connected:
                logger.error('✗ Failed to connect to Ollama')
                return

            logger.info(f'✓ Connected to Ollama: {self.config.OLLAMA_MODEL}')

        except Exception as e:
            logger.error(f'✗ Initialization error: {e}')
            return

        start_time = datetime.now()
        end_time = start_time + timedelta(hours=self.duration_hours)
        exercise_list = list(exercises.values())
        exercise_index = 0

        logger.info(f'\nStarting loop at {start_time}')
        logger.info(f'Will run until {end_time} ({self.duration_hours}h)')
        logger.info('Training in progress...\n')

        try:
            async with ollama_client:
                while datetime.now() < end_time:
                    exercise = exercise_list[exercise_index % len(exercise_list)]
                    exercise_index += 1

                    elapsed = (datetime.now() - start_time).total_seconds() / 3600
                    logger.info(f'[{elapsed:.1f}h/{self.duration_hours}h] {exercise.title}')

                    try:
                        _, user_prompt, _ = prompt_builder.build_exercise_prompts(exercise)

                        response_data = await ollama_client.generate(
                            prompt=user_prompt,
                            temperature=self.config.GENERATION_TEMPERATURE,
                            top_p=self.config.GENERATION_TOP_P,
                            max_tokens=self.config.GENERATION_MAX_TOKENS
                        )
                        response_text = response_data.get("text", "")

                        result_dict = ResponseValidator.auto_evaluate(response_text, exercise)

                        result = ExerciseResult(
                            exercise_id=exercise.id,
                            quality_score=result_dict['quality_score'],
                            success=result_dict['success'],
                            timestamp=datetime.now(),
                            patterns_found=result_dict['patterns_found'],
                            patterns_total=result_dict['patterns_total'],
                            regex_matched=result_dict['regex_matched'],
                            regex_total=result_dict['regex_total'],
                            requires_manual_review=result_dict['requires_manual_review'],
                            response_length=len(response_text)
                        )

                        self.session_metrics.add_result(result)

                        status = '[OK]' if result.success else '[ERROR]'
                        logger.info(f'  Score: {result.quality_score:.1f}/10 {status}')

                    except Exception as e:
                        logger.error(f'  Error: {e}')

                    await asyncio.sleep(0.5)

        except KeyboardInterrupt:
            logger.info('\n\nTraining paused by user')

        self.session_metrics.ended_at = datetime.now()
        await self.save_session()

    async def save_session(self):
        """Save session to disk"""
        duration = (self.session_metrics.ended_at - self.session_metrics.started_at).total_seconds() / 3600
        session_file = self.config.TRAINING_LOGS_DIR / f'{self.session_id}.json'

        with open(session_file, 'w') as f:
            json.dump(self.session_metrics.to_dict(), f, indent=2)

        logger.info('\n' + '='*80)
        logger.info('TRAINING SESSION COMPLETE')
        logger.info('='*80)
        logger.info(f'Duration: {duration:.1f} hours')
        logger.info(f'Exercises: {self.session_metrics.total_exercises}')
        logger.info(f'Success rate: {self.session_metrics.success_rate:.1%}')
        logger.info(f'Avg quality: {self.session_metrics.avg_quality_score:.1f}/10')
        logger.info(f'Saved to: {session_file}')
        logger.info('='*80)


async def main():
    trainer = TrainingLoop(duration_hours=12)
    try:
        await trainer.run()
    except Exception as e:
        logger.error(f'Fatal error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('\n\nTraining stopped')
        sys.exit(0)
