from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from quart import Quart
from quart.typing import TestClientProtocol

from src.Context.Service.Population import CountryReportService
from src.Controllers.Web.countries_report_app import CountryReportController
from src.Infrastructure.Entities.Geo import CountryEntity
from src.Infrastructure.Repositories.Utils import NoEntityFound


class TestCountryReportController:

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(CountryReportService)
        self._mocked_service.fetch_data = AsyncMock(
            return_value=[
                ([1], [2], [3], [4], [5]),
                Mock(CountryEntity, iso_2="UA", name="Ukraine"),
            ]
        )

        app.view_functions["root.web.countries_report_app.controller"] = (
            CountryReportController.as_view("controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_country_report_controller_unauthenticated_status(self, app: Quart):
        """Test Country Report Controller status code only accessed while logged in."""
        async with app.test_client() as client:
            response = await client.get("/report/")

        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_country_report_controller_authenticated_status(
        self, authenticated_client: TestClientProtocol
    ):
        """Test Country Report Controller status code."""
        response = await authenticated_client.get("/report/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_country_report_controller_template(
        self, authenticated_client: TestClientProtocol, captured_templates: list[Any]
    ):
        """Test Country Report Controller template."""
        await authenticated_client.get("/report/")

        template, _ = captured_templates[0]
        assert template.name == "individual_reports.html"

    @pytest.mark.asyncio
    async def test_country_report_controller_context(
        self, authenticated_client: TestClientProtocol, captured_templates: list[Any]
    ):
        """Test Country Report Controller context."""
        await authenticated_client.get("/report/")

        _, ctx = captured_templates[0]
        assert ctx["top_inflow"] == [1]
        assert ctx["top_outflow"] == [2]
        assert ctx["total_inflow"] == [3]
        assert ctx["total_outflow"] == [4]
        assert ctx["outflow_per_cntry"] == [5]

        assert isinstance(ctx["cntry"], CountryEntity)

        assert ctx["nbar"] == "UA report"

    @pytest.mark.asyncio
    async def test_country_report_controller_if_service_processes_arguments_correctly(
        self, authenticated_client: TestClientProtocol
    ):
        """Test Country Report Controller service called appropriately"""

        await authenticated_client.get("/report/US")

        self._mocked_service.fetch_data.assert_called_once_with("US")

    @pytest.mark.asyncio
    async def test_country_report_controller_no_data_to_return(
        self, authenticated_client: TestClientProtocol
    ):
        """Test Country Report Controller no data to return."""
        self._mocked_service.fetch_data.side_effect = NoEntityFound()

        response = await authenticated_client.get("/report/")
        assert response.status_code == 404
