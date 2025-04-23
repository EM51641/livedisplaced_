"""
Update all the country data from the UN db.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TypedDict
from uuid import uuid4

import pycountry  # type: ignore
from sqlalchemy import select

from src.Crons import BaseScrapper
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities.Geo import ContinentEntity, CountryEntity, RegionEntity


class TypeCountry(TypedDict):
    """
    JSON structure for country.
    """

    majorArea: str
    region: str
    name: str
    iso: str
    iso2: str
    code: str


class BaseGeoDataRecorder(BaseScrapper):
    @abstractmethod
    async def load_geodata(self, data: "TypeCountry") -> None:
        """Not implemented yet"""


class GeoDataRecorder(BaseGeoDataRecorder):
    """
    Scrap the time series data provided by the UN API.
    """

    def __init__(self, db: DBSession) -> None:
        """
        Initialize the GeoDataRecorder.

        Args:
            db (Database): The database instance to use.
        """
        self._db = db

    @property
    def db(self) -> DBSession:
        return self._db

    async def load_geodata(self, data: "TypeCountry") -> None:
        """
        Loads geodata for a given country.

        Args:
        ---
            data (TypeCountry): The country data to load geodata for.

        Returns:
        ---
            None
        """
        data = self._data_checker(data)
        continent = await self._load_continent(data)
        region = await self._load_region(continent, data)
        await self._load_country(region, data)

    def _data_checker(self, data: "TypeCountry"):
        """
        Check and update the missing fields in the given data dictionary.

        Args:
            data (TypeCountry): The data dictionary to be checked.

        Returns:
            TypeCountry: The updated data dictionary with missing fields filled with "NA".
        """
        if not data["majorArea"]:
            data["majorArea"] = "NA"

        if not data["region"]:
            data["region"] = "NA"

        if not data["name"]:
            data["name"] = "NA"

        if not data["iso"]:
            data["iso"] = "NA"

        if not data["iso2"]:
            data["iso2"] = "NA"

        if not data["code"]:
            data["code"] = "NA"

        return data

    async def _load_continent(self, data: "TypeCountry") -> ContinentEntity:
        """
        Get the data entry.

        Parameters:
        ----
        data: TypeCountry
            The data containing information about the country.

        Returns:
        ----
        ContinentEntity
            The continent entity created from the data.
        """
        continent = ContinentEntity(id=uuid4(), name=data["majorArea"])
        query = select(ContinentEntity).filter(ContinentEntity.name == continent.name)
        continent_record = await self._save_if_no_duplicates(query, continent)
        return continent_record

    async def _load_region(
        self, continent: ContinentEntity, data: "TypeCountry"
    ) -> RegionEntity:
        """
        Load a region entity based on the provided data.

        Parameters:
        ----
        continent (ContinentEntity): The continent entity to which the region belongs.
        data (TypeCountry): The data containing information about the region.

        Returns:
        ----
        RegionEntity: The loaded region entity.
        """

        region = RegionEntity(
            id=uuid4(), name=data["region"], continent_id=continent.id
        )
        query = select(RegionEntity).filter(RegionEntity.name == region.name)
        region_record = await self._save_if_no_duplicates(query, region)
        return region_record

    async def _load_country(
        self, region: RegionEntity, data: "TypeCountry"
    ) -> CountryEntity:
        """
        Get the data entry.

        Parameters:
        ----
        region (RegionEntity): The region entity associated with the country.
        data (TypeCountry): The data entry containing information about the country.

        Returns:
        ----
        CountryEntity: The created country entity.

        """
        is_official = self._is_country_official(data["iso2"])

        country = CountryEntity(
            id=uuid4(),
            name=data["name"],
            iso=data["iso"],
            iso_2=data["iso2"],
            is_recognized=is_official,
            region_id=region.id,
        )
        query = select(CountryEntity).filter(CountryEntity.name == country.name)
        country_record = await self._save_if_no_duplicates(query, country)
        return country_record

    def _is_country_official(self, iso2: str) -> bool:
        """
        Check if the given ISO2 country code is an official country code.

        Args:
            iso2 (str): The ISO2 country code to check.

        Returns:
            bool: True if the country code is official, False otherwise.
        """
        country = pycountry.countries.get(alpha_2=iso2)
        return True if country else False
