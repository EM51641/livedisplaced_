from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from quart import Quart

from src.Context.Service.Population import HomeService
from src.Controllers.Web.overview_app import OverviewController
from src.Infrastructure.Repositories.Utils import NoEntityFound


class TestOverviewController:

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(HomeService)
        self._mocked_service.fetch_data = AsyncMock(return_value=[[1], [2], [3], [4]])

        app.view_functions["root.web.overview_app.controller"] = (
            OverviewController.as_view("controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_overview_controller_status(self, app: Quart):
        """Test overview controller status code."""
        async with app.test_client() as client:
            response = await client.get("/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_overview_controller_template(
        self, app: Quart, captured_templates: list[Any]
    ):
        """Test overview controller template."""
        async with app.test_client() as client:
            await client.get("/")

        template, _ = captured_templates[0]
        assert template.name == "home.html"

    @pytest.mark.asyncio
    async def test_overview_controller_context(
        self, app: Quart, captured_templates: list[Any]
    ):
        """Test overview controller context."""
        async with app.test_client() as client:
            await client.get("/")

        _, ctx = captured_templates[0]
        assert ctx["coo"] == [1]
        assert ctx["coa"] == [2]
        assert ctx["total"] == [3]
        assert ctx["geo"] == [4]
        assert ctx["nbar"] == "home"

    @pytest.mark.asyncio
    async def test_overview_controller_no_data_to_return(self, app: Quart):
        """Test overview controller no data to return."""
        self._mocked_service.fetch_data.side_effect = NoEntityFound()

        async with app.test_client() as client:
            response = await client.get("/")

        assert response.status_code == 404
