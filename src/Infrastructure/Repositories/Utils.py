"""
Global Reposiotory

This module contains the implementation of the Repository pattern for the infrastructure layer of the application.
It provides a base repository class and a concrete repository class that can be used to interact with the database.

Classes:
- _RepositoryBase: Abstract base class for repositories.
- RepositoryBase: Concrete implementation of the repository base class.
- NoEntityFound: Exception raised when no entity is found.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Sequence, TypeVar
from uuid import UUID

from sqlalchemy import Function, Select
from sqlalchemy.exc import NoResultFound

from src.Context.Domain import BusinessObject
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities import BaseEntity

if TYPE_CHECKING:
    from src.Infrastructure.Repositories.Mappers import EntityDomainMapper

TEntity = TypeVar("TEntity", bound=BaseEntity)
TDomain = TypeVar("TDomain", bound=BusinessObject)


class _RepositoryBase(ABC, Generic[TEntity, TDomain]):
    """
    Repository Pattern.
    """

    @property
    @abstractmethod
    def session(self) -> Session:
        """
        Not implemented
        """

    @property
    @abstractmethod
    def entity_type(self) -> type[TEntity]:
        """
        Not implemented
        """

    @property
    @abstractmethod
    def db(self) -> DBSession:
        """
        Not implemented
        """

    @property
    @abstractmethod
    def entity_domain_mapper(
        self,
    ) -> EntityDomainMapper[TEntity, TDomain]:
        """
        Not implemented
        """

    @abstractmethod
    def add(self, domain: TDomain) -> BaseEntity:
        pass

    @abstractmethod
    async def modify(self, domain: TDomain) -> BaseEntity:
        pass

    @abstractmethod
    async def remove(self, domain: TDomain) -> BaseEntity:
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID) -> TDomain:
        pass


class RepositoryBase(_RepositoryBase[TEntity, TDomain]):
    """
    Repository Pattern.
    """

    def __init__(
        self,
        session: Session,
        db: DBSession,
        entity_type: type[TEntity],
        entity_domain_mapper: EntityDomainMapper[TEntity, TDomain],
    ) -> None:
        self._entity_type = entity_type
        self._entity_domain_mapper = entity_domain_mapper
        self._session = session
        self._db = db

    @property
    def entity_type(self) -> type[TEntity]:
        return self._entity_type

    @property
    def session(self) -> Session:
        return self._session

    @property
    def db(self) -> DBSession:
        return self._db

    @property
    def entity_domain_mapper(
        self,
    ) -> EntityDomainMapper[TEntity, TDomain]:
        return self._entity_domain_mapper

    def add(self, domain: TDomain) -> BaseEntity:
        """
        Add a new domain.

        Params:
        ----
            domain: TDomain

        Returns:
        ----
            BaseEntity
        """
        record = self._entity_domain_mapper.to_entity(domain)
        self._session.add(record)
        return record

    async def modify(self, domain: TDomain) -> BaseEntity:
        """
        Modify a domain.

        Parameters:
        ----
            :param domain: TDomain

        Returns:
        ----
            BaseEntity
        """
        query = self._query_by_id(domain.id)
        record = await self._find_first_record(query)
        self._entity_domain_mapper.map_to_entity(domain, record)
        return record

    async def remove(self, domain: TDomain) -> BaseEntity:
        """
        Remove a domain.

        Parameters:
        ----
            :param passcode: TDomain

        Returns:
        ----
            BaseEntity
        """
        query = self._query_by_id(domain.id)
        record = await self._find_first_record(query)
        self.session.remove(record)
        return record

    async def find_by_id(self, id: UUID) -> TDomain:
        """
        Return the domain by id.

        Params:
        ----
            id: UUID

        Returns:
        ----
            TDomain
        """
        query = self._query_by_id(id)
        domain = await self._find_first_domain(query)
        return domain

    async def _find_first_domain(self, query: Select[tuple[TEntity]]) -> TDomain:
        """
        Find the first domain.

        Parameters:
        ----
            :param query: query of the oauth.

        Returns:
        ----
            TDomain
        """
        record = await self._find_first_record(query)
        domain = self._entity_domain_mapper.to_domain(record)  # type: ignore
        return domain

    async def _find_first_record(self, query: Select[tuple[TEntity]]) -> TEntity:
        """
        Find the first record.

        Parameters:
        ----
            :param query: query to get the first record.

        Returns:
        ----
            TEntity
        """
        res = await self._db.execute(query)

        try:
            record = res.scalar_one()
        except NoResultFound:
            # await self._db.rollback()
            raise NoEntityFound()

        return record

    def _query_by_id(self, id: UUID) -> Select[tuple[TEntity]]:
        """
        Get a query searching a record by id.

        Params:
        ----
            id: int

        Returns:
        ----
           Query[TEntity]
        """
        select_table = self._db.select(self._entity_type)
        query = select_table.filter(self._entity_type.id == id)
        return query


class NoEntityFound(Exception):
    """
    Exception raised when no entity is found.
    """

    def __init__(self, message: str = "No entity found.") -> None:
        super().__init__(message)


class DALBase(ABC):
    def __init__(self, db_con: DBSession | None = None) -> None:
        if not db_con:
            from src.managers import db

            db_con = DBSession(db.session)
        self._db = db_con

    async def _execute_statement_and_return_sequence(
        self, stmt: Function[Any]
    ) -> Sequence[Any]:
        """
        Execute statement.

        Parameters:
        ----
            stmt: Function[Any]

        Returns:
        ----
            Sequence[Any]
        """

        result = await self._db.execute(stmt)
        return result.scalars().all()
