"""Validators for corpus and exercises."""

import re
from typing import List, Tuple
from .exercise_loader import Exercise, Level
import logging

logger = logging.getLogger(__name__)


class CorpusValidator:
    """Validate corpus content."""

    @staticmethod
    def validate_markdown(content: str) -> Tuple[bool, List[str]]:
        """Validate markdown structure."""
        issues = []

        if not content or len(content) < 100:
            issues.append("Content too short (< 100 chars)")

        if not any(line.startswith("#") for line in content.split("\n")):
            issues.append("Missing headers (# title)")

        # Check for code blocks
        code_blocks = re.findall(r"```", content)
        if len(code_blocks) % 2 != 0:
            issues.append("Mismatched code block markers")

        return len(issues) == 0, issues

    @staticmethod
    def validate_size(content: str, min_kb: int = 1) -> Tuple[bool, str]:
        """Validate corpus size."""
        size_kb = len(content) / 1024
        if size_kb < min_kb:
            return False, f"Content too small: {size_kb:.1f}KB (min {min_kb}KB)"
        return True, f"Size OK: {size_kb:.1f}KB"

    @staticmethod
    def validate_readability(content: str, max_line_length: int = 120) -> Tuple[bool, List[str]]:
        """Check readability metrics."""
        issues = []

        long_lines = [
            (i + 1, line)
            for i, line in enumerate(content.split("\n"))
            if len(line) > max_line_length and not line.startswith("#")
        ]

        if long_lines:
            issues.append(f"Found {len(long_lines)} lines > {max_line_length} chars (readability)")

        return len(issues) == 0, issues


class ExerciseValidator:
    """Validate exercises."""

    @staticmethod
    def validate_structure(exercise: Exercise) -> Tuple[bool, List[str]]:
        """Validate exercise structure."""
        issues = []

        if not exercise.id:
            issues.append("Missing 'id'")

        if not exercise.title or len(exercise.title) < 5:
            issues.append("Title too short or missing")

        if not exercise.description or len(exercise.description) < 10:
            issues.append("Description too short or missing")

        if not exercise.expected_patterns:
            issues.append("Missing 'expected_patterns'")

        if not exercise.auto_eval_regex:
            issues.append("Missing 'auto_eval_regex'")

        return len(issues) == 0, issues

    @staticmethod
    def validate_id_format(exercise_id: str) -> Tuple[bool, str]:
        """Validate exercise ID format."""
        # Format: category_level_nnn (e.g., arch_junior_001)
        pattern = r"^[a-z_]+_(junior|mid|senior)_\d{3}$"

        if re.match(pattern, exercise_id):
            return True, "ID format valid"
        else:
            return False, f"ID format invalid: {exercise_id}. Expected: category_level_nnn"

    @staticmethod
    def validate_patterns(patterns: List[str]) -> Tuple[bool, List[str]]:
        """Validate expected patterns."""
        issues = []

        if len(patterns) == 0:
            issues.append("No expected patterns")

        for pattern in patterns:
            if not isinstance(pattern, str) or len(pattern) < 3:
                issues.append(f"Invalid pattern: {pattern}")

        return len(issues) == 0, issues

    @staticmethod
    def validate_regex(regex_patterns: List[str]) -> Tuple[bool, List[str]]:
        """Validate regex patterns."""
        issues = []

        for regex_pattern in regex_patterns:
            try:
                re.compile(regex_pattern)
            except re.error as e:
                issues.append(f"Invalid regex pattern '{regex_pattern}': {e}")

        return len(issues) == 0, issues

    @classmethod
    def validate_complete(cls, exercise: Exercise) -> Tuple[bool, List[str]]:
        """Validate exercise completely."""
        all_issues = []

        # Structure validation
        valid, issues = cls.validate_structure(exercise)
        all_issues.extend(issues)

        # ID format validation
        valid, message = cls.validate_id_format(exercise.id)
        if not valid:
            all_issues.append(message)

        # Pattern validation
        valid, issues = cls.validate_patterns(exercise.expected_patterns)
        all_issues.extend([f"Pattern: {issue}" for issue in issues])

        # Regex validation
        valid, issues = cls.validate_regex(exercise.auto_eval_regex)
        all_issues.extend([f"Regex: {issue}" for issue in issues])

        return len(all_issues) == 0, all_issues


