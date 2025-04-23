from __future__ import annotations

from typing import Optional, TypedDict

from sqlalchemy.exc import NoResultFound

from src.Context.Service import BaseServiceDAL
from src.Infrastructure.Entities.Geo import CountryEntity
from src.Infrastructure.Entities.Population import DisplacedCategory
from src.Infrastructure.Repositories.Population import (
    DALBilateral,
    DALCountryReport,
    DALHome,
    TDictChart,
    TDictGeo,
)
from src.Infrastructure.Repositories.Utils import NoEntityFound

THome = tuple[list[TDictGeo], list[TDictGeo], list[TDictChart], list[TDictGeo]]

TReport = tuple[
    list[TDictGeo],
    list[TDictGeo],
    list[TDictChart],
    list[TDictChart],
    list[TDictGeo],
]

TTwoCountriesReport = tuple[list[TDictChart], list[TDictChart], list[TDictChart]]


class APIPerCatPerYearDTO(TypedDict):
    country_iso_2: Optional[str]
    category: DisplacedCategory
    year: int
    head: bool
    origin: bool


class APIPerCatPerDTO(TypedDict):
    country_iso_2: Optional[str]
    category: Optional[DisplacedCategory]

    origin: bool


class APIRelationsDTO(TypedDict):
    coo_iso_2: str
    coa_iso_2: str
    category: Optional[DisplacedCategory]


class HomeService(BaseServiceDAL[DALHome]):
    """
    Home service.

    This service class provides methods to fetch data related to the home country
    for generating reports. It interacts with the data access layer to retrieve
    relevant data and process it to generate the report.

    Attributes:
    ----------
    dal : DALHome
        The data access layer object used to interact with the database.

    Methods:
    -------
    fetch_data() -> THome:
        Fetches the data required for generating the home country report.

    Private Methods:
    ---------------
    _get_last_available_year() -> int:
        Fetches the last available year of data.

    _fetch_data(year: int) -> THome:
        Fetches the specific data required for generating the home country report
        based on the given year.

    """

    _CATEGORY_NAME = DisplacedCategory.REFUGEES

    def __init__(self, dal: DALHome) -> None:
        super().__init__(dal)

    async def fetch_data(self) -> THome:
        """
        Fetches the data required for generating the home country report.

        Returns:
        -------
        THome
            The report data for the home country.
        """
        year = await self._get_last_available_year()
        result = await self._fetch_data(year)
        return result

    async def _get_last_available_year(self) -> int:
        """
        Fetches the last available year of data.

        Returns:
        -------
        int
            The last available year of data.
        """
        try:
            year = await self._data_access_layer.fetch_last_available_year_of_data()
            return year
        except NoResultFound:
            raise NoEntityFound()

    async def _fetch_data(self, year: int) -> THome:
        """
        Fetches the specific data required for generating the home country report
        based on the given year.

        Parameters:
        ----------
        year : int
            The year for which the data is fetched.

        Returns:
        -------
        THome
            The report data for the home country.
        """
        coo_data = await self._data_access_layer.fetch_top_10_coo_per_cat_per_year(
            self._CATEGORY_NAME, year
        )
        coa_data = await self._data_access_layer.fetch_top_10_coa_per_cat_per_year(
            self._CATEGORY_NAME, year
        )
        total_data = await self._data_access_layer.fetch_total_displaced_serie()
        geo_coo_data = await self._data_access_layer.fetch_coo_per_cat_per_year(
            self._CATEGORY_NAME, year
        )
        return (coo_data, coa_data, total_data, geo_coo_data)


