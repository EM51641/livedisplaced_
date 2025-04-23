import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.Crons.loaders.population_loader import PopulationRecorder, TPopulation
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities.Geo import CountryEntity, RegionEntity
from src.Infrastructure.Entities.Population import DisplacedCategory, PopulationEntity
from tests.integration.conftest import resolve_query_one
from tests.integration.Factory.geo import (
    ContinentFactory,
    CountryFactory,
    RegionFactory,
)


class TestPopulationCron:

    @pytest_asyncio.fixture
    async def region(
        self, continent_factory: ContinentFactory, region_factory: RegionFactory
    ) -> RegionEntity:
        continent = await continent_factory.create_continent()
        region = await region_factory.create_region(continent_id=continent.id)
        return region

    @pytest_asyncio.fixture
    async def country_of_origin(
        self, region: RegionEntity, country_factory: CountryFactory
    ):
        country = await country_factory.create_country(region_id=region.id)
        return country

    @pytest_asyncio.fixture
    async def country_of_arrival(
        self, region: RegionEntity, country_factory: CountryFactory
    ):
        country = await country_factory.create_country(region_id=region.id)
        return country

    @pytest.fixture(autouse=True)
    def setup_service(self, scoped_session: async_scoped_session[AsyncSession]):
        self.service = PopulationRecorder(DBSession(scoped_session))

    @pytest.fixture
    def data(
        self, country_of_arrival: CountryEntity, country_of_origin: CountryEntity
    ) -> TPopulation:
        return {
            "coo_iso": country_of_origin.iso,
            "coa_iso": country_of_arrival.iso,
            "refugees": 100,
            "asylum_seekers": 200,
            "stateless": 300,
            "idps": 400,
            "ooc": 500,
            "oip": 600,
            "year": 2020,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "category,expected_number",
        [
            (DisplacedCategory.REFUGEES, 100),
            (DisplacedCategory.ASYLIUM_SEEKERS, 800),
            (DisplacedCategory.INTERNALLY_DISPLACED, 400),
            (DisplacedCategory.PEOPLE_OF_CONCERNS, 800),
        ],
    )
    async def test_ingest_traffic_data(
        self,
        category: DisplacedCategory,
        expected_number: int,
        data: TPopulation,
        session: AsyncSession,
        country_of_origin: CountryEntity,
        country_of_arrival: CountryEntity,
    ):

        await self.service.load_population(data)

        query = select(PopulationEntity).where(
            PopulationEntity.category == category,
        )

        res = await resolve_query_one(query, session)

        assert res.country_id == country_of_origin.id
        assert res.country_arrival_id == country_of_arrival.id
        assert res.number == expected_number
        assert res.year == 2020
