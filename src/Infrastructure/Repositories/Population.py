from __future__ import annotations

from typing import TypedDict

from sqlalchemy import func, or_, select
from sqlalchemy.exc import NoResultFound

from src.Infrastructure.Entities.Geo import CountryEntity
from src.Infrastructure.Entities.Population import DisplacedCategory, PopulationEntity
from src.Infrastructure.Repositories.Utils import DALBase, NoEntityFound


class TDictGeo(TypedDict):
    number: str
    name: str
    iso_2: str


class TDictChart(TypedDict):
    year: str
    number: str


class DALHome(DALBase):
    async def fetch_top_10_coo_per_cat_per_year(
        self, category: DisplacedCategory, year: int
    ) -> list[TDictGeo]:
        """
        Fetches the top 10 cooperative organizations per category per year.

        Args:
            category (DisplacedCategory):
                The category of the displaced population.
            year (int): The year to fetch the data for.

        Returns:
            list[TDictGeo]:
                A sequence of TDictGeo objects representing the top 10
                cooperative organizations.
        """
        stmt = func.public.aggcootop10percatperyear(year, category.name)
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "name": r[1], "iso_2": r[2]} for r in res]

    async def fetch_top_10_coa_per_cat_per_year(
        self, category: DisplacedCategory, year: int
    ) -> list[TDictGeo]:
        """
        Fetches the top 10 countries of asylum per category per year.

        Args:
            category (DisplacedCategory):
                The category of the displaced population.
            year (int): The year to fetch the data for.

        Returns:
            list[TDictGeo]:
                A sequence of TDictGeo objects representing the top 10
                countries of asylum.
        """
        stmt = func.public.aggcoatop10percatperyear(year, category.name)
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "name": r[1], "iso_2": r[2]} for r in res]

    async def fetch_total_displaced_serie(self) -> list[TDictChart]:
        """
        Fetches the total number of displaced people over time.

        Args:
            None

        Returns:
            list[TDictChart]:
                A sequence of TDictChart objects representing the
                total number of displaced people over time.
        """
        stmt = func.public.aggcoo()
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "year": r[1]} for r in res]

    async def fetch_total_displaced_per_category_serie(
        self, category: DisplacedCategory
    ) -> list[TDictChart]:
        """
        Fetches the total number of displaced people per category over time.

        Args:
            category (DisplacedCategory):
                The category of the displaced population.

        Returns:
            list[TDictChart]:
                A sequence of TDictChart objects representing the
                total number of displaced people per category over
                time.
        """
        stmt = func.public.aggcoopercat(category.name)
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "year": r[1]} for r in res]

    async def fetch_coo_per_cat_per_year(
        self, category: DisplacedCategory, year: int
    ) -> list[TDictGeo]:
        """
        Fetches the cooperative organizations per category per year.

        Args:
            category (DisplacedCategory):
                The category of the displaced population.

            year (int):
                The year to fetch the data.

        Returns:
            list[TDictGeo]:
                A sequence of TDictGeo objects representing the cooperative
                organizations.
        """
        stmt = func.public.aggcoopercatperyear(year, category.name)
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "name": r[1], "iso_2": r[2]} for r in res]

    async def fetch_coa_per_cat_per_year(
        self, category: DisplacedCategory, year: int
    ) -> list[TDictGeo]:
        """
        Fetches the countries per category per year.

        Args:
            category (DisplacedCategory): The category of the displaced
                population.
            year (int):
                The year to fetch the data.

        Returns:
            list[TDictGeo]:
                A sequence of TDictGeo objects representing the countries.
        """
        stmt = func.public.aggcoapercatperyear(year, category.name)
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "name": r[1], "iso_2": r[2]} for r in res]

    async def fetch_last_available_year_of_data(self) -> int:
        """
        Fetches the last available year of data.

        Args:
            None

        Returns:
            int: The last available year of data.
        """
        stmt = (
            select(PopulationEntity.year)
            .order_by(PopulationEntity.year.desc())
            .limit(1)
        )

        result = await self._db.session.execute(stmt)
        try:
            year = result.scalar_one()
        except NoResultFound:
            raise NoEntityFound()
        return year


