"""
Update all the country data from the UN db.
"""

from __future__ import annotations

from abc import abstractmethod
from datetime import UTC, datetime
from typing import TypedDict
from uuid import uuid4

from sqlalchemy import select

from src.Crons import BaseScrapper
from src.Infrastructure.Entities.Geo import CountryEntity
from src.Infrastructure.Entities.Population import DisplacedCategory, PopulationEntity


class TPopulation(TypedDict):
    """
    JSON structure for country.
    """

    coo_iso: str
    coa_iso: str
    refugees: int
    asylum_seekers: int
    stateless: int
    idps: int
    ooc: int
    oip: int
    year: int


class BasePopulationRecorder(BaseScrapper):
    @abstractmethod
    async def load_population(self, data: "TPopulation") -> None:
        """Not implemented yet"""


class PopulationRecorder(BasePopulationRecorder):
    """
    This class is responsible for loading population data from the UN API and
    storing it in the database.

    Methods:
    ----
    load_population(data: TPopulation) -> None:
        Loads population data for a given country and year.
    _get_country(coo_iso: str) -> CountryEntity:
        Retrieves a CountryEntity object for a given ISO code.
    _load_refugees(data: TPopulation, country_of_origin: CountryEntity,
            country_of_arrival: CountryEntity) -> None:
        Loads population data for refugees.
    _load_asylium_seekers(data: TPopulation, country_of_origin: CountryEntity,
        country_of_arrival: CountryEntity) -> None:
        Loads population data for asylum seekers.
    _load_internally_displaced(data: TPopulation, country_of_origin:
        CountryEntity, country_of_arrival: CountryEntity) -> None:
        Loads population data for internally displaced persons.
    _load_people_of_concerns(data: TPopulation, country_of_origin:
        CountryEntity, country_of_arrival: CountryEntity) -> None:
        Loads population data for people of concern.
    """

    async def load_population(self, data: "TPopulation") -> None:
        """
        Loads population data for a given country and year.

        Parameters:
        ----
        data: TPopulation
            The population data to be loaded.

        Returns:
        ----
            None
        """
        data = self.check_data(data)

        country_of_origin = await self._get_country(data["coo_iso"])
        country_of_arrival = await self._get_country(data["coa_iso"])

        await self._load_refugees(data, country_of_origin, country_of_arrival)

        await self._load_asylium_seekers(data, country_of_origin, country_of_arrival)

        await self._load_people_of_concerns(data, country_of_origin, country_of_arrival)
        await self._load_internally_displaced(
            data, country_of_origin, country_of_arrival
        )

    def check_data(self, data: "TPopulation") -> "TPopulation":
        if isinstance(data["refugees"], str):
            data["refugees"] = 0

        if isinstance(data["asylum_seekers"], str):
            data["asylum_seekers"] = 0

        if isinstance(data["idps"], str):
            data["idps"] = 0

        if isinstance(data["ooc"], str):
            data["ooc"] = 0

        if isinstance(data["stateless"], str):
            data["stateless"] = 0

        if isinstance(data["oip"], str):
            data["oip"] = 0

        return data

    async def _get_country(self, iso: str) -> CountryEntity:
        """
        Retrieves a CountryEntity object for a given ISO code.

        Parameters:
        ----
        iso: str
            The ISO code for the country to retrieve.

        Returns:
        ----
        CountryEntity
            The CountryEntity object for the given ISO code.
        """
        query = select(CountryEntity).filter(CountryEntity.iso == iso)
        res = await self._db.execute(query)
        country = res.scalar_one()
        return country

    async def _load_refugees(
        self,
        data: "TPopulation",
        country_of_origin: CountryEntity,
        country_of_arrival: CountryEntity,
    ) -> None:
        """
        Loads population data for refugees.

        Parameters:
        ----
        data: TPopulation
            The population data to be loaded.
        country_of_origin: CountryEntity
            The CountryEntity object for the country of origin.
        country_of_arrival: CountryEntity
            The CountryEntity object for the country of arrival.

        Returns:
        ----
        None
        """
        population = PopulationEntity(
            id=uuid4(),
            country_id=country_of_origin.id,
            country_arrival_id=country_of_arrival.id,
            year=data["year"],
            number=data["refugees"],
            category=DisplacedCategory.REFUGEES,
            created=datetime.now(UTC),
        )

        query = select(PopulationEntity).filter(
            PopulationEntity.country_id == country_of_origin.id,
            PopulationEntity.country_arrival_id == country_of_arrival.id,
            PopulationEntity.year == data["year"],
            PopulationEntity.category == DisplacedCategory.REFUGEES,
        )
        await self._save_if_no_duplicates(query, population)

    async def _load_asylium_seekers(
        self,
        data: "TPopulation",
        country_of_origin: CountryEntity,
        country_of_arrival: CountryEntity,
    ) -> None:
        """
        Loads population data for asylum seekers.

        Parameters:
        ----
        data: TPopulation
            The population data to be loaded.
        country_of_origin: CountryEntity
            The CountryEntity object for the country of origin.
        country_of_arrival: CountryEntity
            The CountryEntity object for the country of arrival.

        Returns:
        ----
            None
        """
        population = PopulationEntity(
            id=uuid4(),
            country_id=country_of_origin.id,
            country_arrival_id=country_of_arrival.id,
            year=data["year"],
            number=data["asylum_seekers"] + data["oip"],
            category=DisplacedCategory.ASYLIUM_SEEKERS,
            created=datetime.now(UTC),
        )

        query = select(PopulationEntity).filter(
            PopulationEntity.country_id == country_of_origin.id,
            PopulationEntity.country_arrival_id == country_of_arrival.id,
            PopulationEntity.year == data["year"],
            PopulationEntity.category == DisplacedCategory.ASYLIUM_SEEKERS,
        )
        await self._save_if_no_duplicates(query, population)

    async def _load_internally_displaced(
        self,
        data: "TPopulation",
        country_of_origin: CountryEntity,
        country_of_arrival: CountryEntity,
    ) -> None:
        """
        Loads population data for internally displaced persons.

        Parameters:
        ----
        data: TPopulation
            The population data to be loaded.
        country_of_origin: CountryEntity
            The CountryEntity object for the country of origin.
        country_of_arrival: CountryEntity
            The CountryEntity object for the country of arrival.

        Returns:
        ----
            None
        """
        population = PopulationEntity(
            id=uuid4(),
            country_id=country_of_origin.id,
            country_arrival_id=country_of_arrival.id,
            year=data["year"],
            number=data["idps"],
            category=DisplacedCategory.INTERNALLY_DISPLACED,
            created=datetime.now(UTC),
        )

        query = select(PopulationEntity).filter(
            PopulationEntity.country_id == country_of_origin.id,
            PopulationEntity.country_arrival_id == country_of_arrival.id,
            PopulationEntity.year == data["year"],
            PopulationEntity.category == DisplacedCategory.INTERNALLY_DISPLACED,
        )

        await self._save_if_no_duplicates(query, population)

    async def _load_people_of_concerns(
        self,
        data: "TPopulation",
        country_of_origin: CountryEntity,
        country_of_arrival: CountryEntity,
    ) -> None:
        """
        Loads population data for people of concern.

        Parameters:
        ----
        data: TPopulation
            The population data to be loaded.
        country_of_origin: CountryEntity
            The CountryEntity object for the country of origin.
        country_of_arrival: CountryEntity
            The CountryEntity object for the country of arrival.

        Returns:
        ----
            None
        """
        population = PopulationEntity(
            id=uuid4(),
            country_id=country_of_origin.id,
            country_arrival_id=country_of_arrival.id,
            year=data["year"],
            number=data["ooc"] + data["stateless"],
            category=DisplacedCategory.PEOPLE_OF_CONCERNS,
            created=datetime.now(UTC),
        )

        query = select(PopulationEntity).filter(
            PopulationEntity.country_id == country_of_origin.id,
            PopulationEntity.country_arrival_id == country_of_arrival.id,
            PopulationEntity.year == data["year"],
            PopulationEntity.category == DisplacedCategory.PEOPLE_OF_CONCERNS,
        )
        await self._save_if_no_duplicates(query, population)
