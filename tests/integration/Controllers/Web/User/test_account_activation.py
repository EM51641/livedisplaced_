from unittest.mock import Mock

import pytest
from quart import Quart

from src.Context.Service.Exceptions.Passcode import InvalidActivationToken
from src.Context.Service.Passcode import ServiceActivateUser
from src.Controllers.Web.User.account_activation_app import UserActivationController


class TestUserActivationController:
    """
    Test User Activation Controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(ServiceActivateUser)
        app.view_functions["root.web.user.account_activation_app.controller"] = (
            UserActivationController.as_view("controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_activate_user_controller_get_status(self, app: Quart):
        """Test forget password controller status."""
        async with app.test_client() as client:
            response = await client.get(
                "/user/activation/03f97ca3-aaa8-4a5f-b14c-cbf51646ddb0/"
            )
        assert response.status_code == 302
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_activate_user_controller_get_location(self, app: Quart):
        """Test forget password controller post."""
        async with app.test_client() as client:
            response = await client.get(
                "/user/activation/03f97ca3-aaa8-4a5f-b14c-cbf51646ddb0/"
            )
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_activate_user_controller_get_succesfull_flash(self, app: Quart):
        """Test forget password controller post flash redirects successfully."""
        async with app.test_client() as client:
            response = await client.get(
                "/user/activation/03f97ca3-aaa8-4a5f-b14c-cbf51646ddb0/",
                follow_redirects=True,
            )
            data = await response.data
        assert b"Account activated successfully. Please login." in data

    @pytest.mark.asyncio
    async def test_activate_user_controller_get_invalid_token(self, app: Quart):
        """Test forget password controller post."""
        self._mocked_service.activate_user.side_effect = InvalidActivationToken(
            "Invalid Token"
        )
        async with app.test_client() as client:
            response = await client.get(
                "/user/activation/03f97ca3-aaa8-4a5f-b14c-cbf51646ddb0/"
            )
        assert response.status_code == 404