class ResponseValidator:
    """Validate model responses to exercises."""

    @staticmethod
    def check_patterns(response: str, patterns: List[str]) -> Tuple[int, List[str]]:
        """Check if response contains expected patterns."""
        found_patterns = []

        for pattern in patterns:
            # Case-insensitive substring search
            if pattern.lower() in response.lower():
                found_patterns.append(pattern)

        return len(found_patterns), found_patterns

    @staticmethod
    def check_regex(response: str, regex_patterns: List[str]) -> Tuple[int, List[str]]:
        """Check if response matches regex patterns."""
        matched_patterns = []

        for regex_pattern in regex_patterns:
            try:
                if re.search(regex_pattern, response):
                    matched_patterns.append(regex_pattern)
            except re.error:
                logger.warning(f"Invalid regex: {regex_pattern}")

        return len(matched_patterns), matched_patterns

    @staticmethod
    def calculate_quality_score(
        response: str,
        exercise: Exercise,
        pattern_weight: float = 0.3,
        regex_weight: float = 0.3,
        length_weight: float = 0.2,
        clarity_weight: float = 0.2,
    ) -> Tuple[float, dict]:
        """Calculate quality score (0-10)."""

        metrics = {}

        # Pattern matching score
        found_patterns, matched = ResponseValidator.check_patterns(
            response, exercise.expected_patterns
        )
        pattern_score = (found_patterns / len(exercise.expected_patterns)) if exercise.expected_patterns else 1.0
        metrics["pattern_score"] = pattern_score

        # Regex matching score
        matched_regex, _ = ResponseValidator.check_regex(response, exercise.auto_eval_regex)
        regex_score = (matched_regex / len(exercise.auto_eval_regex)) if exercise.auto_eval_regex else 1.0
        metrics["regex_score"] = regex_score

        # Length score (longer = more thoughtful, but not infinitely)
        # Target: 300-1000 chars, max at 800
        length = len(response)
        if length < 100:
            length_score = length / 100 * 0.5  # Max 0.5 for short responses
        elif length < 800:
            length_score = 1.0
        else:
            length_score = 1.0  # Don't penalize verbose

        metrics["length_score"] = length_score

        # Clarity score (based on sentence complexity)
        # Simple heuristic: avg sentence length 10-25 words is good
        sentences = response.split(".")
        avg_words = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        clarity_score = 1.0
        if avg_words > 50:  # Too complex
            clarity_score = 0.7
        elif avg_words < 5:  # Too simple
            clarity_score = 0.8

        metrics["clarity_score"] = clarity_score
        metrics["avg_words_per_sentence"] = avg_words

        # Weighted total
        total_score = (
            pattern_score * pattern_weight
            + regex_score * regex_weight
            + length_score * length_weight
            + clarity_score * clarity_weight
        )

        # Scale to 0-10
        final_score = total_score * 10
        return final_score, metrics

    @staticmethod
    def auto_evaluate(response: str, exercise: Exercise) -> dict:
        """Perform automatic evaluation of response."""

        score, metrics = ResponseValidator.calculate_quality_score(response, exercise)

        pattern_count, found_patterns = ResponseValidator.check_patterns(
            response, exercise.expected_patterns
        )
        regex_count, matched_regex = ResponseValidator.check_regex(response, exercise.auto_eval_regex)

        result = {
            "exercise_id": exercise.id,
            "quality_score": round(score, 1),
            "success": score >= 6.0,  # Passing threshold
            "metrics": metrics,
            "patterns_found": pattern_count,
            "patterns_total": len(exercise.expected_patterns),
            "regex_matched": regex_count,
            "regex_total": len(exercise.auto_eval_regex),
            "requires_manual_review": exercise.manual_eval_required or score < 5.0,
        }

        return result
