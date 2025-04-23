from typing import Any
from unittest.mock import Mock

import pytest
from quart import Quart

from src.Context.Service.Passcode import ServiceRequestPasswordReset
from src.Controllers.Web.forget_password_app import ForgetPasswordController


class TestForgetPasswordController:
    """
    Test forget password controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(ServiceRequestPasswordReset)
        app.view_functions["root.web.forget_password_app.controller"] = (
            ForgetPasswordController.as_view("controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_forget_password_controller_status(self, app: Quart):
        """Test forget password controller status."""
        async with app.test_client() as client:
            response = await client.get("/forget-password/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_forget_password_controller_template(
        self, app: Quart, captured_templates: list[Any]
    ):
        """Test forget password controller template."""
        async with app.test_client() as client:
            await client.get("/forget-password/")

        template, _ = captured_templates[0]
        assert template.name == "password_lost_request.html"

    @pytest.mark.asyncio
    async def test_forget_password_controller_post(self, app: Quart):
        """Test forget password controller post."""
        async with app.test_client() as client:
            response = await client.post(
                "/forget-password/", data={"email": "johndoe@example.con"}
            )

            assert response.status_code == 302
            assert response.location == "/forget-password/"

    @pytest.mark.asyncio
    async def test_forget_password_controller_post_flash_redirects_succesfully(
        self, app: Quart
    ):
        """Test forget password controller post flash redirects successfully."""
        async with app.test_client() as client:
            response = await client.post(
                "/forget-password/",
                form={"email": "johndoe@example.com"},
                follow_redirects=True,
            )

            data = await response.data

        assert response.status_code == 200
        assert b"An email to reset your password will be sent to you shortly" in data
        assert b"flash-errors" not in data

    @pytest.mark.asyncio
    async def test_forget_password_controller_post_reset_password_wrong_form(
        self, app: Quart
    ):
        """Test forget password controller post reset password wrong form."""

        async with app.test_client() as client:
            response = await client.post(
                "/forget-password/",
                form={"email": "johndoeexample.com"},
                follow_redirects=True,
            )

            data = await response.data

        assert response.status_code == 200
        assert b"flash-errors" in data
        assert b"flash-success" not in data
