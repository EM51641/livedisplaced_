from typing import Any
from unittest.mock import Mock

import pytest
from quart import Quart

from src.Context.Service.Exceptions.Passcode import InvalidResetToken
from src.Context.Service.Passcode import ServicePasswordReset
from src.Controllers.Web.reset_password_app import PasswordResetController


class TestPasswordResetController:
    """
    Test forget password controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(ServicePasswordReset)
        app.view_functions["root.web.reset_password_app.controller"] = (
            PasswordResetController.as_view("controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_reset_password_controller_get_status(self, app: Quart):
        """Test forget password controller status."""
        async with app.test_client() as client:
            response = await client.get(
                "/edit-password/f380456b-df20-4d78-9778-f5167d9cf0dd/"
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_reset_password_controller_get_template(
        self, app: Quart, captured_templates: list[Any]
    ):
        """Test forget password controller template."""
        async with app.test_client() as client:
            await client.get("/edit-password/f380456b-df20-4d78-9778-f5167d9cf0dd/")

        template, _ = captured_templates[0]
        assert template.name == "reset_password.html"

    @pytest.mark.asyncio
    async def test_reset_password_controller_get_invalid_token(self, app: Quart):
        """Test forget password controller get invalid token."""

        self._mocked_service.check_valid_reset_token.side_effect = InvalidResetToken()

        async with app.test_client() as client:
            response = await client.get(
                "/edit-password/f380456b-df20-4d78-9778-f5167d9cf0dd/"
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_reset_password_controller_post(self, app: Quart):
        """Test forget password controller post."""
        async with app.test_client() as client:
            response = await client.post(
                "/edit-password/f380456b-df20-4d78-9778-f5167d9cf0dd/",
                form={"password": "123535353", "password_2": "123535353"},
            )

        assert response.status_code == 302
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_reset_password_controller_post_flash_redirects_succesfully(
        self, app: Quart
    ):
        """Test forget password controller post flash redirects successfully."""
        async with app.test_client() as client:
            response = await client.post(
                "/edit-password/f380456b-df20-4d78-9778-f5167d9cf0dd/",
                form={"password": "123535353", "password_2": "123535353"},
                follow_redirects=True,
            )

            data = await response.data

        assert response.status_code == 200
        assert b"Your password has been reset succesfully" in data
        assert b"flash-errors" not in data

    @pytest.mark.asyncio
    async def test_reset_password_controller_post_reset_password_wrong_form(
        self, app: Quart
    ):
        """Test forget password controller post reset password wrong form."""

        async with app.test_client() as client:
            response = await client.post(
                "/edit-password/f380456b-df20-4d78-9778-f5167d9cf0dd/",
                form={"password": "123535353", "password_2": "1235353534"},
                follow_redirects=True,
            )

            data = await response.data

        assert response.status_code == 200
        assert b"flash-errors" in data
        assert b"flash-success" not in data

    @pytest.mark.asyncio
    async def test_reset_password_controller_post_reset_password_invalid_token(
        self, app: Quart
    ):
        """Test forget password controller post reset password wrong form."""

        self._mocked_service.reset_user_password.side_effect = InvalidResetToken()

        async with app.test_client() as client:
            response = await client.post(
                "/edit-password/f380456b-df20-4d78-9778-f5167d9cf0dd/",
                form={"password": "123535353", "password_2": "123535353"},
            )

        assert response.status_code == 404
