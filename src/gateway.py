from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
from datetime import datetime

from src.config import settings
from src.models import (
    GenerateRequest, GenerateResponse, HealthResponse,
    ModelsResponse, ModelInfo
)
from src.validators import validate_generate_request, ValidationError
from src.ollama_client import OllamaClient, OllamaClientError
from src.cache import Cache
from src.utils import setup_logging, generate_id

logger = setup_logging(settings.log_level)

app = FastAPI(
    title="AI-Platform Gateway",
    description="Local LLM Gateway with Semantic Caching",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = Cache()
ollama_client = OllamaClient()


@app.on_event("startup")
async def startup_event():
    logger.info("AI-Platform Gateway starting...")
    is_connected = await ollama_client.check_connection()
    if not is_connected:
        logger.warning("Ollama not connected at startup")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("AI-Platform Gateway shutting down...")


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    ollama_connected = await ollama_client.check_connection()
    cache_available = cache.cache_dir.exists()

    status = "healthy" if ollama_connected and cache_available else "degraded"

    return HealthResponse(
        status=status,
        ollama_connected=ollama_connected,
        cache_available=cache_available,
        message="All systems operational" if status == "healthy" else "Some services degraded"
    )


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    try:
        request = validate_generate_request(request)

        cached_response = await cache.get(request.prompt)
        if cached_response and request.mode != "generate":
            return GenerateResponse(
                id=generate_id(),
                prompt=request.prompt,
                response=cached_response["response"],
                tokens_input=cached_response["tokens_input"],
                tokens_output=cached_response["tokens_output"],
                tokens_total=cached_response["tokens_input"] + cached_response["tokens_output"],
                mode="cached",
                cached=True
            )

        async with OllamaClient() as client:
            result = await client.generate(
                prompt=request.prompt,
                temperature=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens,
                stream=False
            )

        await cache.set(
            request.prompt,
            result["text"],
            result["tokens_input"],
            result["tokens_output"]
        )

        return GenerateResponse(
            id=generate_id(),
            prompt=request.prompt,
            response=result["text"],
            tokens_input=result["tokens_input"],
            tokens_output=result["tokens_output"],
            tokens_total=result["tokens_input"] + result["tokens_output"],
            mode=request.mode,
            cached=False
        )

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except OllamaClientError as e:
        logger.error(f"Ollama error: {e}")
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/stream")
async def stream_generate(request: GenerateRequest):
    try:
        request = validate_generate_request(request)

        async def generate_chunks():
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
async def get_models():
    try:
        async with OllamaClient() as client:
            models = await client.get_models()

        model_list = [
            ModelInfo(
                name=m.get("name", "unknown"),
                version=m.get("details", {}).get("parameter_size", "unknown"),
                size_gb=m.get("size", 0) / (1024**3),
                quantization=m.get("details", {}).get("quantization_level", "unknown"),
                description="Available model from Ollama"
            )
            for m in models
        ]

        return ModelsResponse(models=model_list, count=len(model_list))

    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=503, detail="Could not retrieve models")


@app.delete("/api/cache")
async def clear_cache():
    try:
        await cache.clear()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@app.get("/api/cache/stats")
async def cache_stats():
    try:
        stats = await cache.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "code": "INTERNAL_ERROR",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.gateway_host,
        port=settings.gateway_port,
        reload=settings.debug
    )
