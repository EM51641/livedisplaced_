from __future__ import annotations

import os
from asyncio import current_task
from typing import Callable, Optional, TypeVar, overload

from quart import Quart
from quart.globals import app_ctx
from sqlalchemy import Function, Result, Select, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.engine.url import URL
from src.Infrastructure.Entities import BaseEntity

TEntity = TypeVar("TEntity", bound=BaseEntity)


class DBSession:
    def __init__(self, session: async_scoped_session[AsyncSession]) -> None:
        self._session = session

    @property
    def session(self) -> async_scoped_session[AsyncSession]:
        """
        Returns the session object for interacting with the database.

        Returns:
            async_scoped_session[AsyncSession]: The session object.
        """
        return self._session

    def add(self, entity: BaseEntity) -> None:
        """
        Adds an entity to the database.

        Args:
            entity (BaseEntity): The entity to be added.

        Returns:
            None
        """
        self._session.add(entity)

    async def delete(self, entity: BaseEntity) -> None:
        """
        Deletes the given entity from the database.

        Args:
            entity (BaseEntity): The entity to be deleted.

        Returns:
            None
        """
        await self._session.delete(entity)

    async def commit(self) -> None:
        """
        Commits the current transaction to the database.
        """
        await self._session.commit()

    async def flush(self) -> None:
        """
        Flushes the changes made in the session to the database.
        """
        await self._session.flush()

    async def rollback(self) -> None:
        """
        Rollbacks the current transaction.

        This method rolls back any changes made within the current transaction.
        """
        await self._session.rollback()

    def select(self, entity: type[TEntity]) -> Select[tuple[TEntity]]:
        """
        Selects records from the database for the given entity.

        Args:
            entity (type[TEntity]): The type of entity to select records for.

        Returns:
            Select[tuple[TEntity]]: A query object representing the select operation.

        """
        return select(entity)

    @overload
    async def execute(
        self, query: Select[tuple[TEntity]]
    ) -> Result[tuple[TEntity]]: ...

    @overload
    async def execute(self, query: Function[TEntity]) -> Result[tuple[TEntity]]: ...

    async def execute(  # type: ignore
        self, query: Select[tuple[TEntity, ...]] | Function[TEntity]
    ) -> Result[tuple[TEntity, ...]]:
        res = await self._session.execute(query)
        return res


class DBManager:
    """
    A class representing a database connection and operations.

    Attributes:
    ----
    _engine (Optional[AsyncEngine]): The SQLAlchemy engine.
    _session (async_scoped_session[AsyncSession]): The scoped session.

    Methods:
    ----
    __init__(): Initializes the Database object.
    session(): Returns the session object.
    engine(): Returns the engine object.
    add(entity: BaseEntity): Adds an entity to the session.
    delete(entity: BaseEntity): Deletes an entity from the session.
    commit(): Commits the changes made in the session.
    flush(): Flushes the changes made in the session.
    rollback(): Rolls back the changes made in the session.
    select(entity: type[TEntity]): Creates a select query for the specified entity.
    execute(query: Select[tuple[TEntity]] | Function[TEntity]): Executes the specified query.
    init(app: Quart): Initializes the session with the app context.
    _make_engine(): Creates the SQLAlchemy engine.
    _make_scoped_session(engine: AsyncEngine | None = None, scope_fun: Callable[[], int] | None = None):
        Constructs a scoped session.
    _teardown_session(exc: BaseException | None): Tears down the session.
    _get_current_context(): Returns the current app context.
    _get_current_task(): Returns the current task.
    """

    _engine: Optional[AsyncEngine]

    def __init__(self, scoped_fun: Callable[[], int]) -> None:
        """
        Initializes a new instance of the Database class.
        """
        self._engine = None
        self._scope_fun = scoped_fun
        self._session = self._make_scoped_session()

    @property
    def session(self) -> async_scoped_session[AsyncSession]:
        """
        Returns the session object for interacting with the database.

        Returns:
            async_scoped_session[AsyncSession]: The session object.
        """
        return self._session

    @property
    def engine(self) -> Optional[AsyncEngine]:
        """
        Returns the engine object used for database operations.

        Returns:
            Optional[AsyncEngine]: The engine object used for database operations.
        """
        return self._engine

    def init(self, app: Quart) -> None:
        """
        Initialise the session with the app context

        Parameters:
        ----
            app (Quart): The Quart app
        """
        self._engine = self._make_engine()
        self._session = self._make_scoped_session()
        app.teardown_appcontext(self._teardown_session)
        app.logger.info("DB Session scoped initialised")

    def init_db(self) -> None:
        """
        Initializes the database.

        Raises:
            EngineNotFound: If the engine is not found.
        """
        self._engine = self._make_engine()
        self._session = self._make_scoped_session()

    def _make_engine(self) -> AsyncEngine:
        """
        Make the SQLAlchemy engine.

        Returns:
        ----
            AsyncEngine
        """
        url = URL.create(
            drivername="postgresql+psycopg",
            username=os.environ["DB_USERNAME"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            database=os.environ["DB_NAME"],
        )
        return create_async_engine(url=url, pool_size=5, max_overflow=0)  # type: ignore

    def _make_scoped_session(self) -> async_scoped_session[AsyncSession]:
        """
        Construct scoped session.

        Parameters:
        ----
            engine (Optional[AsyncEngine]): The SQLAlchemy engine

        Returns:
        ----
            async_scoped_session[AsyncSession]
        """
        session_maker = async_sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )
        session = async_scoped_session(session_maker, scopefunc=self._scope_fun)
        return session

    async def _teardown_session(self, exc: BaseException | None) -> None:
        await self._session.close()
        await self._session.remove()

    def _get_current_context(self) -> int:
        id_ = id(app_ctx._get_current_object())  # type: ignore
        return id_

    def _get_current_task(self) -> int:
        id_ = id(current_task())
        return id_


class EngineNotFound(Exception):
    def __init__(self, message: str = "Engine not found") -> None:
        super().__init__(message)