class CountryReportService(BaseServiceDAL[DALCountryReport]):
    """
    Country Report Service.

    This service class provides methods to fetch data related to a specific country
    for generating reports. It interacts with the data access layer to retrieve
    relevant data and process it to generate the report.

    Attributes:
    ----------
    dal : DALCountryReport
        The data access layer object used to interact with the database.

    Methods:
    -------
    fetch_data(cntry_iso_2: str) -> tuple[TReport, CountryEntity]:
        Fetches the data required for generating the country report for the given
        country ISO 2 code.

    Private Methods:
    ---------------
    _fetch_data(cntry_iso_2: str, year: int) -> TReport:
        Fetches the specific data required for generating the country report based
        on the given country ISO 2 code and year.

    _get_last_available_year_per_country(cntry_iso_2: str) -> tuple[int, CountryEntity]:
        Fetches the last available year of data for the given country ISO 2 code.

    """

    _CATEGORY_NAME = DisplacedCategory.REFUGEES

    def __init__(self, dal: DALCountryReport) -> None:
        super().__init__(dal)

    async def fetch_data(self, cntry_iso_2: str) -> tuple[TReport, CountryEntity]:
        """
        Fetches the data required for generating the country report for the given
        country ISO 2 code.

        Parameters:
        ----------
        cntry_iso_2 : str
            The ISO 2 code of the country.

        Returns:
        -------
        tuple[TReport, CountryEntity]
            A tuple containing the report data and the country entity.
        """
        last_year_and_cntry = await self._get_last_available_year_per_country(
            cntry_iso_2
        )
        result = await self._fetch_data(cntry_iso_2, last_year_and_cntry[0])
        return result, last_year_and_cntry[1]

    async def _fetch_data(self, cntry_iso_2: str, year: int) -> TReport:
        """
        Fetches the specific data required for generating the country report based
        on the given country ISO 2 code and year.

        Parameters:
        ----------
        cntry_iso_2 : str
            The ISO 2 code of the country.

        year : int
            The year for which the data is fetched.

        Returns:
        -------
        TReport
            The report data for the given country.
        """

        inflow_per_country = await self._data_access_layer.fetch_agg_coo_top_10_per_cat_per_year_per_cntry(
            cntry_iso_2, self._CATEGORY_NAME, year
        )
        outflow_per_country = await self._data_access_layer.fetch_agg_coa_top_10_per_cat_per_year_per_cntry(
            cntry_iso_2, self._CATEGORY_NAME, year
        )
        historic_inflows = await self._data_access_layer.fetch_agg_coa_per_cntry(
            cntry_iso_2
        )
        historic_outflows = await self._data_access_layer.fetch_agg_coo_per_cntry(
            cntry_iso_2
        )
        geo_outflow_data = (
            await self._data_access_layer.fetch_agg_coo_per_cntry_per_cat_per_year(
                cntry_iso_2, self._CATEGORY_NAME, year
            )
        )
        return (
            inflow_per_country,
            outflow_per_country,
            historic_inflows,
            historic_outflows,
            geo_outflow_data,
        )

    async def _get_last_available_year_per_country(
        self, cntry_iso_2: str
    ) -> tuple[int, CountryEntity]:
        """
        Fetches the last available year of data for the given country ISO 2 code.

        Parameters:
        ----------
        cntry_iso_2 : str
            The ISO 2 code of the country.

        Returns:
        -------
        tuple[int, CountryEntity]
            A tuple containing the last available year of data and the country entity.
        """
        try:
            last_year_and_cntry = await self._data_access_layer.fetch_last_available_year_of_data_per_country(
                cntry_iso_2
            )
            return last_year_and_cntry
        except NoResultFound:
            raise NoEntityFound()


class BilateralCountriesReportService(BaseServiceDAL[DALBilateral]):
    """
    Two Countries Report Service.

    This service class provides methods to fetch data for generating a report
    on two countries. It interacts with the data access layer to retrieve
    relevant data and process it to generate the report.

    Attributes:
    ----------
    data_access_layer : DALBilateral
        The data access layer object used to interact with the database.

    Methods:
    -------
    fetch_data(origin_cntry_iso_2: str, destination_cntry_iso_2: str) -> tuple[
                    TTwoCountriesReport, CountryEntity, CountryEntity]:
        Fetches data for the given origin and destination countries and returns
        a tuple containing the report data, origin country entity, and destination
        country entity.

    Private Methods:
    ---------------
    _fetch_data(origin_cntry_iso_2: str, arrival_cntry_iso_2: str) -> TTwoCountriesReport:
        Fetches the specific data required for the report generation based on the
        given origin and destination countries.

    """

    def __init__(self, dal: DALBilateral) -> None:
        super().__init__(dal)

    async def fetch_data(
        self, origin_cntry_iso_2: str, destination_cntry_iso_2: str
    ) -> tuple[TTwoCountriesReport, CountryEntity, CountryEntity]:
        """
        Fetches data for the given origin and destination countries and returns
        a tuple containing the report data, origin country entity, and destination
        country entity.

        Parameters:
        ----
        origin_cntry_iso_2 : str
            The ISO 2 code of the country of origin.

        destination_cntry_iso_2 : str
            The ISO 2 code of the country of destination.

        Returns:
        ----
        tuple[TTwoCountriesReport, CountryEntity, CountryEntity]
            A tuple containing the report data, origin country entity, and destination
            country entity.
        """
        origin_cntry = await self._data_access_layer.get_country(origin_cntry_iso_2)
        destination_cntry = await self._data_access_layer.get_country(
            destination_cntry_iso_2
        )
        result = await self._fetch_data(origin_cntry_iso_2, destination_cntry_iso_2)
        return result, origin_cntry, destination_cntry

    async def _fetch_data(
        self, origin_cntry_iso_2: str, arrival_cntry_iso_2: str
    ) -> TTwoCountriesReport:
        """
        Fetches the specific data required for the report generation based on the
        given origin and destination countries.

        Parameters:
        ----------
        origin_cntry_iso_2 : str
            The ISO 2 code of the country of origin.

        arrival_cntry_iso_2 : str
            The ISO 2 code of the country of destination.

        Returns:
        -------
        TTwoCountriesReport
            The report data for the given origin and destination countries.
        """

        refugees = await self._data_access_layer.fetch_agg_per_coo_per_coa_per_cat(
            origin_cntry_iso_2,
            arrival_cntry_iso_2,
            DisplacedCategory.REFUGEES,
        )

        asylium_seekers = (
            await self._data_access_layer.fetch_agg_per_coo_per_coa_per_cat(
                origin_cntry_iso_2,
                arrival_cntry_iso_2,
                DisplacedCategory.ASYLIUM_SEEKERS,
            )
        )

        people_of_conerns = (
            await self._data_access_layer.fetch_agg_per_coo_per_coa_per_cat(
                origin_cntry_iso_2,
                arrival_cntry_iso_2,
                DisplacedCategory.PEOPLE_OF_CONCERNS,
            )
        )

        return (refugees, asylium_seekers, people_of_conerns)


