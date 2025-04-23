"""
Module for the home controller.

This module contains the controller for the home page of the web application.
"""

from __future__ import annotations

from quart import Blueprint, render_template, abort
from quart.views import MethodView

from src.Context.Service.Population import HomeService, THome
from src.Infrastructure.Repositories.Population import DALHome
from src.Infrastructure.Repositories.Utils import NoEntityFound


class OverviewController(MethodView):
    """
    Home controller.

    This controller handles the logic for the home page of the web application.
    """

    def __init__(self, service: HomeService) -> None:
        """
        Initializes the HomeController.

        Args:
            service (HomeService): The service used by the controller.
        """
        self._service = service

    async def get(self) -> tuple[str, int]:
        """
        Retrieves data, generates a template, and returns it along with a status code.

        Returns:
            tuple[str, int]: The generated template and the status code.
        """
        data = await self._get_data()
        template = await self._generate_template(data)
        return template, 200

    async def _get_data(self) -> THome:
        """
        Fetches data from the service and returns it.

        Returns:
            THome: The fetched data.

        Raises:
            HTTPException: If no entity is found.
        """
        try:
            data = await self._service.fetch_data()
            return data
        except NoEntityFound:
            abort(404)

    async def _generate_template(self, data):
        """
        Generates a template for the home page.

        Args:
            data (list):
                A list of data to be passed to the template.

        Returns:
            str: The generated template.
        """
        template = await render_template(
            "home.html",
            coo=data[0],
            coa=data[1],
            total=data[2],
            geo=data[3],
            nbar="home",
        )
        return template


overview_app = Blueprint("overview_app", __name__)

overview_controller = OverviewController.as_view("controller", HomeService(DALHome()))
overview_app.add_url_rule("/", view_func=overview_controller)
