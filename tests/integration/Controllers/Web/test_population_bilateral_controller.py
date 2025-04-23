from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from quart import Quart
from quart.typing import TestClientProtocol

from src.Context.Service.Population import BilateralCountriesReportService
from src.Controllers.Web.flux_between_cntries_app import BilateralController
from src.Infrastructure.Entities.Geo import CountryEntity
from src.Infrastructure.Repositories.Utils import NoEntityFound


class TestDashboardController:

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(BilateralCountriesReportService)
        self._mocked_service.fetch_data = AsyncMock(
            return_value=[
                ([1], [2], [3]),
                Mock(CountryEntity, iso_2="UA", name="Ukraine"),
                Mock(CountryEntity, iso_2="US", name="United States"),
            ]
        )

        app.view_functions["root.web.flux_between_cntries_app.controller"] = (
            BilateralController.as_view("controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    async def test_flux_between_cntries_unauthenticated_status(self, app: Quart):
        """Test bilateral controller status code only accessed while logged in."""
        async with app.test_client() as client:
            response = await client.get("/dashboard/")

        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_flux_between_cntries_authenticated_status(
        self, authenticated_client: TestClientProtocol
    ):
        """Test bilateral controller status code."""
        response = await authenticated_client.get("/dashboard/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_flux_between_cntries_template(
        self, authenticated_client: TestClientProtocol, captured_templates: list[Any]
    ):
        """Test bilateral controller template."""
        await authenticated_client.get("/dashboard/")

        template, _ = captured_templates[0]
        assert template.name == "dashboard.html"

    @pytest.mark.asyncio
    async def test_flux_between_cntries_context(
        self, authenticated_client: TestClientProtocol, captured_templates: list[Any]
    ):
        """Test bilateral controller context."""
        await authenticated_client.get("/dashboard/")

        _, ctx = captured_templates[0]
        assert ctx["refugees_ts"] == [1]
        assert ctx["asylium_seekers_ts"] == [2]
        assert ctx["people_of_concern_ts"] == [3]

        assert isinstance(ctx["country_of_origin"], CountryEntity)
        assert isinstance(ctx["country_of_arrival"], CountryEntity)

        assert ctx["nbar"] == "UA -> US"

    @pytest.mark.asyncio
    async def test_if_service_processes_arguments_correctly(
        self, authenticated_client: TestClientProtocol
    ):
        """Test bilateral controller service called appropriately"""

        await authenticated_client.get("/dashboard/?coo=UA&coa=AU")

        self._mocked_service.fetch_data.assert_called_once_with("UA", "AU")

    @pytest.mark.asyncio
    async def test_flux_between_cntries_no_data_to_return(
        self, authenticated_client: TestClientProtocol
    ):
        """Test bilateral controller no data to return."""
        self._mocked_service.fetch_data.side_effect = NoEntityFound()

        response = await authenticated_client.get("/dashboard/")
        assert response.status_code == 404