class GeoForAPIService:
    """
    A service class for fetching geographical data from different data access layers.

    This service class provides methods to fetch geographical data from different
    data access layers. It interacts with the data access layers to retrieve the
    relevant data and process it.

    Attributes:
    ----

        global_data_access_layer : DALHome
            The data access layer object used to interact with the global data.

        country_data_access_layer : DALCountryReport
            The data access layer object used to interact with the country-specific data.

    Methods:
    ----
        fetch_data(data: APIPerCatPerYearDTO) -> list[TDictGeo]:
            Fetches the geographical data based on the given API data.
    """

    def __init__(
        self,
        global_data_access_layer: DALHome,
        country_data_access_layer: DALCountryReport,
    ) -> None:
        self._global_data_access_layer = global_data_access_layer
        self._country_data_access_layer = country_data_access_layer

    async def fetch_data(self, data: APIPerCatPerYearDTO) -> list[TDictGeo]:
        """
        Fetches the geographical data based on the given API data.

        Parameters:
        ----
            data : APIPerCatPerYearDTO
                The API data containing the country ISO 2 code, category, year, head, and origin.

        Returns:
        ----
            list[TDictGeo]
                The geographical data based on the given API data.
        """
        if data["head"]:
            res = await self._get_top_data(data)
        else:
            res = await self._get_all_data(data)
        return res

    async def _get_top_data(self, data: APIPerCatPerYearDTO) -> list[TDictGeo]:
        """
        Get top 10 data per country or in the world.

        Args:
            data: The data containing the necessary parameters for fetching the top data.

        Returns:
            A list of dictionaries containing the top data per country or in the world.
        """
        if data["country_iso_2"] and data["origin"]:
            res = await self._country_data_access_layer.fetch_agg_coo_top_10_per_cat_per_year_per_cntry(  # noqa
                data["country_iso_2"], data["category"], data["year"]
            )

        elif data["country_iso_2"] and not data["origin"]:
            res = await self._country_data_access_layer.fetch_agg_coa_top_10_per_cat_per_year_per_cntry(  # noqa
                data["country_iso_2"], data["category"], data["year"]
            )
        elif data["origin"]:
            res = await self._global_data_access_layer.fetch_top_10_coo_per_cat_per_year(  # noqa
                data["category"], data["year"]
            )
        else:
            res = await self._global_data_access_layer.fetch_top_10_coa_per_cat_per_year(  # noqa
                data["category"], data["year"]
            )

        return res

    async def _get_all_data(self, data: APIPerCatPerYearDTO) -> list[TDictGeo]:
        """
        Get all the available data.

        Args:
            data: The data containing the necessary parameters for fetching all the data.

        Returns:
            A list of dictionaries containing all the available data.
        """
        if data["country_iso_2"] and data["origin"]:
            res = await self._country_data_access_layer.fetch_agg_coo_per_cntry_per_cat_per_year(  # noqa
                data["country_iso_2"], data["category"], data["year"]
            )

        elif data["country_iso_2"] and not data["origin"]:
            res = await self._country_data_access_layer.fetch_agg_coa_per_cntry_per_cat_per_year(  # noqa
                data["country_iso_2"], data["category"], data["year"]
            )
        elif data["origin"]:
            res = (
                await self._global_data_access_layer.fetch_coo_per_cat_per_year(  # noqa
                    data["category"], data["year"]
                )
            )
        else:
            res = (
                await self._global_data_access_layer.fetch_coa_per_cat_per_year(  # noqa
                    data["category"], data["year"]
                )
            )

        return res


