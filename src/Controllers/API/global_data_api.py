from __future__ import annotations

from quart import Blueprint, Response, jsonify, request

from src.Context.Service.Population import APIPerCatPerYearDTO, GeoForAPIService
from src.Controllers.API.utils import BaseAPIView
from src.Infrastructure.Repositories.Population import DALCountryReport, DALHome


class GlobalAPIController(BaseAPIView):
    """
    View class for handling API requests related to specific categories and years.
    """

    def __init__(self, service: GeoForAPIService) -> None:
        self._service = service

    async def get(self) -> Response:
        """
        Get general data.

        Returns:
        -----
            Response: The response containing the fetched data.
        """
        args = self._extract_and_validate_args()
        response = await self._service.fetch_data(args)
        return jsonify(response)

    def _extract_and_validate_args(self) -> APIPerCatPerYearDTO:
        """
        Extracts and validates the arguments from the request object.

        Returns:
            APIPerCatPerYearDTO: A dictionary containing the extracted and validated arguments.
        """
        country_iso_2, year, head, origin, category = self._extract_data()

        return {
            "country_iso_2": country_iso_2,
            "category": category,
            "year": year,
            "head": head,
            "origin": origin,
        }

    def _extract_data(self):
        """
        Extracts data from the request arguments and returns it as a tuple.

        Returns:
            tuple: A tuple containing the country ISO code, year, head, origin, and category.
        """
        args = request.args
        country_iso_2 = args.get("country")
        category_name = args.get("category", "REFUGEES", type=lambda x: x.upper())
        year = args.get("year", 2022, type=int)
        head = args.get("head", False, type=lambda x: x.lower() == "true")
        origin = args.get("origin", True, type=lambda x: x.lower() == "true")
        category = self._get_category(category_name)
        return country_iso_2, year, head, origin, category


global_api_app = Blueprint("global_api_app", __name__)
global_controller = GlobalAPIController.as_view(
    "global_controller", GeoForAPIService(DALHome(), DALCountryReport())
)
global_api_app.add_url_rule("/", view_func=global_controller)
