from typing import Any
from unittest.mock import Mock

import pytest
from quart import Quart, session
from quart.typing import TestClientProtocol

from src.Context.Service.User import ServiceUpdateAccountPassword
from src.Controllers.Web.User.account_edit_password_app import EditPasswordController


class TestEditPasswordController:
    """
    Test edit password controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(ServiceUpdateAccountPassword)
        app.view_functions["root.web.user.account_edit_password_app.controller"] = (
            EditPasswordController.as_view("controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_edit_password_controller_unauthenticated_get_status(
        self, app: Quart
    ):
        """Test edit password controller get status."""
        async with app.test_client() as client:
            response = await client.get("/user/edit-password/")
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_edit_password_controller_unauthenticated_get_location(
        self, app: Quart
    ):
        """Test edit password controller get location."""
        async with app.test_client() as client:
            response = await client.get("/user/edit-password/")
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_edit_password_controller_get_status(
        self, authenticated_client: TestClientProtocol
    ):
        """Test edit password controller get status."""
        response = await authenticated_client.get("/user/edit-password/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_edit_password_controller_get_template(
        self, authenticated_client: TestClientProtocol, captured_templates: list[Any]
    ):
        """Test edit password controller get template."""
        await authenticated_client.get("/user/edit-password/")

        template, _ = captured_templates[0]
        assert template.name == "update_password.html"

    @pytest.mark.asyncio
    async def test_edit_password_controller_post_unauthenticated_status(
        self, app: Quart
    ):
        """Test edit password controller post status."""
        async with app.test_client() as client:
            response = await client.post(
                "/user/edit-password/",
                form={
                    "current_password": "1dadaa234456778",
                    "new_password": "1dadaa234456779",
                    "new_password_2": "1dadaa234456779",
                },
            )
        assert response.status_code == 302
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_edit_password_controller_post_status(
        self, authenticated_client: TestClientProtocol
    ):
        """Test edit password controller post status."""
        response = await authenticated_client.post(
            "/user/edit-password/",
            form={
                "current_password": "1dadaa234456778",
                "new_password": "1dadaa234456779",
                "new_password_2": "1dadaa234456779",
            },
        )
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_edit_password_controller_post_location(
        self, authenticated_client: TestClientProtocol
    ):
        """Test edit password controller post redirects successfully."""
        response = await authenticated_client.post(
            "/user/edit-password/",
            form={
                "current_password": "1dadaa234456778",
                "new_password": "1dadaa234456779",
                "new_password_2": "1dadaa234456779",
            },
        )
        assert response.location == "/user/settings/"

    @pytest.mark.asyncio
    async def test_edit_password_controller_post_succesfull_flash(
        self, authenticated_client: TestClientProtocol
    ):
        """Test edit password controller post flash redirects successfully."""
        await authenticated_client.post(
            "/user/edit-password/",
            form={
                "current_password": "1dadaa234456778",
                "new_password": "1dadaa234456779",
                "new_password_2": "1dadaa234456779",
            },
        )

        flashes_data = session.pop("_flashes")
        assert ("flash-success", "Password updated successfully.") in flashes_data

    @pytest.mark.asyncio
    async def test_edit_password_controller_post_failure_flash(
        self, authenticated_client: TestClientProtocol
    ):
        """Test edit password controller post flash redirects successfully."""
        await authenticated_client.post(
            "/user/edit-password/",
            form={
                "current_password": "1dadaa234456778",
                "new_password": "1dadaa234456779",
                "new_password_2": "1dadaa234456719",
            },
        )
        flashes_data = session.pop("_flashes")
        assert "flash-errors" in set(x[0] for x in flashes_data)
