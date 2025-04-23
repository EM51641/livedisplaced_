from typing import Any
from unittest.mock import Mock

import pytest
from quart import Quart

from src.Context.Service.Population import GeoForAPIService
from src.Controllers.API.global_data_api import GlobalAPIController
from src.Infrastructure.Entities.Population import DisplacedCategory


class TestGlobalAPIController:
    """
    Test global api controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(GeoForAPIService)
        self._mocked_service.fetch_data.return_value = {"data": [1, 2, 3]}
        app.view_functions["root.api.global_api_app.global_controller"] = (
            GlobalAPIController.as_view("global_controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "url, expected_args",
        [
            (
                "/api/v1/?country=US&category=ASYLIUM_SEEKERS&year=2000&head=true&origin=false",
                {
                    "country_iso_2": "US",
                    "category": DisplacedCategory.ASYLIUM_SEEKERS,
                    "year": 2000,
                    "head": True,
                    "origin": False,
                },
            ),
            (
                "/api/v1/",
                {
                    "country_iso_2": None,
                    "category": DisplacedCategory.REFUGEES,
                    "year": 2022,
                    "head": False,
                    "origin": True,
                },
            ),
        ],
    )
    async def test_global_controller_get(
        self, url: str, expected_args: dict[str, Any], app: Quart
    ):
        """Test global api controller status."""
        async with app.test_client() as client:
            response = await client.get(url)
            data = await response.get_json()
        assert response.status_code == 200
        assert response.content_type == "application/json"
        assert data == {
            "data": [1, 2, 3],
        }

        self._mocked_service.fetch_data.assert_called_once_with(expected_args)
