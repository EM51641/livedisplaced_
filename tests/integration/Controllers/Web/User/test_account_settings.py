from typing import Any

import pytest
from quart.typing import TestClientProtocol


class TestSettingsController:
    """
    Test settings controller.
    """

    @pytest.mark.asyncio
    async def test_settings_controller_authenticated_get_status(
        self, authenticated_client: TestClientProtocol
    ):
        """Test settings controller get status."""
        response = await authenticated_client.get("/user/settings/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_settings_controller_authenticate_get_template(
        self, authenticated_client: TestClientProtocol, captured_templates: list[Any]
    ):
        """Test settings controller get template."""
        await authenticated_client.get("/user/settings/")

        template, _ = captured_templates[0]
        assert template.name == "settings.html"

    @pytest.mark.asyncio
    async def test_settings_controller_unauthenticated(
        self, client: TestClientProtocol
    ):
        """Test settings controller get status."""
        response = await client.get("/user/settings/")
        assert response.status_code == 302
        assert response.location == "/user/login/"
