from __future__ import annotations

from quart import Blueprint, abort, render_template, request
from quart.views import MethodView
from quart_auth import login_required

from src.Context.Service.Population import (
    BilateralCountriesReportService,
    TTwoCountriesReport,
)
from src.Infrastructure.Entities.Geo import CountryEntity
from src.Infrastructure.Repositories.Population import DALBilateral
from src.Infrastructure.Repositories.Utils import NoEntityFound


class BilateralController(MethodView):
    """
    Two Countries Report Service Controller.

    This controller handles the retrieval and generation of a report template
    for two countries. It interacts with the BilateralCountriesReportService to fetch
    data and render the template.
    """

    decorators = [login_required]

    def __init__(self, service: BilateralCountriesReportService) -> None:
        """
        Initializes a new instance of the CrossFunctionalPage class.

        Args:
            service (BilateralCountriesReportService): The service used for generating two countries reports.
        """
        self._service = service

    async def get(self) -> tuple[str, int]:
        """
        Get method.

        This method handles the GET request for the cross_functional_page.

        Returns:
        -----
            template: str
                The generated HTML template.
            code: int
                The HTTP status code indicating the success of the request.
        """
        country_of_origin_iso_2 = request.args.get("coo", "UA")
        country_of_destination_iso_2 = request.args.get("coa", "US")

        data, country_origin, country_arrival = await self._get_data(
            country_of_origin_iso_2, country_of_destination_iso_2
        )
        template = await self._generate_template(country_origin, country_arrival, data)
        return template, 200

    async def _get_data(
        self, country_of_origin_iso_2: str, country_of_destination_iso_2: str
    ) -> tuple[TTwoCountriesReport, CountryEntity, CountryEntity]:
        """
        Fetches data for the given country of origin and country of destination.

        Args:
            country_of_origin_iso_2 (str):
                The ISO 2-letter code of the country of origin.
            country_of_destination_iso_2 (str):
                The ISO 2-letter code of the country of destination.

        Returns:
            tuple[TTwoCountriesReport, CountryEntity, CountryEntity]: A tuple containing the fetched data,
            the country of origin entity, and the country of destination entity.

        Raises:
            NoEntityFound: If no data is found for the given country of origin and country of destination.
        """
        try:
            (data, country_origin, country_arrival) = await self._service.fetch_data(
                country_of_origin_iso_2, country_of_destination_iso_2
            )
            return data, country_origin, country_arrival
        except NoEntityFound:
            abort(404)

    async def _generate_template(
        self,
        country_of_origin: CountryEntity,
        country_of_arrival: CountryEntity,
        data: TTwoCountriesReport,
    ):
        """
        Generates a template for the traffic between two countries report.

        Args:
            country_of_origin (CountryEntity):
                The country of origin.
            country_of_arrival (CountryEntity):
                The country of arrival.
            data (TTwoCountriesReport):
                The data for the report.

        Returns:
            str: The generated template.
        """
        template = await render_template(
            "dashboard.html",
            refugees_ts=data[0],
            asylium_seekers_ts=data[1],
            people_of_concern_ts=data[2],
            country_of_origin=country_of_origin,
            country_of_arrival=country_of_arrival,
            nbar=f"{country_of_origin.iso_2} -> {country_of_arrival.iso_2}",  # noqa
        )

        return template


flux_between_cntries_app = Blueprint(
    "flux_between_cntries_app", __name__, url_prefix="/dashboard"
)


flux_between_cntries_view = BilateralController.as_view(
    "controller", BilateralCountriesReportService(DALBilateral())
)

flux_between_cntries_app.add_url_rule("/", view_func=flux_between_cntries_view)
