from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class GenerationModeEnum(str, Enum):
    GENERATE = "generate"
    STREAM = "stream"
    CACHED = "cached"


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000, description="Prompt para el modelo")
    mode: GenerationModeEnum = Field(
        default=GenerationModeEnum.GENERATE, description="Modo: generate, stream, o cached"
    )
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Control de creatividad")
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Nucleus sampling")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4096, description="Máximo de tokens")

    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "Write a Python function to sort a list",
                "mode": "generate",
                "temperature": 0.7,
                "max_tokens": 500,
            }
        }
    }


class TokenCountRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto para contar tokens")


class GenerateResponse(BaseModel):
    id: str = Field(..., description="ID único de la generación")
    prompt: str
    response: str
    tokens_input: int
    tokens_output: int
    tokens_total: int
    mode: str
    cached: bool = Field(default=False, description="¿Fue obtenido de caché?")


class StreamChunk(BaseModel):
    chunk_id: int
    data: str
    finished: bool = False


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    ollama_connected: bool
    cache_available: bool
    message: str = ""


class ModelInfo(BaseModel):
    name: str
    version: str
    size_gb: float
    quantization: str
    description: str


class ModelsResponse(BaseModel):
    models: List[ModelInfo]
    count: int


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Descripción del error")
    code: str = Field(..., description="Código de error")
    details: Optional[Dict[str, Any]] = None
