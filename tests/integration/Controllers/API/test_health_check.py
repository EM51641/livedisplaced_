import pytest
from quart import Quart


@pytest.mark.asyncio
async def test_health_check_get(app: Quart):
    """Test health check controller status."""
    async with app.test_client() as client:
        response = await client.get("/api/v1/health-check")
        data = await response.get_json()
        assert response.status_code == 200
        assert response.content_type == "application/json"
        assert data == {"status": "ok"}
