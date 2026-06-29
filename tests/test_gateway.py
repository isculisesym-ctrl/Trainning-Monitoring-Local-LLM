import pytest
import pytest_asyncio
from httpx import AsyncClient
from src.gateway import app
from src.models import GenerateRequest


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]


@pytest.mark.asyncio
async def test_generate_invalid_prompt(client):
    response = await client.post(
        "/api/generate",
        json={"prompt": "", "mode": "generate"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_request_model(client):
    request = GenerateRequest(
        prompt="Test prompt",
        temperature=0.7,
        max_tokens=100
    )
    assert request.prompt == "Test prompt"
    assert request.temperature == 0.7
    assert request.max_tokens == 100


@pytest.mark.asyncio
async def test_models_endpoint(client):
    response = await client.get("/api/models")
    assert response.status_code in [200, 503]
