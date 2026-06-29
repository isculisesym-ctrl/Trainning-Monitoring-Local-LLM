"""Build training prompts with injected Sr-level corpus."""

from typing import Optional
from .corpus_loader import get_corpus_loader
from .exercise_loader import Exercise, Level
import logging

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Build prompts with Sr-level corpus context injection."""

    def __init__(self, corpus_loader=None):
        self.corpus_loader = corpus_loader or get_corpus_loader()

    def build_exercise_prompt(
        self,
        exercise: Exercise,
        include_corpus: bool = True,
        corpus_keys: Optional[list] = None,
    ) -> str:
        """Build a training prompt for an exercise."""

        corpus_text = ""
        if include_corpus:
            if corpus_keys:
                corpus_text = "\n\n".join(
                    self.corpus_loader.get_corpus_content(key) for key in corpus_keys
                )
            else:
                # Include relevant corpus based on category
                corpus_text = self._get_relevant_corpus(exercise.category)

        system_prompt = self._build_system_prompt(exercise.level, corpus_text)
        user_prompt = self._build_user_prompt(exercise)

        return f"{system_prompt}\n\n{user_prompt}"

    def build_exercise_prompts(self, exercise: Exercise) -> tuple:
        """Build system and user prompts separately."""
        system_prompt = self._build_system_prompt(exercise.level)
        user_prompt = self._build_user_prompt(exercise)
        corpus_text = self._get_relevant_corpus(exercise.category)

        return system_prompt, user_prompt, corpus_text

    @staticmethod
    def _build_system_prompt(level: Level, corpus_context: str = "") -> str:
        """Build system prompt with Sr-level guidelines."""

        level_guidelines = {
            Level.JUNIOR: "You are a junior software developer learning software architecture. Be clear, ask questions.",
            Level.MID: "You are a mid-level software engineer. Show understanding of tradeoffs and decisions.",
            Level.SENIOR: "You are a senior architect. Consider scalability, maintainability, security, and cost. Justify decisions.",
        }

        corpus_part = f"CORPUS CONTEXT:{chr(10)}{corpus_context}" if corpus_context else ""

        base_prompt = f"""You are a software architecture expert training to reach Sr-level expertise.

{level_guidelines.get(level, "")}

Guidelines:
1. Be specific and practical (code examples when applicable)
2. Consider real-world constraints (cost, team size, timeline)
3. Explain WHY, not just WHAT
4. Address security, scalability, and maintainability
5. For Sr-level: Consider failure modes and edge cases

{corpus_part}"""

        return base_prompt.strip()

    @staticmethod
    def _build_user_prompt(exercise: Exercise) -> str:
        """Build user prompt from exercise."""
        return f"""Task: {exercise.title}

{exercise.description}

Provide a comprehensive answer."""

    def _get_relevant_corpus(self, category: str) -> str:
        """Get relevant corpus based on exercise category."""
        # Map categories to corpus keys
        category_to_corpus = {
            "architecture": ["01_architecture_patterns", "04_design_patterns"],
            "scalability": ["02_scalability_design"],
            "security": ["03_security_owasp"],
            "patterns": ["04_design_patterns"],
            "quality": ["05_code_quality"],
        }

        corpus_keys = category_to_corpus.get(category, ["01_architecture_patterns"])

        corpus_parts = []
        for key in corpus_keys:
            try:
                content = self.corpus_loader.get_corpus_content(key)
                corpus_parts.append(content)
            except KeyError:
                logger.warning(f"Corpus key not found: {key}")

        return "\n\n---\n\n".join(corpus_parts)

    def build_evaluation_prompt(self, exercise: Exercise, response: str) -> str:
        """Build prompt for evaluating a response."""
        return f"""Evaluate this response to the exercise.

EXERCISE:
{exercise.title}

EXPECTED PATTERNS:
{", ".join(exercise.expected_patterns)}

RESPONSE:
{response}

EVALUATION CRITERIA:
1. Correctness: Does it accurately address the exercise?
2. Completeness: Does it cover all required patterns?
3. Clarity: Is the explanation clear and understandable?
4. Practicality: Is it practical and applicable?
5. Sr-Level: Does it show Sr-level thinking (tradeoffs, constraints, justification)?

Provide a score (0-10) and feedback."""

    @staticmethod
    def build_checkpoint_prompt(session_report: dict, corpus_text: str) -> str:
        """Build prompt for Claude to audit a training checkpoint."""
        return f"""You are auditing a training session for a model being trained as a Sr-level developer.

CORPUS CONTEXT:
{corpus_text[:2000]}...

SESSION REPORT:
Exercises completed: {session_report.get("total_exercises", 0)}
Success rate: {session_report.get("success_rate", 0):.1%}
Average quality score: {session_report.get("avg_quality_score", 0):.1f}/10

FAILED EXERCISES:
{session_report.get("failed_exercises_summary", "None")}

QUALITY OBSERVATIONS:
{session_report.get("quality_observations", "No notes")}

TASK:
1. Assess if the model is improving towards Sr-level
2. Identify weak areas
3. Suggest focus areas for next training session
4. Recommend adjustments to prompts or exercises

Provide structured feedback that will help improve the model."""

    @staticmethod
    def build_demo_prompt() -> str:
        """Build a demo prompt for testing."""
        return """You are a software architecture expert.

Design a system to handle 10M requests per day with <500ms latency.
Consider: scalability, cost, reliability.

Provide:
1. Architecture diagram (text-based)
2. Component justifications
3. Potential failure points"""
