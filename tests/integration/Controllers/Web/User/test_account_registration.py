from typing import Any
from unittest.mock import Mock

import pytest
from quart import Quart, session
from quart.typing import TestClientProtocol

from src.Context.Service.Exceptions.User import EmailAlreadyUsed
from src.Context.Service.User import ServiceRegistrationUser
from src.Controllers.Web.User.account_registration_app import UserRegistrationController


class TestUserRegistrationController:
    """
    Test register account controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(ServiceRegistrationUser)
        app.view_functions["root.web.user.account_registration_app.controller"] = (
            UserRegistrationController.as_view("controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_account_registration_controller_unauthenticated_get_status(
        self, client: TestClientProtocol
    ):
        """Test register account controller get status."""
        response = await client.get("/user/register/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_account_registration_controller_get_template(
        self, client: TestClientProtocol, captured_templates: list[Any]
    ):
        """Test register account controller get template."""
        await client.get("/user/register/")
        template, _ = captured_templates[0]
        assert template.name == "register.html"

    @pytest.mark.asyncio
    async def test_account_registration_controller_post_unauthenticated_status(
        self, client: TestClientProtocol
    ):
        """Test register account controller post status."""
        response = await client.post(
            "/user/register/",
            form={
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "password": "1dadaa234456779",
                "password_2": "1dadaa234456779",
                "agree": True,
            },
        )
        assert response.status_code == 302
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_account_registration_controller_post_unauthenticated_incorrect_form(
        self, client: TestClientProtocol
    ):
        """Test register account controller post status."""
        response = await client.post(
            "/user/register/",
            form={
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "password": "1dadaa234456779",
                "password_2": "1dadaa23445677",
            },
        )

        flashes_data = session.pop("_flashes")
        assert {flash[0] for flash in flashes_data} == {"flash-errors"}
        assert response.status_code == 302
        assert response.location == "/user/register/"

    @pytest.mark.asyncio
    async def test_account_registration_controller_post_unauthenticated_already_used_email(
        self, client: TestClientProtocol
    ):
        """Test register account controller post status."""
        self._mocked_service.register_user.side_effect = EmailAlreadyUsed()
        response = await client.post(
            "/user/register/",
            form={
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "password": "1dadaa234456779",
                "password_2": "1dadaa234456779",
                "agree": True,
            },
        )

        flashes_data = session.pop("_flashes")
        assert [("flash-errors", "This email is already in use.")] == flashes_data
        assert response.status_code == 302
        assert response.location == "/user/register/"

    @pytest.mark.asyncio
    async def test_account_registration_controller_post_unauthenticate_succesfull_flash(
        self, client: TestClientProtocol
    ):
        """Test register account controller post flash redirects successfully."""
        await client.post(
            "/user/register/",
            form={
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "password": "1dadaa234456779",
                "password_2": "1dadaa234456779",
                "agree": True,
            },
        )

        flashes_data = session.pop("_flashes")
        assert (
            "flash-success",
            "An activation email should be sent to your email address. Please check your inbox.",
        ) in flashes_data

    @pytest.mark.asyncio
    async def test_account_registration_controller_get_authenticated_status(
        self, authenticated_client: TestClientProtocol
    ):
        """Test register account controller post flash redirects successfully."""
        response = await authenticated_client.get("/user/register/")
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_account_registration_controller_get_authenticated_location(
        self, authenticated_client: TestClientProtocol
    ):
        """Test register account controller post flash redirects successfully."""
        response = await authenticated_client.get("/user/register/")
        assert response.location == "/"
