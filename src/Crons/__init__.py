"""
Update all the country data from the UN db.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.managers import db

if TYPE_CHECKING:
    from typing import TypeVar

    from sqlalchemy import Select

    from src.Infrastructure.Database import DBSession
    from src.Infrastructure.Entities.Geo import (
        ContinentEntity,
        CountryEntity,
        RegionEntity,
    )
    from src.Infrastructure.Entities.Population import PopulationEntity

    TInstanceSave = PopulationEntity | ContinentEntity | CountryEntity | RegionEntity

    TInstanceToSaveVar = TypeVar("TInstanceToSaveVar", bound=TInstanceSave)


logger = logging.getLogger(__name__)


class BaseScrapper:
    """
    Base class for scrapers.

    This class provides common functionality for scrapers, such as saving
    entities to the database and checking for duplicates.

    Attributes:
        db (Database): The database connection.

    Methods:
        _save_if_no_duplicates: Saves the given entity to the database if no duplicates are found.
        _save: Saves the data into the database.
        _select_table: Selects a table from the database.

    """

    def __init__(self, db_con: DBSession | None = None):
        if db_con is None:
            db_con = DBSession(db.session)

        self._db = db_con

    @property
    def db(self) -> DBSession:
        return self._db

    async def _save_if_no_duplicates(
        self,
        query: Select[tuple[TInstanceToSaveVar]],
        entity: TInstanceToSaveVar,
    ) -> TInstanceToSaveVar:
        """
        Saves the given entity to the database if
        no duplicates are found.

        Args:
            query: A SQLAlchemy select query to check for duplicates.
            entity: The entity to save to the database.

        Returns:
            The saved entity if no duplicates were found, otherwise the
            existing record.
        """
        res = await self._db.execute(query)
        record = res.scalar()
        if record is None:
            await self._save(entity)
            return entity
        else:
            return record

    async def _save(self, instance: TInstanceSave) -> None:
        """
        Save the data into the db.

        Parameters:
        ----
            instance: TInstanceSave

        Returns:
        ----
            None
        """
        try:
            self._db.session.add(instance)
            await self._db.session.commit()
        except Exception as e:
            logger.exception(e)
            await self._db.session.rollback()
