from uuid import UUID

from src.Infrastructure.Entities.Geo import ContinentEntity, CountryEntity, RegionEntity
from tests.integration.Factory import BaseFactory

IMAGINARY_CONTINENTS = (
    "Atlantis",
    "El Dorado",
    "Lemuria",
    "Mu",
    "Hyperborea",
    "Agartha",
    "Shambhala",
    "Avalon",
    "Hy-Brasil",
    "Thule",
    "Tir na nÓg",
    "Cockaigne",
    "Camelot",
    "Ys",
)


IMAGINARY_REGIONS = (
    "Asgard",
    "Narnia",
    "Mordor",
    "Gotham",
)


IMAGINARY_COUNTRY_NAMES = (
    "Wakanda",
    "Genovia",
    "Asgard",
    "Narnia",
    "Mordor",
    "Gotham",
    "Gondor",
    "Arendelle",
    "Hyrule",
    "Zamunda",
    "Krypton",
    "Azeroth",
    "Midgard",
    "Pandora",
    "Rivendell",
    "Tatooine",
    "Westeros",
    "Xandar",
    "Zion",
    "Zootopia",
)

IMAGINARY_COUNTRY_ISO_3166_1 = (
    "WAK",
    "GEN",
    "ASG",
    "NAR",
    "MOR",
    "GOT",
    "SON",
    "ARE",
    "HYR",
    "ZAM",
    "KRY",
    "AZE",
    "MID",
    "PAN",
    "RIV",
    "TAT",
    "WES",
    "XAN",
    "ZIO",
    "ZOO",
)


class ContinentFactory(BaseFactory):
    """
    Factory class for creating OauthEntity objects.
    """

    async def create_continent(
        self, id: UUID | None = None, name: str | None = None
    ) -> ContinentEntity:
        """
        Create a new ContinentEntity object with the given attributes.

        Args:
            name (str): The name of the continent.
            id (UUID, optional): The ID of the continent. If not provided, a new UUID will be generated.


        Returns:
            ContinentEntity: The created ContinentEntity object.
        """

        if id is None:
            id = UUID(self._faker.unique.uuid4())

        if name is None:
            name = self._faker.random_element(IMAGINARY_CONTINENTS)

        continent = ContinentEntity(
            id=id,  # type: ignore
            name=name,  # type: ignore
        )

        self._session.add(continent)
        await self._session.commit()
        return continent


class RegionFactory(BaseFactory):
    """
    Factory class for creating OauthEntity objects.
    """

    async def create_region(
        self, continent_id: UUID, id: UUID | None = None, name: str | None = None
    ) -> RegionEntity:
        """
        Create a new RegionEntity object with the given attributes.

        Args:
            name (str): The name of the continent.
            continent_id (UUID): The ID of the continent that the region belongs to.
            id (UUID, optional): The ID of the continent. If not provided, a new UUID will be generated.

        Returns:
            RegionEntity: The created RegionEntity object.
        """

        if id is None:
            id = UUID(self._faker.unique.uuid4())

        if name is None:
            name = self._faker.unique.random_element(IMAGINARY_REGIONS)

        region = RegionEntity(
            id=id,  # type: ignore
            continent_id=continent_id,
            name=name,  # type: ignore
        )

        self._session.add(region)
        await self._session.commit()
        return region


class CountryFactory(BaseFactory):
    """
    Factory class for creating OauthEntity objects.
    """

    async def create_country(
        self,
        region_id: UUID,
        id: UUID | None = None,
        name: str | None = None,
        iso: str | None = None,
        iso_2: str | None = None,
        recognized: bool | None = None,
    ) -> CountryEntity:
        """
        Create a new CountryEntity object with the given attributes.

        Args:
            name (str): The name of the country.
            region_id (UUID): The ID of the region that the country belongs to.
            id (UUID, optional): The ID of the country. If not provided, a new UUID will be generated.

        Returns:
            CountryEntity: The created CountryEntity object.
        """
        if id is None:
            id = UUID(self._faker.unique.uuid4())

        if name is None:
            name = self._faker.unique.random_element(IMAGINARY_COUNTRY_NAMES)

        if iso is None:
            iso = self._faker.unique.random_element(IMAGINARY_COUNTRY_ISO_3166_1)

        if iso_2 is None:
            iso_2 = iso[:-1]  # type: ignore

        if recognized is None:
            recognized = self._faker.boolean()

        country = CountryEntity(
            id=id,  # type: ignore
            region_id=region_id,
            name=name,  # type: ignore
            iso=iso,  # type: ignore
            iso_2=iso_2,
            is_recognized=recognized,  # type: ignore
        )

        self._session.add(country)
        await self._session.commit()
        return country
