from typing import Any
from unittest.mock import Mock

import pytest
from quart import Quart
from quart.typing import TestClientProtocol

from src.Context.Service.Exceptions.User import (
    UserAccountNotActivated,
    UserAccountNotFound,
)
from src.Context.Service.User import ServiceLogin
from src.Controllers.Web.User.account_login_app import UserLoginController


class TestLoginController:
    """
    Test login controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(ServiceLogin)
        app.view_functions["root.web.user.account_login_app.controller"] = (
            UserLoginController.as_view("controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_login_controller_unauthenticated_get_status(self, app: Quart):
        """Test login controller get location."""
        async with app.test_client() as client:
            response = await client.get("/user/login/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_login_controller_unauthenticated_get_template(
        self, app: Quart, captured_templates: list[Any]
    ):
        """Test login controller get template."""
        async with app.test_client() as client:
            await client.get("/user/login/")
        template, _ = captured_templates[0]
        assert template.name == "login.html"

    @pytest.mark.asyncio
    async def test_login_controller_post_unauthenticated_status(self, app: Quart):
        """Test login controller post status."""
        async with app.test_client() as client:
            response = await client.post(
                "/user/login/",
                form={
                    "email": "johndoe@example.com",
                    "password": "1dadaa234456778",
                },
            )
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_login_controller_post_unauthenticated_location(self, app: Quart):
        """Test login controller post status."""
        async with app.test_client() as client:
            response = await client.post(
                "/user/login/",
                form={
                    "email": "johndoe@example.com",
                    "password": "1dadaa234456778",
                },
            )
        assert response.location == "/"

    @pytest.mark.asyncio
    async def test_login_controller_post_unauthenticated_form_validation_failure_status(
        self, app: Quart
    ):
        """Test login controller post status."""
        async with app.test_client() as client:
            response = await client.post(
                "/user/login/",
                form={
                    "email": "johndoeexample.com",
                    "password": "1dadaa234456778",
                },
            )
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_login_controller_post_unauthenticated_form_validation_failure_location(
        self, app: Quart
    ):
        """Test login controller post status."""
        async with app.test_client() as client:
            response = await client.post(
                "/user/login/",
                form={
                    "email": "johndoeexample.com",
                    "password": "1dadaa234456778",
                },
            )
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_login_controller_post_unauthenticated_form_validation_failure_errors(
        self, app: Quart
    ):
        """Test login controller post status."""
        async with app.test_client() as client:
            response = await client.post(
                "/user/login/",
                form={
                    "email": "johndoeexample",
                    "password": "1dadaa234456778",
                },
                follow_redirects=True,
            )
            data = await response.data

        assert b"flash-error" in data
        assert b"flash-success" not in data

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception", [UserAccountNotActivated(), UserAccountNotFound()]
    )
    async def test_login_controller_post_unauthenticated_service_exception_status(
        self, exception: Exception, app: Quart
    ):
        """Test login controller post redirects successfully."""

        self._mocked_service.login.side_effect = exception
        async with app.test_client() as client:
            response = await client.post(
                "/user/login/",
                form={
                    "email": "johndoe@example.com",
                    "password": "1dadaa234456778",
                },
            )

        assert response.status_code == 302

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception", [UserAccountNotActivated(), UserAccountNotFound()]
    )
    async def test_login_controller_post_unauthenticated_service_exception_location(
        self, exception: Exception, app: Quart
    ):
        """Test login controller post redirects successfully."""

        self._mocked_service.login.side_effect = exception
        async with app.test_client() as client:
            response = await client.post(
                "/user/login/",
                form={
                    "email": "johndoe@example.com",
                    "password": "1dadaa234456778",
                },
            )

        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "expected_flash_msg, exception",
        [
            (
                b"Your account is not activated yet. Please check your email.",
                UserAccountNotActivated(),
            ),
            (b"Incorrect email and/or password", UserAccountNotFound()),
        ],
    )
    async def test_login_controller_post_unauthenticated_service_exception_redirect_flash_messages(
        self, expected_flash_msg: bytes, exception: Exception, app: Quart
    ):
        """Test login controller post redirects successfully."""

        self._mocked_service.login.side_effect = exception
        async with app.test_client() as client:
            response = await client.post(
                "/user/login/",
                form={
                    "email": "johndoe@example.com",
                    "password": "1dadaa234456778",
                },
                follow_redirects=True,
            )
            data = await response.data

        assert b"flash-error" in data
        assert b"flash-success" not in data

        assert expected_flash_msg in data

    async def test_login_controller_get_authenticated_client_status(
        self, authenticated_client: TestClientProtocol
    ):
        """Test login controller with authenticated client."""

        response = await authenticated_client.get("/user/login/")
        assert response.status_code == 302

    async def test_login_controller_get_authenticated_client_location(
        self, authenticated_client: TestClientProtocol
    ):
        """Test login controller with authenticated client."""

        response = await authenticated_client.get("/user/login/")
        assert response.location == "/"
