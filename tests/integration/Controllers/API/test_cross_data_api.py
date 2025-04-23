from typing import Any
from unittest.mock import Mock

import pytest
from quart import Quart
from quart.typing import TestClientProtocol

from src.Context.Service.Population import RelationAPIService
from src.Controllers.API.bilateral_ts_data_api import RelationAPIController
from src.Infrastructure.Entities.Population import DisplacedCategory


class TestRelationAPIController:
    """
    Test relational api controller.
    """

    @pytest.fixture(autouse=True)
    def setup(self, app: Quart):
        self._mocked_service = Mock(RelationAPIService)
        self._mocked_service.fetch_data.return_value = {"data": [1, 2, 3]}
        app.view_functions["root.api.bilateral_app.bilateral_controller"] = (
            RelationAPIController.as_view("bilateral_controller", self._mocked_service)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "url, expected_args",
        [
            (
                "/api/v1/relations?coo=AD&coa=AZ&category=ASYLIUM_SEEKERS",
                {
                    "coo_iso_2": "AD",
                    "coa_iso_2": "AZ",
                    "category": DisplacedCategory.ASYLIUM_SEEKERS,
                },
            ),
            (
                "/api/v1/relations",
                {
                    "coo_iso_2": "UA",
                    "coa_iso_2": "US",
                    "category": None,
                },
            ),
        ],
    )
    async def test_relational_controller_authenticated_get(
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

    @pytest.mark.asyncio
    async def test_relational_controller_unauthenticated_get(self, app: Quart):
        """Test relational api controller template."""
        async with app.test_client() as client:
            response = await client.get("/api/v1/relations")

        assert response.status_code == 302
        assert response.location == "/user/login/"
