import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from src.cache import Cache
from src.config import settings
from src.models import GenerateRequest, GenerateResponse, HealthResponse, ModelInfo, ModelsResponse
from src.ollama_client import OllamaClient, OllamaClientError
from src.utils import generate_id, setup_logging
from src.validators import ValidationError, validate_generate_request

logger = setup_logging(settings.log_level)

cache = Cache()
ollama_client = OllamaClient()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Log startup/shutdown and warn if Ollama is unreachable at boot."""
    logger.info("AI-Platform Gateway starting...")
    if not await ollama_client.check_connection():
        logger.warning("Ollama not connected at startup")
    yield
    logger.info("AI-Platform Gateway shutting down...")


app = FastAPI(
    title="AI-Platform Gateway",
    description="Local LLM Gateway with Semantic Caching",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Report overall health based on Ollama connectivity and cache availability."""
    ollama_connected = await ollama_client.check_connection()
    cache_available = cache.cache_dir.exists()

    status: Literal["healthy", "degraded", "unhealthy"]
    if ollama_connected and cache_available:
        status = "healthy"
    elif cache_available or ollama_connected:
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthResponse(
        status=status,
        ollama_connected=ollama_connected,
        cache_available=cache_available,
        message="All systems operational" if status == "healthy" else "Some services degraded",
    )


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate a completion, transparently serving a cached response on a hit."""
    try:
        request = validate_generate_request(request)

        cached_response = await cache.get(request.prompt)
        if cached_response:
            return GenerateResponse(
                id=generate_id(),
                prompt=request.prompt,
                response=cached_response["response"],
                tokens_input=cached_response["tokens_input"],
                tokens_output=cached_response["tokens_output"],
                tokens_total=cached_response["tokens_input"] + cached_response["tokens_output"],
                mode="cached",
                cached=True,
            )

        async with OllamaClient() as client:
            result = await client.generate(
                prompt=request.prompt,
                temperature=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens,
                stream=False,
            )

        await cache.set(
            request.prompt,
            result["text"],
            result["tokens_input"],
            result["tokens_output"],
        )

        return GenerateResponse(
            id=generate_id(),
            prompt=request.prompt,
            response=result["text"],
            tokens_input=result["tokens_input"],
            tokens_output=result["tokens_output"],
            tokens_total=result["tokens_input"] + result["tokens_output"],
            mode=request.mode.value,
            cached=False,
        )

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except OllamaClientError as e:
        logger.error(f"Ollama error: {e}")
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/stream")
async def stream_generate(request: GenerateRequest) -> StreamingResponse:
    """Stream a completion as Server-Sent Events (``text/event-stream``)."""
    try:
        request = validate_generate_request(request)

        async def generate_chunks() -> AsyncIterator[str]:
            async with OllamaClient() as client:
                async for chunk in client.stream_generate(
                    prompt=request.prompt,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    max_tokens=request.max_tokens,
                ):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        return StreamingResponse(generate_chunks(), media_type="text/event-stream")

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Stream error: {e}")
        raise HTTPException(status_code=500, detail="Streaming failed")


@app.get("/api/models", response_model=ModelsResponse)
async def get_models() -> ModelsResponse:
    """List the models available from the configured Ollama server."""
    try:
        async with OllamaClient() as client:
            models = await client.get_models()

        model_list = [
            ModelInfo(
                name=m.get("name", "unknown"),
                version=m.get("details", {}).get("parameter_size", "unknown"),
                size_gb=m.get("size", 0) / (1024**3),
                quantization=m.get("details", {}).get("quantization_level", "unknown"),
                description="Available model from Ollama",
            )
            for m in models
        ]

        return ModelsResponse(models=model_list, count=len(model_list))

    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=503, detail="Could not retrieve models")


@app.delete("/api/cache")
async def clear_cache() -> dict:
    """Delete every cached response."""
    try:
        await cache.clear()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@app.get("/api/cache/stats")
async def cache_stats() -> dict:
    """Return cache statistics (entry count, directory, TTL)."""
    try:
        return await cache.get_stats()
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last-resort handler returning a JSON error envelope with status 500."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.gateway_host,
        port=settings.gateway_port,
        reload=settings.debug,
    )
