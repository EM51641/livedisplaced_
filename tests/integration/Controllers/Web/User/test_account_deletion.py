from unittest.mock import Mock

import pytest
from quart import Quart, session
from quart.typing import TestClientProtocol

from src.Context.Service.User import ServiceDeleteAccount
from src.Controllers.Web.User.account_deletion_app import DeleteController


class TestDeleteController:
    """
    Test User Activation Controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(ServiceDeleteAccount)
        app.view_functions["root.web.user.account_deletion_app.controller"] = (
            DeleteController.as_view("controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_delete_user_controller_post_unauthenticated_status(self, app: Quart):
        """Test forget password controller status."""
        async with app.test_client() as client:
            response = await client.post("/user/delete/")
        assert response.status_code == 302
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_delete_user_controller_post_status(
        self, authenticated_client: TestClientProtocol
    ):
        """Test forget password controller status."""
        response = await authenticated_client.post("/user/delete/")
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_delete_user_controller_post_location(
        self, authenticated_client: TestClientProtocol
    ):
        """Test forget password controller post."""
        response = await authenticated_client.post("/user/delete/")
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_delete_user_controller_post_succesfull_flash(
        self, authenticated_client: TestClientProtocol
    ):
        """Test forget password controller post flash redirects successfully."""
        await authenticated_client.post("/user/delete/", follow_redirects=True)
        flashes_data = session.pop("_flashes")
        assert ("flash-success", "Account deleted successfully.") in flashes_data
