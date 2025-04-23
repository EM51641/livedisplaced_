from __future__ import annotations


from quart import Blueprint, abort, render_template
from quart.views import MethodView
from quart_auth import login_required

from src.Context.Service.Population import CountryReportService, TReport
from src.Infrastructure.Entities.Geo import CountryEntity
from src.Infrastructure.Repositories.Population import DALCountryReport
from src.Infrastructure.Repositories.Utils import NoEntityFound


class CountryReportController(MethodView):
    """
    Controller class for generating country reports.
    """

    decorators = [login_required]

    def __init__(self, service: CountryReportService) -> None:
        self._service = service

    async def get(self, country_iso_2: str = "UA") -> tuple[str, int]:
        """
        Get method.

        This method handles the GET request for the country analysis page.
        It retrieves the country ISO code from the request parameters and uses it to fetch data.
        Then, it generates a template using the fetched data and returns it along with the HTTP status code.

        Returns:
        -----
            template: str
                The generated template for the country analysis page.
            code: int
                The HTTP status code indicating the success of the request.
        """
        data = await self._get_data(country_iso_2)
        template = await self._generate_template(data)
        return template, 200

    async def _get_data(self, country_iso_2: str) -> tuple[TReport, CountryEntity]:
        """
        Fetches data for a given country using its ISO 2-letter code.

        Args:
            country_iso_2 (str): The ISO 2-letter code of the country.

        Returns:
            tuple[TReport, CountryEntity]: A tuple containing the fetched data and the CountryEntity object.

        Raises:
            404: If no entity is found for the given country ISO 2-letter code.
        """

        try:
            data = await self._service.fetch_data(country_iso_2)
        except NoEntityFound:
            abort(404)
        return data

    async def _generate_template(self, data: tuple[TReport, CountryEntity]):
        """
        Generates a template for the country analysis page.

        Args:
            data (tuple[TReport, CountryEntity]): A tuple containing the report data and the country entity.

        Returns:
            str: The generated template.
        """

        result = data[0]
        country = data[1]

        template = await render_template(
            "individual_reports.html",
            top_inflow=result[0],
            top_outflow=result[1],
            total_inflow=result[2],
            total_outflow=result[3],
            outflow_per_cntry=result[4],
            cntry=country,
            nbar=f"{country.iso_2} report",
        )

        return template


countries_report_app = Blueprint("countries_report_app", __name__, url_prefix="/report")


cntry_analysis_controller = CountryReportController.as_view(
    "controller", CountryReportService(DALCountryReport())
)
countries_report_app.add_url_rule(
    "/<string:country_iso_2>", view_func=cntry_analysis_controller
)
countries_report_app.add_url_rule("/", view_func=cntry_analysis_controller)
