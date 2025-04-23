from __future__ import annotations

from quart import Blueprint, Response, jsonify, request
from quart_auth import login_required

from src.Context.Service.Population import APIRelationsDTO, RelationAPIService
from src.Controllers.API.utils import BaseAPIView
from src.Infrastructure.Repositories.Population import DALBilateral


class RelationAPIController(BaseAPIView):
    """
    API endpoint for retrieving time series data related to relations.
    """

    decorators = [login_required]

    def __init__(self, service: RelationAPIService) -> None:
        self._service = service

    async def get(self) -> Response:
        """
        Get Time series data.

        Parameters:
        -----
            None

        Returns:
        -----
            Response: The response containing the fetched data.
        """
        args = self._extract_and_validate_args()
        response = await self._service.fetch_data(args)
        return jsonify(response)

    def _extract_and_validate_args(self) -> APIRelationsDTO:
        """
        Extract and validate the arguments from the request.

        Returns:
        -----
            APIRelationsDTO: The validated arguments.
        """
        args = request.args
        country_of_origin_iso_2 = args.get("coo", "UA")
        country_of_arrival_iso_2 = args.get("coa", "US")
        category_name = args.get("category")
        category = self._define_category(category_name)

        return {
            "coo_iso_2": country_of_origin_iso_2,
            "coa_iso_2": country_of_arrival_iso_2,
            "category": category,
        }

    def _define_category(self, category_name: str | None):
        """
        Define the category based on the category name.

        Parameters:
        -----
            category_name (str | None): The name of the category.

        Returns:
        -----
            str | None: The defined category.
        """
        if category_name is None:
            category = None
        else:
            category = self._get_category(category_name)
        return category


bilateral_app = Blueprint("bilateral_app", __name__)
bilateral_controller = RelationAPIController.as_view(
    "bilateral_controller", RelationAPIService(DALBilateral())
)

bilateral_app.add_url_rule("/relations", view_func=bilateral_controller)
