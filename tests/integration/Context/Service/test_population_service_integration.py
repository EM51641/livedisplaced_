"""
All of these tests results can be deducted from arithmetic sums of the data
that is being inserted into the database. The data is being inserted in the
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.Context.Service.Population import (
    APIPerCatPerDTO,
    APIPerCatPerYearDTO,
    APIRelationsDTO,
    BilateralCountriesReportService,
    CountryReportService,
    GeoForAPIService,
    HomeService,
    RelationAPIService,
    TimeSeriesAPIService,
)
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities.Geo import CountryEntity
from src.Infrastructure.Entities.Population import DisplacedCategory
from src.Infrastructure.Repositories.Population import (
    DALBilateral,
    DALCountryReport,
    DALHome,
)
from tests.integration.Factory.geo import (
    ContinentFactory,
    CountryFactory,
    RegionFactory,
)
from tests.integration.Factory.population import PopulationFactory


class BasePopulationService:
    """
    Base class for the user services.
    """

    @pytest.fixture
    async def countries(
        self,
        continent_factory: ContinentFactory,
        region_factory: RegionFactory,
        country_factory: CountryFactory,
    ) -> list[CountryEntity]:

        continent = await continent_factory.create_continent()
        region = await region_factory.create_region(continent_id=continent.id)

        data = [
            ("Moldor", "MD"),
            ("Ginbland", "GB"),
            ("Borland", "BL"),
            ("Someland", "SL"),
            ("Narnia", "NA"),
            ("Gotham", "GH"),
            ("Atlantis", "AT"),
            ("Wakanda", "WK"),
            ("Asgard", "AG"),
            ("Gondor", "GD"),
            ("Azeroth", "AZ"),
            ("Olympus", "OL"),
        ]

        countries = [
            await country_factory.create_country(
                region_id=region.id, name=name, iso_2=iso_2, recognized=True
            )
            for name, iso_2 in data
        ]
        return countries

    @pytest_asyncio.fixture
    async def setup_data_aggregation(
        self,
        countries: list[CountryEntity],
        population_factory: PopulationFactory,
    ) -> None:
        """
        Setup the test on the PasscodeReset instance.
        """

        for x, country in enumerate(countries, start=1):

            for country_arrival in countries:
                if country.id == country_arrival.id:
                    continue
                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 4,
                    year=2024,
                    category=DisplacedCategory.REFUGEES,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 3,
                    year=2024,
                    category=DisplacedCategory.INTERNALLY_DISPLACED,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 2,
                    year=2024,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x,
                    year=2024,
                    category=DisplacedCategory.PEOPLE_OF_CONCERNS,
                )

    @pytest_asyncio.fixture
    async def setup_data_aggregation_multiple_periods(
        self,
        countries: list[CountryEntity],
        country_factory: CountryFactory,
        population_factory: PopulationFactory,
    ):
        """
        Setup the test on the PasscodeReset instance.
        """

        for x, country in enumerate(countries, start=1):
            for country_arrival in countries:
                if country.id == country_arrival.id:
                    continue
                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 5,
                    year=2024,
                    category=DisplacedCategory.REFUGEES,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 4,
                    year=2023,
                    category=DisplacedCategory.INTERNALLY_DISPLACED,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 3,
                    year=2022,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 2,
                    year=2021,
                    category=DisplacedCategory.PEOPLE_OF_CONCERNS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x,
                    year=2020,
                    category=DisplacedCategory.PEOPLE_OF_CONCERNS,
                )

    @pytest_asyncio.fixture
    async def setup_data_aggregation_recognized_countries(
        self,
        countries: list[CountryEntity],
        country_factory: CountryFactory,
        population_factory: PopulationFactory,
    ):
        """
        Setup the test on the PasscodeReset instance.
        """
        country = await country_factory.create_country(
            region_id=countries[0].region_id,
            name="Monhovia",
            iso_2="MH",
            recognized=False,
        )

        countries.append(country)

        for x, country in enumerate(countries, start=1):
            for country_arrival in countries:
                if country_arrival.id == country.id:
                    continue
                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 4,
                    year=2024,
                    category=DisplacedCategory.REFUGEES,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 3,
                    year=2024,
                    category=DisplacedCategory.INTERNALLY_DISPLACED,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 2,
                    year=2024,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x,
                    year=2024,
                    category=DisplacedCategory.PEOPLE_OF_CONCERNS,
                )


class TestPopulationOverviewService(BasePopulationService):
    """
    Test class for the ServiceRegisterUser class.
    """

    @pytest.fixture
    def data_access_layer(
        self, scoped_session: async_scoped_session[AsyncSession]
    ) -> DALHome:
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        session = DBSession(scoped_session)
        return DALHome(db_con=session)

    @pytest.fixture(autouse=True)
    def setup_service(self, data_access_layer: DALHome):
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        self._service = HomeService(dal=data_access_layer)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_data_aggregation")
    async def test_overview_service(self) -> None:
        """
        Test the overview service public api.
        """
        data = await self._service.fetch_data()

        assert data[0] == [
            {"number": "176", "name": "Olympus", "iso_2": "OL"},
            {"number": "165", "name": "Azeroth", "iso_2": "AZ"},
            {"number": "154", "name": "Gondor", "iso_2": "GD"},
            {"number": "143", "name": "Asgard", "iso_2": "AG"},
            {"number": "132", "name": "Wakanda", "iso_2": "WK"},
            {"number": "121", "name": "Atlantis", "iso_2": "AT"},
            {"number": "110", "name": "Gotham", "iso_2": "GH"},
            {"number": "99", "name": "Narnia", "iso_2": "NA"},
            {"number": "88", "name": "Someland", "iso_2": "SL"},
            {"number": "77", "name": "Borland", "iso_2": "BL"},
            {"number": "121", "name": "Others", "iso_2": None},
        ]
        assert data[1] == [
            {"number": "121", "name": "Moldor", "iso_2": "MD"},
            {"number": "120", "name": "Ginbland", "iso_2": "GB"},
            {"number": "119", "name": "Borland", "iso_2": "BL"},
            {"number": "118", "name": "Someland", "iso_2": "SL"},
            {"number": "117", "name": "Narnia", "iso_2": "NA"},
            {"number": "116", "name": "Gotham", "iso_2": "GH"},
            {"number": "115", "name": "Atlantis", "iso_2": "AT"},
            {"number": "114", "name": "Wakanda", "iso_2": "WK"},
            {"number": "113", "name": "Asgard", "iso_2": "AG"},
            {"number": "112", "name": "Gondor", "iso_2": "GD"},
            {"number": "221", "name": "Others", "iso_2": None},
        ]
        assert data[2] == [{"number": "4620", "year": "2024"}]

        assert data[3] == [
            {"number": "176", "name": "Olympus", "iso_2": "OL"},
            {"number": "165", "name": "Azeroth", "iso_2": "AZ"},
            {"number": "154", "name": "Gondor", "iso_2": "GD"},
            {"number": "143", "name": "Asgard", "iso_2": "AG"},
            {"number": "132", "name": "Wakanda", "iso_2": "WK"},
            {"number": "121", "name": "Atlantis", "iso_2": "AT"},
            {"number": "110", "name": "Gotham", "iso_2": "GH"},
            {"number": "99", "name": "Narnia", "iso_2": "NA"},
            {"number": "88", "name": "Someland", "iso_2": "SL"},
            {"number": "77", "name": "Borland", "iso_2": "BL"},
            {"number": "66", "name": "Ginbland", "iso_2": "GB"},
            {"number": "55", "name": "Moldor", "iso_2": "MD"},
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_data_aggregation_multiple_periods")
    async def test_top_aggregation(self) -> None:
        """
        Test the overview service public api.
        """
        data = await self._service.fetch_data()

        assert data[0] == [
            {"number": "187", "name": "Olympus", "iso_2": "OL"},
            {"number": "176", "name": "Azeroth", "iso_2": "AZ"},
            {"number": "165", "name": "Gondor", "iso_2": "GD"},
            {"number": "154", "name": "Asgard", "iso_2": "AG"},
            {"number": "143", "name": "Wakanda", "iso_2": "WK"},
            {"number": "132", "name": "Atlantis", "iso_2": "AT"},
            {"number": "121", "name": "Gotham", "iso_2": "GH"},
            {"number": "110", "name": "Narnia", "iso_2": "NA"},
            {"number": "99", "name": "Someland", "iso_2": "SL"},
            {"number": "88", "name": "Borland", "iso_2": "BL"},
            {"number": "143", "name": "Others", "iso_2": None},
        ]

        assert data[1] == [
            {"number": "132", "name": "Moldor", "iso_2": "MD"},
            {"number": "131", "name": "Ginbland", "iso_2": "GB"},
            {"number": "130", "name": "Borland", "iso_2": "BL"},
            {"number": "129", "name": "Someland", "iso_2": "SL"},
            {"number": "128", "name": "Narnia", "iso_2": "NA"},
            {"number": "127", "name": "Gotham", "iso_2": "GH"},
            {"number": "126", "name": "Atlantis", "iso_2": "AT"},
            {"number": "125", "name": "Wakanda", "iso_2": "WK"},
            {"number": "124", "name": "Asgard", "iso_2": "AG"},
            {"number": "123", "name": "Gondor", "iso_2": "GD"},
            {"number": "243", "name": "Others", "iso_2": None},
        ]
        assert data[2] == [
            {"number": "858", "year": "2020"},
            {"number": "1122", "year": "2021"},
            {"number": "1254", "year": "2022"},
            {"number": "1386", "year": "2023"},
            {"number": "1518", "year": "2024"},
        ]
        assert data[3] == [
            {"number": "187", "name": "Olympus", "iso_2": "OL"},
            {"number": "176", "name": "Azeroth", "iso_2": "AZ"},
            {"number": "165", "name": "Gondor", "iso_2": "GD"},
            {"number": "154", "name": "Asgard", "iso_2": "AG"},
            {"number": "143", "name": "Wakanda", "iso_2": "WK"},
            {"number": "132", "name": "Atlantis", "iso_2": "AT"},
            {"number": "121", "name": "Gotham", "iso_2": "GH"},
            {"number": "110", "name": "Narnia", "iso_2": "NA"},
            {"number": "99", "name": "Someland", "iso_2": "SL"},
            {"number": "88", "name": "Borland", "iso_2": "BL"},
            {"number": "77", "name": "Ginbland", "iso_2": "GB"},
            {"number": "66", "name": "Moldor", "iso_2": "MD"},
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_data_aggregation_recognized_countries")
    async def test_aggregation_recognized_countries(self) -> None:
        """
        Test the overview service public api.
        """
        data = await self._service.fetch_data()

        assert data[0] == [
            {"number": "192", "name": "Olympus", "iso_2": "OL"},
            {"number": "180", "name": "Azeroth", "iso_2": "AZ"},
            {"number": "168", "name": "Gondor", "iso_2": "GD"},
            {"number": "156", "name": "Asgard", "iso_2": "AG"},
            {"number": "144", "name": "Wakanda", "iso_2": "WK"},
            {"number": "132", "name": "Atlantis", "iso_2": "AT"},
            {"number": "120", "name": "Gotham", "iso_2": "GH"},
            {"number": "108", "name": "Narnia", "iso_2": "NA"},
            {"number": "96", "name": "Someland", "iso_2": "SL"},
            {"number": "84", "name": "Borland", "iso_2": "BL"},
            {"number": "132", "name": "Others", "iso_2": None},
        ]

        assert data[1] == [
            {"number": "138", "name": "Moldor", "iso_2": "MD"},
            {"number": "137", "name": "Ginbland", "iso_2": "GB"},
            {"number": "136", "name": "Borland", "iso_2": "BL"},
            {"number": "135", "name": "Someland", "iso_2": "SL"},
            {"number": "134", "name": "Narnia", "iso_2": "NA"},
            {"number": "133", "name": "Gotham", "iso_2": "GH"},
            {"number": "132", "name": "Atlantis", "iso_2": "AT"},
            {"number": "131", "name": "Wakanda", "iso_2": "WK"},
            {"number": "130", "name": "Asgard", "iso_2": "AG"},
            {"number": "129", "name": "Gondor", "iso_2": "GD"},
            {"number": "255", "name": "Others", "iso_2": None},
        ]

        assert data[2] == [{"number": "5772", "year": "2024"}]

        assert data[3] == [
            {"number": "192", "name": "Olympus", "iso_2": "OL"},
            {"number": "180", "name": "Azeroth", "iso_2": "AZ"},
            {"number": "168", "name": "Gondor", "iso_2": "GD"},
            {"number": "156", "name": "Asgard", "iso_2": "AG"},
            {"number": "144", "name": "Wakanda", "iso_2": "WK"},
            {"number": "132", "name": "Atlantis", "iso_2": "AT"},
            {"number": "120", "name": "Gotham", "iso_2": "GH"},
            {"number": "108", "name": "Narnia", "iso_2": "NA"},
            {"number": "96", "name": "Someland", "iso_2": "SL"},
            {"number": "84", "name": "Borland", "iso_2": "BL"},
            {"number": "72", "name": "Ginbland", "iso_2": "GB"},
            {"number": "60", "name": "Moldor", "iso_2": "MD"},
        ]


class TestCountryReportService(BasePopulationService):

    @pytest_asyncio.fixture
    async def origin_aggregation(
        self,
        countries: list[CountryEntity],
        country_factory: CountryFactory,
        population_factory: PopulationFactory,
    ) -> None:
        """
        Setup the test on the PasscodeReset instance.
        """

        unrecognized_country = await country_factory.create_country(
            region_id=countries[0].region_id, name="Mikda", iso_2="MK", recognized=False
        )
        countries.append(unrecognized_country)

        for x, country in enumerate(countries, start=1):

            for country_arrival in countries:
                if country.id == country_arrival.id:
                    continue
                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 4,
                    year=2024,
                    category=DisplacedCategory.REFUGEES,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 3,
                    year=2024,
                    category=DisplacedCategory.INTERNALLY_DISPLACED,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 2,
                    year=2024,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x,
                    year=2024,
                    category=DisplacedCategory.PEOPLE_OF_CONCERNS,
                )

    @pytest_asyncio.fixture
    async def arrival_aggregation(
        self,
        countries: list[CountryEntity],
        country_factory: CountryFactory,
        population_factory: PopulationFactory,
    ) -> None:
        """
        Setup the test on the PasscodeReset instance.
        """

        unrecognized_country = await country_factory.create_country(
            region_id=countries[0].region_id, name="Mikda", iso_2="MK", recognized=False
        )
        countries.append(unrecognized_country)

        country_of_interest = await country_factory.create_country(
            region_id=countries[0].region_id, name="Molva", iso_2="MV", recognized=True
        )

        for x, country in enumerate(countries, start=1):

            await population_factory.create_population(
                country_id=country_of_interest.id,
                country_arrival_id=country.id,
                number=x + 4,
                year=2024,
                category=DisplacedCategory.REFUGEES,
            )

            await population_factory.create_population(
                country_id=country_of_interest.id,
                country_arrival_id=country.id,
                number=x + 3,
                year=2024,
                category=DisplacedCategory.INTERNALLY_DISPLACED,
            )

            await population_factory.create_population(
                country_id=country_of_interest.id,
                country_arrival_id=country.id,
                number=x + 2,
                year=2024,
                category=DisplacedCategory.ASYLIUM_SEEKERS,
            )

            await population_factory.create_population(
                country_id=country_of_interest.id,
                country_arrival_id=country.id,
                number=x,
                year=2024,
                category=DisplacedCategory.PEOPLE_OF_CONCERNS,
            )

    @pytest_asyncio.fixture
    async def timeline_aggregration_inflow(
        self,
        countries: list[CountryEntity],
        country_factory: CountryFactory,
        population_factory: PopulationFactory,
    ):
        """
        Setup the test on the PasscodeReset instance.
        """

        unrecognized_country = await country_factory.create_country(
            region_id=countries[0].region_id, name="Mikda", iso_2="MK", recognized=False
        )

        countries.append(unrecognized_country)

        country_of_interest = await country_factory.create_country(
            region_id=countries[0].region_id, name="Molva", iso_2="MV", recognized=True
        )

        for x, country in enumerate(countries, start=1):

            await population_factory.create_population(
                country_id=country_of_interest.id,
                country_arrival_id=country.id,
                number=x + 4,
                year=2024,
            )

            await population_factory.create_population(
                country_id=country_of_interest.id,
                country_arrival_id=country.id,
                number=x + 3,
                year=2023,
            )

            await population_factory.create_population(
                country_id=country_of_interest.id,
                country_arrival_id=country.id,
                number=x + 2,
                year=2022,
            )

            await population_factory.create_population(
                country_id=country_of_interest.id,
                country_arrival_id=country.id,
                number=x,
                year=1991,
            )

    @pytest_asyncio.fixture
    async def timeline_aggregration_outflow(
        self,
        countries: list[CountryEntity],
        country_factory: CountryFactory,
        population_factory: PopulationFactory,
    ):
        """
        Setup the test on the PasscodeReset instance.
        """

        unrecognized_country = await country_factory.create_country(
            region_id=countries[0].region_id, name="Mikda", iso_2="MK", recognized=False
        )

        countries.append(unrecognized_country)

        country_of_interest = await country_factory.create_country(
            region_id=countries[0].region_id, name="Molva", iso_2="MV", recognized=True
        )

        for x, country in enumerate(countries, start=1):

            await population_factory.create_population(
                country_id=country.id,
                country_arrival_id=country_of_interest.id,
                number=x + 5,
                year=2024,
            )

            await population_factory.create_population(
                country_id=country.id,
                country_arrival_id=country_of_interest.id,
                number=x + 4,
                year=2023,
            )

            await population_factory.create_population(
                country_id=country.id,
                country_arrival_id=country_of_interest.id,
                number=x + 3,
                year=2022,
            )

            await population_factory.create_population(
                country_id=country.id,
                country_arrival_id=country_of_interest.id,
                number=x + 1,
                year=1991,
            )

    @pytest.fixture
    def data_access_layer(
        self, scoped_session: async_scoped_session[AsyncSession]
    ) -> DALCountryReport:
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        session = DBSession(scoped_session)
        return DALCountryReport(db_con=session)

    @pytest.fixture(autouse=True)
    def setup_service(self, data_access_layer: DALCountryReport):
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        self._service = CountryReportService(dal=data_access_layer)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("origin_aggregation")
    async def test_country_report_service_top_10_origin_aggregation(self) -> None:
        """
        Test the overview service public api.
        """
        data, _ = await self._service.fetch_data("OL")

        assert data[0] == [
            {"number": "15", "name": "Azeroth", "iso_2": "AZ"},
            {"number": "14", "name": "Gondor", "iso_2": "GD"},
            {"number": "13", "name": "Asgard", "iso_2": "AG"},
            {"number": "12", "name": "Wakanda", "iso_2": "WK"},
            {"number": "11", "name": "Atlantis", "iso_2": "AT"},
            {"number": "10", "name": "Gotham", "iso_2": "GH"},
            {"number": "9", "name": "Narnia", "iso_2": "NA"},
            {"number": "8", "name": "Someland", "iso_2": "SL"},
            {"number": "7", "name": "Borland", "iso_2": "BL"},
            {"number": "6", "name": "Ginbland", "iso_2": "GB"},
            {"number": "22", "name": "Others", "iso_2": None},
        ]

        assert data[4] == [
            {"number": "17", "name": "Mikda", "iso_2": "MK"},
            {"number": "15", "name": "Azeroth", "iso_2": "AZ"},
            {"number": "14", "name": "Gondor", "iso_2": "GD"},
            {"number": "13", "name": "Asgard", "iso_2": "AG"},
            {"number": "12", "name": "Wakanda", "iso_2": "WK"},
            {"number": "11", "name": "Atlantis", "iso_2": "AT"},
            {"number": "10", "name": "Gotham", "iso_2": "GH"},
            {"number": "9", "name": "Narnia", "iso_2": "NA"},
            {"number": "8", "name": "Someland", "iso_2": "SL"},
            {"number": "7", "name": "Borland", "iso_2": "BL"},
            {"number": "6", "name": "Ginbland", "iso_2": "GB"},
            {"number": "5", "name": "Moldor", "iso_2": "MD"},
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("arrival_aggregation")
    async def test_country_report_service_top_10_arival_aggregation(self) -> None:
        """
        Test the overview service public api.
        """
        data, _ = await self._service.fetch_data("MV")

        assert data[1] == [
            {"number": "16", "name": "Olympus", "iso_2": "OL"},
            {"number": "15", "name": "Azeroth", "iso_2": "AZ"},
            {"number": "14", "name": "Gondor", "iso_2": "GD"},
            {"number": "13", "name": "Asgard", "iso_2": "AG"},
            {"number": "12", "name": "Wakanda", "iso_2": "WK"},
            {"number": "11", "name": "Atlantis", "iso_2": "AT"},
            {"number": "10", "name": "Gotham", "iso_2": "GH"},
            {"number": "9", "name": "Narnia", "iso_2": "NA"},
            {"number": "8", "name": "Someland", "iso_2": "SL"},
            {"number": "7", "name": "Borland", "iso_2": "BL"},
            {"number": "28", "name": "Others", "iso_2": None},
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("timeline_aggregration_inflow")
    async def test_country_report_service_timeline_aggregation_inflow(self) -> None:
        """
        Test the overview service public api.
        """
        data, _ = await self._service.fetch_data("MV")

        assert data[3] == [
            {"number": "91", "year": "1991"},
            {"number": "117", "year": "2022"},
            {"number": "130", "year": "2023"},
            {"number": "143", "year": "2024"},
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("timeline_aggregration_outflow")
    async def test_country_report_service_timeline_aggregation_outflow(self) -> None:
        """
        Test the overview service public api.
        """
        data, _ = await self._service.fetch_data("MV")

        assert data[2] == [
            {"number": "104", "year": "1991"},
            {"number": "130", "year": "2022"},
            {"number": "143", "year": "2023"},
            {"number": "156", "year": "2024"},
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("timeline_aggregration_outflow")
    async def test_country_report_service_country_info(self) -> None:
        """
        Test the overview service public api.
        """
        _, country = await self._service.fetch_data("MV")

        assert country.iso_2 == "MV"
        assert country.name == "Molva"


class TestBilateralCountriesReportService(BasePopulationService):

    @pytest_asyncio.fixture
    async def setup_data_aggregation_multi_periods_and_displacement_category(
        self, countries: list[CountryEntity], population_factory: PopulationFactory
    ):
        """
        Setup the test on the PasscodeReset instance.
        """

        for x, country in enumerate(countries, start=1):
            for country_arrival in countries:
                if country.id == country_arrival.id:
                    continue

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 5,
                    year=2024,
                    category=DisplacedCategory.REFUGEES,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 4,
                    year=2023,
                    category=DisplacedCategory.REFUGEES,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 3,
                    year=2022,
                    category=DisplacedCategory.REFUGEES,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 2,
                    year=2001,
                    category=DisplacedCategory.REFUGEES,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 4,
                    year=2019,
                    category=DisplacedCategory.INTERNALLY_DISPLACED,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 3,
                    year=2016,
                    category=DisplacedCategory.INTERNALLY_DISPLACED,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 2,
                    year=2015,
                    category=DisplacedCategory.INTERNALLY_DISPLACED,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 1,
                    year=2009,
                    category=DisplacedCategory.INTERNALLY_DISPLACED,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 3,
                    year=2024,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 2,
                    year=2019,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 1,
                    year=1992,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x,
                    year=1990,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 7,
                    year=2025,
                    category=DisplacedCategory.PEOPLE_OF_CONCERNS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 6,
                    year=1995,
                    category=DisplacedCategory.PEOPLE_OF_CONCERNS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 5,
                    year=1992,
                    category=DisplacedCategory.PEOPLE_OF_CONCERNS,
                )

                await population_factory.create_population(
                    country_id=country.id,
                    country_arrival_id=country_arrival.id,
                    number=x + 4,
                    year=1990,
                    category=DisplacedCategory.PEOPLE_OF_CONCERNS,
                )

    @pytest.fixture
    def data_access_layer(
        self, scoped_session: async_scoped_session[AsyncSession]
    ) -> DALBilateral:
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        session = DBSession(scoped_session)
        return DALBilateral(db_con=session)

    @pytest.fixture(autouse=True)
    def setup_service(self, data_access_layer: DALBilateral):
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        self._service = BilateralCountriesReportService(dal=data_access_layer)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "setup_data_aggregation_multi_periods_and_displacement_category"
    )
    async def test_bilateral_countries_report_service(self) -> None:
        """
        Test the overview service public api.
        """
        data, _, _ = await self._service.fetch_data(
            origin_cntry_iso_2="OL", destination_cntry_iso_2="AZ"
        )

        assert data[0] == [
            {"number": "14", "year": "2001"},
            {"number": "15", "year": "2022"},
            {"number": "16", "year": "2023"},
            {"number": "17", "year": "2024"},
        ]
        assert data[1] == [
            {"number": "12", "year": "1990"},
            {"number": "13", "year": "1992"},
            {"number": "14", "year": "2019"},
            {"number": "15", "year": "2024"},
        ]

        assert data[2] == [
            {"number": "16", "year": "1990"},
            {"number": "17", "year": "1992"},
            {"number": "18", "year": "1995"},
            {"number": "19", "year": "2025"},
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "setup_data_aggregation_multi_periods_and_displacement_category"
    )
    async def test_bilateral_countries_report_service_countries_info(self) -> None:
        """
        Test the overview service public api.
        """
        _, country_of_arrival, country_of_origin = await self._service.fetch_data(
            "GD", "OL"
        )

        assert country_of_arrival.iso_2 == "GD"
        assert country_of_arrival.name == "Gondor"

        assert country_of_origin.iso_2 == "OL"
        assert country_of_origin.name == "Olympus"


class BaseAPIPopulationService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_data(
        self,
        continent_factory: ContinentFactory,
        region_factory: RegionFactory,
        country_factory: CountryFactory,
        population_factory: PopulationFactory,
    ):
        """
        Setup the test on the PasscodeReset instance.
        """
        continent = await continent_factory.create_continent(name="Olympus")
        region = await region_factory.create_region(
            continent_id=continent.id, name="Olympus"
        )

        country_1 = await country_factory.create_country(
            region_id=region.id, name="Azeroth", iso_2="AZ", recognized=True
        )
        country_2 = await country_factory.create_country(
            region_id=region.id, name="Gondor", iso_2="GD", recognized=True
        )
        country_3 = await country_factory.create_country(
            region_id=region.id, name="Asgard", iso_2="AG", recognized=True
        )

        await population_factory.create_population(
            country_id=country_1.id,
            country_arrival_id=country_2.id,
            number=10,
            year=2024,
            category=DisplacedCategory.REFUGEES,
        )

        await population_factory.create_population(
            country_id=country_1.id,
            country_arrival_id=country_2.id,
            number=5,
            year=2022,
            category=DisplacedCategory.REFUGEES,
        )

        await population_factory.create_population(
            country_id=country_3.id,
            country_arrival_id=country_2.id,
            number=5,
            year=2024,
            category=DisplacedCategory.REFUGEES,
        )

        await population_factory.create_population(
            country_id=country_1.id,
            country_arrival_id=country_3.id,
            number=43,
            year=2024,
            category=DisplacedCategory.REFUGEES,
        )

        await population_factory.create_population(
            country_id=country_1.id,
            country_arrival_id=country_2.id,
            number=1,
            year=2023,
            category=DisplacedCategory.ASYLIUM_SEEKERS,
        )

        await population_factory.create_population(
            country_id=country_3.id,
            country_arrival_id=country_2.id,
            number=5,
            year=2023,
            category=DisplacedCategory.ASYLIUM_SEEKERS,
        )


class TestGeoServiceAPI(BaseAPIPopulationService):

    @pytest.fixture(autouse=True)
    def setup_service(self, scoped_session: async_scoped_session[AsyncSession]):
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        self._service = GeoForAPIService(
            global_data_access_layer=DALHome(db_con=DBSession(scoped_session)),
            country_data_access_layer=DALCountryReport(
                db_con=DBSession(scoped_session)
            ),
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                APIPerCatPerYearDTO(
                    country_iso_2="GD",
                    category=DisplacedCategory.REFUGEES,
                    year=2024,
                    head=False,
                    origin=False,
                ),
                [],
            ),
            (
                APIPerCatPerYearDTO(
                    country_iso_2="GD",
                    category=DisplacedCategory.REFUGEES,
                    year=2024,
                    head=False,
                    origin=True,
                ),
                [
                    {"number": "10", "name": "Azeroth", "iso_2": "AZ"},
                    {"number": "5", "name": "Asgard", "iso_2": "AG"},
                ],
            ),
            (
                APIPerCatPerYearDTO(
                    country_iso_2="GD",
                    category=DisplacedCategory.REFUGEES,
                    year=2024,
                    head=True,
                    origin=False,
                ),
                [],
            ),
            (
                APIPerCatPerYearDTO(
                    country_iso_2="GD",
                    category=DisplacedCategory.REFUGEES,
                    year=2024,
                    head=False,
                    origin=False,
                ),
                [],
            ),
            (
                APIPerCatPerYearDTO(
                    country_iso_2=None,
                    category=DisplacedCategory.REFUGEES,
                    year=2024,
                    head=False,
                    origin=True,
                ),
                [
                    {"number": "53", "name": "Azeroth", "iso_2": "AZ"},
                    {"number": "5", "name": "Asgard", "iso_2": "AG"},
                ],
            ),
            (
                APIPerCatPerYearDTO(
                    country_iso_2=None,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                    year=2023,
                    head=False,
                    origin=False,
                ),
                [
                    {"number": "6", "name": "Gondor", "iso_2": "GD"},
                ],
            ),
            (
                APIPerCatPerYearDTO(
                    country_iso_2=None,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                    year=2023,
                    head=True,
                    origin=False,
                ),
                [
                    {"number": "6", "name": "Gondor", "iso_2": "GD"},
                ],
            ),
            (
                APIPerCatPerYearDTO(
                    country_iso_2=None,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                    year=2023,
                    head=True,
                    origin=True,
                ),
                [
                    {"number": "5", "name": "Asgard", "iso_2": "AG"},
                    {"number": "1", "name": "Azeroth", "iso_2": "AZ"},
                ],
            ),
        ],
    )
    async def test_fetching_geo_data(self, data, expected) -> None:
        """
        Test the overview service public api.
        """
        res = await self._service.fetch_data(data)
        assert res == expected


class TestTimeSeriesAPIService(BaseAPIPopulationService):

    @pytest.fixture(autouse=True)
    def setup_service(self, scoped_session: async_scoped_session[AsyncSession]):
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        self._service = TimeSeriesAPIService(
            global_data_access_layer=DALHome(db_con=DBSession(scoped_session)),
            country_data_access_layer=DALCountryReport(
                db_con=DBSession(scoped_session)
            ),
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                APIPerCatPerDTO(
                    country_iso_2="GD",
                    category=DisplacedCategory.REFUGEES,
                    origin=False,
                ),
                [{"number": "5", "year": "2022"}, {"number": "15", "year": "2024"}],
            ),
            (
                APIPerCatPerDTO(
                    country_iso_2="GD",
                    category=DisplacedCategory.REFUGEES,
                    origin=True,
                ),
                [],
            ),
            (
                APIPerCatPerDTO(
                    country_iso_2=None,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                    origin=False,
                ),
                [{"number": "6", "year": "2023"}],
            ),
            (
                APIPerCatPerDTO(
                    country_iso_2=None,
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                    origin=True,
                ),
                [{"number": "6", "year": "2023"}],
            ),
        ],
    )
    async def test_fetching_ts_data(self, data, expected) -> None:
        """
        Test the overview service public api.
        """
        res = await self._service.fetch_data(data)
        assert res == expected


class TestRelationAPIService(BaseAPIPopulationService):

    @pytest.fixture(autouse=True)
    def setup_service(self, scoped_session: async_scoped_session[AsyncSession]):
        """
        Setup the test on the RelationAPIService instance.
        """
        self._service = RelationAPIService(
            data_access_layer=DALBilateral(db_con=DBSession(scoped_session)),
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                APIRelationsDTO(
                    coo_iso_2="AZ",
                    coa_iso_2="GD",
                    category=DisplacedCategory.REFUGEES,
                ),
                [{"number": "5", "year": "2022"}, {"number": "10", "year": "2024"}],
            ),
            (
                APIRelationsDTO(
                    coo_iso_2="AG",
                    coa_iso_2="GD",
                    category=DisplacedCategory.ASYLIUM_SEEKERS,
                ),
                [{"number": "5", "year": "2023"}],
            ),
        ],
    )
    async def test_fetching_relational_data(self, data, expected) -> None:
        """
        Test the overview service public api.
        """
        res = await self._service.fetch_data(data)
        assert res == expected
