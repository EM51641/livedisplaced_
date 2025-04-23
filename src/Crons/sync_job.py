"""
This module contains utility functions for the Crons package.

Functions:
- get_response(location: str) -> list[dict[Any, Any]]:
    Sends a GET request to the specified location and returns the JSON
    response as a list of dictionaries.
- update_geo_data(geo_data_link: str = GEO_DATA_LINK) -> None:
    Updates the geo data by sending a GET request to the specified
    location and recording the data.
- update_population_data(population_data_link: str) -> None:
    Updates the population data by sending a GET request to the specified
    location and recording the data.
"""

import asyncio
import logging
from typing import Any

import requests  # type: ignore
from fake_useragent import UserAgent  # type: ignore
from sqlalchemy import select  # type: ignore

from src.Crons.loaders.geo_loader import GeoDataRecorder
from src.Crons.loaders.population_loader import PopulationRecorder
from src.Infrastructure.Database import DBManager, DBSession
from src.Infrastructure.Entities.Geo import CountryEntity

GEO_DATA_LINK = (
    "https://api.unhcr.org/population/v1/countries/?limit=90000000000"  # noqa
)
POPULATION_LINK = "https://api.unhcr.org/population/v1/population/?limit=90000000000&coo={0}&coa={1}"  # noqa


logger = logging.getLogger(__name__)


def _get_current_task() -> int:
    id_ = id(asyncio.current_task())
    return id_


db = DBManager(_get_current_task)
db.init_db()


async def load_data():
    """
    Loads data by updating geo data and population data for countries that receive refugees.
    """

    await update_geo_data()

    all_cntries_query = select(CountryEntity)
    country_res = await db.session.execute(all_cntries_query)
    country_seq = country_res.scalars().all()

    iso_code_list = [country.iso for country in country_seq]

    # Get all the code for the countries that receive refugees
    world_iso_str = ",".join(iso_code_list)

    # We don't want to overflow the API so we split our iterations
    number_to_split = 4
    steps = len(iso_code_list) // number_to_split

    for i in range(steps, len(iso_code_list), steps):
        begin, end = i - steps, i
        joined_iso_string = ",".join(iso for iso in iso_code_list[begin:end])
        url = POPULATION_LINK.format(joined_iso_string, world_iso_str)
        await update_population_data(url)

    if len(country_seq) > steps * number_to_split:
        begin = steps * number_to_split
        joined_iso_string = ",".join(iso for iso in iso_code_list[begin:])
        url = POPULATION_LINK.format(joined_iso_string, world_iso_str)
        await update_population_data(url)


def get_response(location: str) -> list[dict[Any, Any]]:
    """
    Sends a GET request to the specified location and returns the JSON
    response as a list of dictionaries.

    Args:
        location (str): The URL to send the GET request to.

    Returns:
        list[dict[Any, Any]]: The JSON response as a list of dictionaries.
    """

    ua = UserAgent()
    response = requests.get(location, headers={"User-Agent": ua.random}, timeout=30)
    return response.json()["items"]


async def update_geo_data(geo_data_link: str = GEO_DATA_LINK) -> None:
    """
    Update the geo data by loading the data from the given link and recording
    it using GeoDataRecorder.

    Args:
    ----
        geo_data_link (str): The link to the geo data.

    Returns:
    ----
        None
    """
    db_session = DBSession(db.session)
    geo_loader = GeoDataRecorder(db_session)
    data: Any = get_response(geo_data_link)

    for point in data:
        try:
            await geo_loader.load_geodata(point)
        except Exception as e:
            logger.error(e)
            await db_session.rollback()


async def update_population_data(population_data_link: str) -> None:
    """
    Update population data by loading population data from the given link and
    loading it into the PopulationRecorder.

    Args:
    ----
        population_data_link (str): The link to the population data.

    Returns:
    ----
        None
    """
    db_session = DBSession(db.session)
    population_loader = PopulationRecorder(db_session)
    data: Any = get_response(population_data_link)

    for point in data:
        try:
            await population_loader.load_population(point)
        except Exception as e:
            logger.exception(e)
            await db_session.rollback()


if __name__ == "__main__":
    asyncio.run(load_data())
