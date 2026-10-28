import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_health():
    """Verify root /health endpoint returns ok (TECH_SPEC §1)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data


@pytest.mark.asyncio
async def test_api_health():
    """Verify /api/health endpoint returns ok."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_trailing_slash_served_without_redirect():
    """Regression: behind the Vercel proxy a 307 drops the Authorization header (agents got logged out)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for path in ("/health", "/health/"):
            res = await client.get(path)
            assert res.status_code == 200, path
        res = await client.get("/cases/")
        assert res.status_code == 401  # reaches the route (auth), not a 307 redirect
        assert (await client.get("/does-not-exist/")).status_code == 404
