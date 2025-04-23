from typing import Any
from unittest.mock import Mock

import pytest
from quart import Quart
from quart.typing import TestClientProtocol

from src.Context.Service.TermsOfUse import UserComplianceService
from src.Controllers.Web.terms_of_use_app import ComplyController


class TestTermsOfUseController:
    """
    Test terms of use controller.
    """

    @pytest.mark.asyncio
    async def test_privacy_policy_controller_get_status(self, app: Quart):
        """Test forget password controller status."""
        async with app.test_client() as client:
            response = await client.get("/terms/privacy-policy")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_privacy_policy_controller_get_template(
        self, app: Quart, captured_templates: list[Any]
    ):
        """Test forget password controller template."""
        async with app.test_client() as client:
            await client.get("/terms/privacy-policy")

        template, _ = captured_templates[0]
        assert template.name == "privacy_policy.html"

    @pytest.mark.asyncio
    async def test_terms_of_use_controller_get_status(self, app: Quart):
        """Test forget password controller status."""
        async with app.test_client() as client:
            response = await client.get("/terms/terms-of-use")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_terms_of_use_controller_get_template(
        self, app: Quart, captured_templates: list[Any]
    ):
        """Test forget password controller template."""
        async with app.test_client() as client:
            await client.get("/terms/terms-of-use")

        template, _ = captured_templates[0]
        assert template.name == "terms_of_use.html"


class TestComplyController:
    """
    Test comply controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(UserComplianceService)
        app.view_functions["root.web.terms_app.compliance_controller"] = (
            ComplyController.as_view("compliance_controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_comply_controller_non_logged_in_get_redirect(self, app: Quart):
        """Test comply controller status."""
        async with app.test_client() as client:
            response = await client.get("/terms/comply")

        assert response.status_code == 302
        assert response.location == "/user/login/"

    @pytest.mark.asyncio
    async def test_comply_controller_get_status(
        self, authenticated_client: TestClientProtocol
    ):
        """Test comply controller status."""
        response = await authenticated_client.get("/terms/comply")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_comply_controller_get_template(
        self, authenticated_client: TestClientProtocol, captured_templates: list[Any]
    ):
        """Test comply controller template."""
        await authenticated_client.get("/terms/comply")

        template, _ = captured_templates[0]
        assert template.name == "compliance_form.html"

    @pytest.mark.asyncio
    async def test_comply_controller_post_agreed_redirect(
        self, authenticated_client: TestClientProtocol
    ):
        """Test comply controller get redirect."""
        response = await authenticated_client.post(
            "/terms/comply", form={"agree": True}
        )

        assert response.status_code == 302
        assert response.location == "/"

    @pytest.mark.asyncio
    async def test_comply_controller_post_not_agreed_redirect(
        self, authenticated_client: TestClientProtocol
    ):
        """Test comply controller get redirect if not agreed."""

        response = await authenticated_client.post(
            "/terms/comply", follow_redirects=True
        )

        data = await response.data

        assert response.status_code == 200
        assert b"flash-errors" in data
        assert b"flash-success" not in data