class DALCountryReport(DALBase):
    async def fetch_agg_coo_top_10_per_cat_per_year_per_cntry(
        self,
        country_iso_2: str,
        category: DisplacedCategory,
        year: int,
    ) -> list[TDictGeo]:
        """
        Fetches the top 10 cooperative organizations per category per year per
        country.

        Args:
            country_iso_2 (str): The ISO 2 code of the country.
            category (DisplacedCategory):
                The category of the displaced population.
            year (int): The year to fetch the data for.

        Returns:
            list[TDictGeo]:
                A sequence of TDictGeo objects representing the top 10
                cooperative organizations.
        """
        stmt = func.public.aggcootop10percatperyearpercntry(
            year, category.name, country_iso_2
        )
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "name": r[1], "iso_2": r[2]} for r in res]

    async def fetch_agg_coa_top_10_per_cat_per_year_per_cntry(
        self,
        country_iso_2: str,
        category: DisplacedCategory,
        year: int,
    ) -> list[TDictGeo]:
        """
        Fetches the top 10 countries of asylum per category per year per
        country.

        Args:
            country_iso_2 (str): The ISO 2 code of the country.
            category (DisplacedCategory):
                The category of the displaced population.
            year (int): The year to fetch the data for.

        Returns:
            list[TDictGeo]:
                A sequence of TDictGeo objects representing the top 10
                countries of asylum.
        """
        stmt = func.public.aggcoatop10percatperyearpercntry(
            year, category.name, country_iso_2
        )
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "name": r[1], "iso_2": r[2]} for r in res]

    async def fetch_agg_coa_per_cntry(self, country_iso_2: str) -> list[TDictChart]:
        """
        Fetches the total number of displaced people per year per country.

        Args:
            country_iso_2 (str): The ISO 2 code of the country.

        Returns:
            list[TDictChart]:
                A sequence of TDictChart objects representing the total number
                of displaced people per year per country.
        """
        stmt = func.public.aggcoapercntry(country_iso_2)
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "year": r[1]} for r in res]

    async def fetch_agg_coo_per_cntry(self, country_iso_2: str) -> list[TDictChart]:
        """
        Fetches the total number of displaced people per year per origin
        country.

        Args:
            country_iso_2 (str): The ISO 2 code of the country.

        Returns:
            list[TDictChart]:
            A sequence of TDictChart objects representing the total number of
            displaced people per year per origin country.
        """
        stmt = func.public.aggcoopercntry(country_iso_2)
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "year": r[1]} for r in res]

    async def fetch_agg_coo_per_cntry_per_cat(
        self, country_iso_2: str, category: DisplacedCategory
    ) -> list[TDictChart]:
        """
        Fetches the total number of displaced people per year per origin
        country per category.

        Args:
            country_iso_2 (str):
                The ISO 2 code of the country.
            category (DisplacedCategory):
                The category of the displaced population.

        Returns:
            list[TDictChart]:
                A sequence of TDictChart objects representing the total number
                of displaced people per year per origin country per category.
        """
        stmt = func.public.aggcoopercntrypercat(country_iso_2, category.name)
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "year": r[1]} for r in res]

    async def fetch_agg_coa_per_cntry_per_cat(
        self, country_iso_2: str, category: DisplacedCategory
    ) -> list[TDictChart]:
        """
        Fetches the total number of displaced people per year per country per
        category.

        Args:
            country_iso_2 (str):
                The ISO 2 code of the country.
            category (DisplacedCategory):
                The category of the displaced population.

        Returns:
            list[TDictChart]:
                A sequence of TDictChart objects representing the total number
                of displaced people per year per country per category.
        """
        stmt = func.public.aggcoapercntrypercat(country_iso_2, category.name)
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "year": r[1]} for r in res]

    async def fetch_agg_coo_per_cntry_per_cat_per_year(
        self, country_iso_2: str, category: DisplacedCategory, year: int
    ) -> list[TDictGeo]:
        """geo_outflow_data: geo data per origin country."""
        stmt = func.public.aggcooperyearpercatpercntry(
            year, category.name, country_iso_2
        )
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "name": r[1], "iso_2": r[2]} for r in res]

    async def fetch_agg_coa_per_cntry_per_cat_per_year(
        self, country_iso_2: str, category: DisplacedCategory, year: int
    ) -> list[TDictGeo]:
        """geo_outflow_data: geo data per origin country."""
        stmt = func.public.aggcoaperyearpercatpercntry(
            year, category.name, country_iso_2
        )
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "name": r[1], "iso_2": r[2]} for r in res]

    async def fetch_last_available_year_of_data_per_country(
        self, country_iso: str
    ) -> tuple[int, CountryEntity]:
        """
        Retreive last year's population

        Parameters:
        ----
            country_iso: str

        Returns:
        ----
            year:int selected year
        """

        country_entity = await self._get_country(country_iso)

        stmt = (
            select(PopulationEntity.year)
            .where(
                or_(
                    PopulationEntity.country_id == country_entity.id,
                    PopulationEntity.country_arrival_id == country_entity.id,
                )
            )
            .order_by(PopulationEntity.year.desc())
            .limit(1)
        )

        result = await self._db.session.execute(stmt)

        try:
            year = result.scalar_one()
        except NoResultFound:
            raise NoEntityFound()

        return year, country_entity

    async def _get_country(self, country_iso_2: str) -> CountryEntity:
        stmt = select(CountryEntity).where(
            CountryEntity.iso_2 == country_iso_2,
            CountryEntity.is_recognized == True,  # noqa
        )
        result = await self._db.execute(stmt)

        try:
            country_entity = result.scalar_one()
        except NoResultFound:
            raise NoEntityFound()

        return country_entity


class DALBilateral(DALBase):
    async def fetch_agg_per_coo_per_coa_per_cat(
        self,
        country_origin_iso_2: str,
        country_arrival_iso_2: str,
        category: DisplacedCategory,
    ) -> list[TDictChart]:
        """
        Fetch total displaced people per country of origin and hosting country.

        Parameters:
        ----
            country_origin_iso_2: str
            country_arrival_iso_2: str
            category: DisplacedCategory

        Returns:
        ----
            list[TDictChart]
        """
        stmt = func.public.aggpercoopercoapercat(
            country_origin_iso_2, country_arrival_iso_2, category.name
        )
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "year": r[1]} for r in res]

    async def fetch_agg_per_coo_per_coa(
        self, country_origin_iso_2: str, country_arrival_iso_2: str
    ) -> list[TDictChart]:
        """
        Fetch total displaced people per country of origin and hosting country.

        Parameters:
        ----
            country_origin_iso_2: str
            country_arrival_iso_2: str

        Returns:
        ----
            list[TDictChart]
        """
        stmt = func.public.aggpercoopercoaper(
            country_origin_iso_2, country_arrival_iso_2
        )
        res = await self._execute_statement_and_return_sequence(stmt)
        return [{"number": r[0], "year": r[1]} for r in res]

    async def get_country(self, country_iso_2: str) -> CountryEntity:
        stmt = select(CountryEntity).where(
            CountryEntity.iso_2 == country_iso_2,
            CountryEntity.is_recognized == True,  # noqa
        )
        result = await self._db.execute(stmt)
        try:
            country_entity = result.scalar_one()
        except NoResultFound:
            raise NoEntityFound()
        return country_entity
