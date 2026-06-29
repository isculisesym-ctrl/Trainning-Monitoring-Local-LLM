import re

from src.config import settings
from src.models import GenerateRequest


class ValidationError(Exception):
    pass


DANGEROUS_PATTERNS = [
    r"ignore previous",
    r"system prompt",
    r"jailbreak",
]


def validate_prompt(prompt: str) -> str:
    """Normalize whitespace and reject empty, over-long, or unsafe prompts.

    Returns the cleaned prompt. Raises ``ValidationError`` for empty/blank
    input, prompts over 10,000 characters, or known prompt-injection patterns.
    """
    if not prompt or len(prompt.strip()) == 0:
        raise ValidationError("Prompt no puede estar vacío")

    cleaned = " ".join(prompt.split())

    if len(cleaned) > 10000:
        raise ValidationError("Prompt no puede exceder 10,000 caracteres")

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            raise ValidationError(f"Prompt contiene patrón sospechoso: {pattern}")

    return cleaned


def validate_token_count(count: int) -> bool:
    """Return True if ``count`` is a valid token count (0 < count < 4096)."""
    return 0 < count < 4096


def validate_temperature(value: float) -> float:
    """Clamp-check temperature to [0.0, 2.0] and round to 2 decimals."""
    if not 0.0 <= value <= 2.0:
        raise ValidationError("Temperature debe estar entre 0.0 y 2.0")
    return round(value, 2)


def validate_generate_request(request: GenerateRequest) -> GenerateRequest:
    """Validate the prompt and fill missing generation params from settings.

    Explicit values are preserved (including ``temperature=0.0``); only ``None``
    fields fall back to configured defaults.
    """
    request.prompt = validate_prompt(request.prompt)

    if request.temperature is None:
        request.temperature = settings.temperature
    else:
        request.temperature = validate_temperature(request.temperature)

    if request.top_p is None:
        request.top_p = settings.top_p

    if request.max_tokens is None:
        request.max_tokens = settings.max_tokens

    return request
