from typing import Any
from unittest.mock import Mock

import pytest
from quart import Quart
from quart.typing import TestClientProtocol

from src.Context.Service.Population import TimeSeriesAPIService
from src.Controllers.API.country_ts_data_api import CountryTSAPIController
from src.Infrastructure.Entities.Population import DisplacedCategory


class TestCountryTSAPIController:
    """
    Test relational api controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(TimeSeriesAPIService)
        self._mocked_service.fetch_data.return_value = {"data": [1, 2, 3]}
        app.view_functions["root.api.country_ts_api_app.country_ts_api_controller"] = (
            CountryTSAPIController.as_view(
                "country_ts_api_controller", self._mocked_service
            )
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "url, expected_args",
        [
            (
                "/api/v1/chart?country=AD&category=ASYLIUM_SEEKERS&origin=false",
                {
                    "country_iso_2": "AD",
                    "category": DisplacedCategory.ASYLIUM_SEEKERS,
                    "origin": False,
                },
            ),
            (
                "/api/v1/chart",
                {
                    "country_iso_2": None,
                    "category": None,
                    "origin": True,
                },
            ),
        ],
    )
    async def test_country_ts_controller_get(
        self,
        authenticated_client: TestClientProtocol,
        url: str,
        expected_args: dict[str, Any],
    ):
        """Test relational api controller status."""
        response = await authenticated_client.get(url)
        data = await response.get_json()
        assert response.status_code == 200
        assert response.content_type == "application/json"
        assert data == {"data": [1, 2, 3]}

        self._mocked_service.fetch_data.assert_called_once_with(expected_args)
