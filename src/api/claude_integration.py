"""Claude API integration for training checkpoint audits."""

from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ClaudeCheckpointAuditor:
    """Audit training checkpoints using Claude API."""

    def __init__(self, api_key: Optional[str], model: str = "claude-haiku-4-5-20251001"):
        """Initialize Claude auditor."""
        self.api_key = api_key
        self.model = model
        self.client = None

        if self.api_key:
            try:
                from anthropic import Anthropic

                self.client = Anthropic(api_key=self.api_key)
                logger.info(f"[OK] Claude API initialized: {model}")
            except ImportError:
                logger.warning("anthropic library not installed. Run: pip install anthropic")
            except Exception as e:
                logger.error(f"Failed to initialize Claude API: {e}")

    def is_available(self) -> bool:
        """Check if Claude API is available."""
        return self.client is not None

    def audit_checkpoint(self, checkpoint_report: dict, corpus_text: str) -> Optional[dict]:
        """Audit a training checkpoint using Claude."""
        if not self.is_available():
            logger.warning("Claude API not available. Skipping audit.")
            return None

        try:
            system_prompt = f"""You are a software architecture expert auditing a model's training progress.

The model is being trained to become a Sr-level software architect and developer.

CORPUS (Sr-level reference):
{corpus_text[:3000]}...

Your task:
1. Assess progress towards Sr-level expertise
2. Identify weak areas
3. Recommend focus areas for next sessions
4. Suggest prompt adjustments if needed

Be specific and actionable."""

            user_message = f"""CHECKPOINT AUDIT

Session: {checkpoint_report.get('session_id', 'unknown')}
Exercises completed: {checkpoint_report.get('total_exercises', 0)}
Success rate: {checkpoint_report.get('success_rate', 0):.1%}
Avg quality score: {checkpoint_report.get('avg_quality_score', 0):.1f}/10

Failed exercises: {checkpoint_report.get('failed_exercises_summary', 'None')}

Quality observations: {checkpoint_report.get('quality_observations', 'None')}

Provide feedback on:
1. Is the model improving?
2. What are the weak areas?
3. What should be the focus for next session?
4. Any prompt adjustments recommended?"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
            )

            audit_text = response.content[0].text

            result = {
                "checkpoint_id": checkpoint_report.get("checkpoint_id"),
                "audit_timestamp": datetime.now().isoformat(),
                "audit_feedback": audit_text,
                "model_used": self.model,
                "success": True,
            }

            logger.info("[OK] Checkpoint audit completed")
            return result

        except Exception as e:
            logger.error(f"Failed to audit checkpoint: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def analyze_response_quality(self, exercise_id: str, response: str) -> Optional[dict]:
        """Analyze quality of a single response (optional, expensive)."""
        if not self.is_available():
            return None

        try:
            prompt = f"""Analyze this response to a Sr-level architecture exercise.

EXERCISE ID: {exercise_id}

RESPONSE:
{response[:2000]}

Evaluate:
1. Sr-level thinking? (considers tradeoffs, constraints, scalability)
2. Correctness
3. Completeness
4. Practical applicability

Score 0-10 and provide brief feedback."""

            response_msg = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            return {
                "exercise_id": exercise_id,
                "analysis": response_msg.content[0].text,
            }

        except Exception as e:
            logger.error(f"Failed to analyze response: {e}")
            return None


class ClaudeCheckpointAuditorLocal:
    """Local mock auditor (for testing without API)."""

    def __init__(self):
        logger.info("Using local checkpoint auditor (no Claude API)")

    def is_available(self) -> bool:
        return False

    def audit_checkpoint(self, checkpoint_report: dict, corpus_text: str) -> dict:
        """Generate mock audit."""
        return {
            "checkpoint_id": checkpoint_report.get("checkpoint_id"),
            "audit_timestamp": datetime.now().isoformat(),
            "audit_feedback": f"""Mock Audit (no Claude API configured)

Session exercises: {checkpoint_report.get('total_exercises')}
Success rate: {checkpoint_report.get('success_rate'):.1%}

To enable Claude audits:
1. Set TRAINING_MODE=hybrid in .env.training
2. Set ANTHROPIC_API_KEY in .env.training
3. Restart training

For now, exercise results are logged locally for manual review.""",
            "model_used": "local_mock",
            "success": True,
        }


def get_checkpoint_auditor(api_key: Optional[str], model: str = "claude-haiku-4-5-20251001"):
    """Get checkpoint auditor (Claude or local mock)."""
    if api_key:
        return ClaudeCheckpointAuditor(api_key, model)
    else:
        return ClaudeCheckpointAuditorLocal()
