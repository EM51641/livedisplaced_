"""
This module contains the implementation of the BaseUnitOfWork and UnitOfWork
classes.

The BaseUnitOfWork class is an abstract base class that defines the interface
for a unit of work. The UnitOfWork class is a concrete implementation of
the BaseUnitOfWork class.

A unit of work is a design pattern that helps to maintain consistency and
integrity in a database transaction. It groups together all the changes made
to the database within a single transaction and ensures that they are either
all committed or all rolled back in case of an error.

Classes:
- BaseUnitOfWork: An abstract base class that defines the interface for a unit
    of work.
- UnitOfWork: A concrete implementation of the BaseUnitOfWork class.

Type Variables:
- TUnitOfWork: A type variable that is bound to the UnitOfWork class.

Exceptions:
- AddException: An exception that is raised when an entity cannot be added to
    the database.
- CommitException: An exception that is raised when the database cannot be
    committed.
- DbException: An exception that is raised when there is an error in the
    database.
- FlushException: An exception that is raised when changes cannot be flushed
    to the database.
- RemoveException: An exception that is raised when an entity cannot be
    removed from the database.
"""

from abc import ABC, abstractmethod
from logging import getLogger
from typing import TypeVar

from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities import BaseEntity

logger = getLogger(__name__)


class BaseUnitOfWork(ABC):
    def __init__(
        self, session: Session | None = None, db_con: DBSession | None = None
    ) -> None:
        if not session:
            session = Session()

        self._session = session

        if not db_con:
            from src.managers import db

            db_con = DBSession(db.session)

        self._db = db_con

    @abstractmethod
    async def save(self) -> None:
        """
        Save all changes persistently.
        """

    @abstractmethod
    async def flush(self) -> None:
        """
        Flush all changes unpersistently.
        """

    @property
    def session(self) -> Session:
        return self._session

    @property
    def db(self) -> DBSession:
        return self._db


class UnitOfWork(BaseUnitOfWork):
    """
    The Unit of Work (UOW) class is responsible for managing the state of the
    database session and for persisting changes to the database.

    Attributes:
    ----
        _session: Session
            The database session.
        _db: Database
            The database instance.
    """

    async def save(self) -> None:
        """
        Save all changes persistently.

        Raises:
        ----
            DbException:
                If there is an error saving changes to the database.
        """
        try:
            await self._save()
        except (AddException, RemoveException, CommitException):
            logger.exception("Error saving changes to the database")
            await self._db.rollback()
            raise DbException()

    async def flush(self) -> None:
        """
        Flush all changes unpersistently.

        Raises:
        ----
            DbException:
               If there is an error flushing changes to the database.
        """
        try:
            await self._flush()
        except (AddException, RemoveException, FlushException):
            logger.exception("Error flushing changes to the database")
            await self._db.rollback()
            raise DbException()

    async def _save(self) -> None:
        """
        Save all changes persistently.
        """
        await self._process_all()
        await self._commit()

    async def _flush(self) -> None:
        """
        Flush all changes unpersistently.
        """
        await self._process_all()
        await self._flush_to_db()

    async def _process_all(self) -> None:
        """
        Add unpersisted data to the database session.
        """
        for entity in self._session.session:
            if entity.operation == "add":
                await self._add(entity.entity)
            else:
                await self._remove(entity.entity)

    async def _add(self, entity: BaseEntity) -> None:
        """
        Add an entity to the database session.

        Parameters:
        ----
            entity: BaseEntity
                The entity to add to the database.

        Raises:
        ----
            AddException:
                If there is an error adding the entity to the database
                session.
        """
        try:
            self._db.add(entity)
        except Exception:
            logger.exception("Error adding entity to the database")
            raise AddException()

    async def _remove(self, entity: BaseEntity) -> None:
        """
        Remove an entity from the database session.

        Parameters:
        ----
            entity: BaseEntity
                The entity to remove from the database.

        Raises:
        ----
            RemoveException:
                If there is an error removing the entity from the
                database session.
        """
        try:
            await self._db.delete(entity)
        except Exception:
            logger.exception("Error removing entity from the database")
            raise RemoveException()

    async def _commit(self) -> None:
        """
        Commit changes to the database.
        """
        try:
            await self._db.commit()
        except Exception:
            logger.exception("Error committing changes to the database")
            raise CommitException()

    async def _flush_to_db(self) -> None:
        """
        Flush changes to the database.
        """
        try:
            await self._db.flush()
        except Exception:
            logger.exception("Error flushing changes to the database")
            raise FlushException()


TUnitOfWork = TypeVar("TUnitOfWork", bound=UnitOfWork)


class DbException(Exception):
    def __init__(
        self,
        message: str = "An error occured while reading or writing to the db",
    ) -> None:
        super().__init__(message)


class AddException(Exception):
    def __init__(self, message: str = "An item couldn't be added") -> None:
        super().__init__(message)


class RemoveException(Exception):
    def __init__(self, message: str = "An item couldn't be removed") -> None:
        super().__init__(message)


class CommitException(Exception):
    def __init__(self, message: str = "Session couldn't be committed") -> None:
        super().__init__(message)


class FlushException(Exception):
    def __init__(self, message: str = "Session couldn't be flushed") -> None:
        super().__init__(message)
