import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.Crons.loaders.geo_loader import GeoDataRecorder, TypeCountry
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities.Geo import ContinentEntity, CountryEntity, RegionEntity
from tests.integration.conftest import resolve_query_one


class TestGeoCron:

    @pytest.fixture(autouse=True)
    def setup_service(self, scoped_session: async_scoped_session[AsyncSession]):
        self.service = GeoDataRecorder(DBSession(scoped_session))

    @pytest.fixture
    def data(self) -> TypeCountry:
        return {
            "majorArea": "Azeroth",
            "region": "Eastern Kingdoms",
            "iso": "SWD",
            "iso2": "SW",
            "name": "Stormwind",
            "code": "SWD",
        }

    @pytest.mark.asyncio
    async def test_ingest_continent_geo_data(
        self, data: TypeCountry, session: AsyncSession
    ):

        await self.service.load_geodata(data)

        query = select(ContinentEntity)

        continent = await resolve_query_one(query, session)

        assert continent.name == "Azeroth"

    @pytest.mark.asyncio
    async def test_ingest_region_geo_data(
        self, data: TypeCountry, session: AsyncSession
    ):

        await self.service.load_geodata(data)

        query = select(RegionEntity)

        region = await resolve_query_one(query, session)

        assert region.name == "Eastern Kingdoms"

    @pytest.mark.asyncio
    async def test_ingest_country_geo_data(
        self, data: TypeCountry, session: AsyncSession
    ):

        await self.service.load_geodata(data)

        query = select(CountryEntity)

        country = await resolve_query_one(query, session)

        assert country.name == "Stormwind"
        assert country.iso == "SWD"
        assert country.iso_2 == "SW"
        assert country.is_recognized is False
