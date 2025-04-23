from __future__ import annotations

from quart import Blueprint, Response, jsonify, request

from src.Context.Service.Population import APIPerCatPerDTO, TimeSeriesAPIService
from src.Controllers.API.utils import BaseAPIView
from src.Infrastructure.Repositories.Population import DALCountryReport, DALHome


class CountryTSAPIController(BaseAPIView):
    """
    API endpoint for retrieving time series data.
    """

    def __init__(self, service: TimeSeriesAPIService) -> None:
        self._service = service

    async def get(self) -> Response:
        """
        Get Time series data.

        Returns:
        -----
            Response:
                The response containing time series data.
        """
        args = self._extract_and_validate_args()
        response = await self._service.fetch_data(args)
        return jsonify(response)

    def _extract_and_validate_args(self) -> APIPerCatPerDTO:
        """
        Extracts and validates the arguments from the request.

        Returns:
            A dictionary containing the extracted and validated arguments:
            - country_iso_2 (str): The ISO 2-letter country code.
            - category (Category): The category of data.
            - origin (bool): Flag indicating whether to include origin data.
        """
        args = request.args
        country_iso_2 = args.get("country")
        category_name = args.get("category", type=str)
        origin = args.get("origin", "true").lower() == "true"
        category = self._define_category(category_name)

        return {"country_iso_2": country_iso_2, "category": category, "origin": origin}

    def _define_category(self, category_name: str | None):
        """
        Defines the category based on the given category name.

        Args:
            category_name (str | None): The name of the category.

        Returns:
            category: The defined category.

        """
        if category_name is None:
            category = None
        else:
            category = self._get_category(category_name)
        return category


country_ts_api_app = Blueprint("country_ts_api_app", __name__)
country_ts_api_controller = CountryTSAPIController.as_view(
    "country_ts_api_controller", TimeSeriesAPIService(DALHome(), DALCountryReport())
)
country_ts_api_app.add_url_rule("/chart", view_func=country_ts_api_controller)