class TimeSeriesAPIService:
    """
    Service class for fetching time series data related to population.
    """

    def __init__(
        self,
        global_data_access_layer: DALHome,
        country_data_access_layer: DALCountryReport,
    ) -> None:
        self._global_data_access_layer = global_data_access_layer
        self._country_data_access_layer = country_data_access_layer

    async def fetch_data(self, data: APIPerCatPerDTO) -> list[TDictChart]:
        """
        Fetches data based on the given APIPerCatPerDTO object.

        Args:
            data (APIPerCatPerDTO): The APIPerCatPerDTO object containing the data.

        Returns:
            list[TDictChart]: The fetched data as a list of TDictChart objects.
        """

        if data["category"]:
            res = await self._get_per_category_data(data)
        else:
            res = await self._get_total_data(data)
        return res

    async def _get_total_data(self, data: APIPerCatPerDTO) -> list[TDictChart]:
        """
        Get aggregated data of people in concerning situation across the globe.

        Args:
            data (APIPerCatPerDTO): The data containing the country ISO code and origin information.

        Returns:
            list[TDictChart]: The aggregated data of people in concerning situation.
        """
        if data["country_iso_2"] and data["origin"]:
            res = await self._country_data_access_layer.fetch_agg_coo_per_cntry(
                data["country_iso_2"]
            )

        elif data["country_iso_2"] and not data["origin"]:
            res = await self._country_data_access_layer.fetch_agg_coa_per_cntry(
                data["country_iso_2"]
            )
        else:
            res = (
                await self._global_data_access_layer.fetch_total_displaced_serie()  # noqa
            )

        return res

    async def _get_per_category_data(self, data: APIPerCatPerDTO) -> list[TDictChart]:
        """
        Get all the available data.
        """
        assert data["category"]

        if data["country_iso_2"] and data["origin"]:
            res = await self._country_data_access_layer.fetch_agg_coo_per_cntry_per_cat(  # noqa
                data["country_iso_2"], data["category"]
            )

        elif data["country_iso_2"] and not data["origin"]:
            res = await self._country_data_access_layer.fetch_agg_coa_per_cntry_per_cat(  # noqa
                data["country_iso_2"], data["category"]
            )
        else:
            res = await self._global_data_access_layer.fetch_total_displaced_per_category_serie(  # noqa
                data["category"]
            )

        return res


class RelationAPIService:
    """
    Service class for fetching relation data.
    """

    def __init__(self, data_access_layer: DALBilateral) -> None:
        self._data_access_layer = data_access_layer

    async def fetch_data(self, data: APIRelationsDTO) -> list[TDictChart]:
        """
        Fetches relation data based on the provided parameters.

        Args:
            data (APIRelationsDTO): The data object containing the parameters for fetching data.

        Returns:
            list[TDictChart]: The fetched relation data.
        """
        if data["category"]:
            res = await self._get_per_category_data(data)
        else:
            res = await self._get_total_data(data)
        return res

    async def _get_total_data(self, data: APIRelationsDTO) -> list[TDictChart]:
        """
        Get aggregated data of people in concerning situation across the globe.

        Args:
            data (APIRelationsDTO): The data object containing the parameters for fetching data.

        Returns:
            list[TDictChart]: The fetched aggregated data.
        """
        res = await self._data_access_layer.fetch_agg_per_coo_per_coa(
            data["coo_iso_2"], data["coa_iso_2"]
        )
        return res

    async def _get_per_category_data(self, data: APIRelationsDTO) -> list[TDictChart]:
        """
        Get all the available data.

        Args:
            data (APIRelationsDTO): The data object containing the parameters for fetching data.

        Returns:
            list[TDictChart]: The fetched data.
        """

        assert data["category"]

        res = await self._data_access_layer.fetch_agg_per_coo_per_coa_per_cat(
            data["coo_iso_2"], data["coa_iso_2"], data["category"]
        )
        return res
