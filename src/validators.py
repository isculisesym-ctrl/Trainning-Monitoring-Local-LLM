import re
from src.models import GenerateRequest


class ValidationError(Exception):
    pass


def validate_prompt(prompt: str) -> str:
    if not prompt or len(prompt.strip()) == 0:
        raise ValidationError("Prompt no puede estar vacío")

    cleaned = " ".join(prompt.split())

    if len(cleaned) > 10000:
        raise ValidationError("Prompt no puede exceder 10,000 caracteres")

    dangerous_patterns = [
        r"ignore previous",
        r"system prompt",
        r"jailbreak"
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, cleaned, re.IGNORECASE):
            raise ValidationError(f"Prompt contiene patrón sospechoso: {pattern}")

    return cleaned


def validate_token_count(count: int) -> bool:
    return 0 < count < 4096


def validate_temperature(value: float) -> float:
    if not 0.0 <= value <= 2.0:
        raise ValidationError("Temperature debe estar entre 0.0 y 2.0")
    return round(value, 2)


def validate_generate_request(request: GenerateRequest) -> GenerateRequest:
    request.prompt = validate_prompt(request.prompt)

    if request.temperature is None:
        from src.config import settings
        request.temperature = settings.temperature
    else:
        request.temperature = validate_temperature(request.temperature)

    if request.top_p is None:
        from src.config import settings
        request.top_p = settings.top_p

    if request.max_tokens is None:
        from src.config import settings
        request.max_tokens = settings.max_tokens

    return request
