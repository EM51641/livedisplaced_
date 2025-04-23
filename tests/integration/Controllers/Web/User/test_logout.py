import pytest
from quart import Quart, session
from quart.typing import TestClientProtocol


class TestLogoutController:
    """
    Test logout controller.
    """

    @pytest.mark.asyncio
    async def test_logout_controller_unauthenticated_post_status(self, app: Quart):
        """Test edit password controller get status."""
        async with app.test_client() as client:
            response = await client.post("/user/logout/")
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_logout_controller_unauthenticated_post_location(self, app: Quart):
        """Test edit password controller get status."""
        async with app.test_client() as client:
            response = await client.post("/user/logout/")
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_logout_controller_post_unauthenticated_client_flash_msg(
        self, app: Quart
    ):
        """Test logout controller with authenticated client."""
        async with app.test_client() as client:
            await client.post("/user/logout/")
            flashes_data = session.get("_flashes")
        assert flashes_data is None

    @pytest.mark.asyncio
    async def test_logout_controller_post_authenticated_client_status(
        self, authenticated_client: TestClientProtocol
    ):
        """Test logout controller with authenticated client."""

        response = await authenticated_client.post("/user/logout/")
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_logout_controller_post_authenticated_client_location(
        self, authenticated_client: TestClientProtocol
    ):
        """Test logout controller with authenticated client."""

        response = await authenticated_client.post("/user/logout/")
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_logout_controller_post_authenticated_client_flash_msg(
        self, authenticated_client: TestClientProtocol
    ):
        """Test logout controller with authenticated client."""

        await authenticated_client.post("/user/logout/", follow_redirects=True)
        flashes_data = session.pop("_flashes")
        assert ("flash-success", "Logged out succesfully") in flashes_data
