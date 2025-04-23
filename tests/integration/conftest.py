"""
This module contains fixtures for integration tests. Fixtures are functions
that are run before each test function to which they are applied. They provide
a fixed baseline so that tests execute reliably and produce consistent,
repeatable results. The fixtures in this module set up and tear down
connections to test databases, create and drop tables, and create and
return Quart applications for testing.
"""

import logging
import os
from asyncio import current_task
from pathlib import Path
from typing import Any, AsyncGenerator, Generator, Sequence, TypeVar

import pytest
import pytest_asyncio
from quart import Quart, template_rendered
from quart.typing import TestClientProtocol
from quart_auth import authenticated_client as logged_in_client
from sqlalchemy import URL, Select, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    close_all_sessions,
    create_async_engine,
)

from src.app import QuartManager
from tests.integration.Factory.termsofuse import (
    SignedTermsOfUseFactory,
    TermsOfUseFactory,
)
from tests.integration.Factory.user import UserFactory
from alembic import command
from alembic.config import Config
from src.Infrastructure import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DATABASE_URI = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USERNAME"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    database=os.environ["DB_NAME"],
)


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Creates and yields an async engine for connecting to a PostgreSQL database.

    Returns:
        AsyncGenerator[AsyncEngine, None]:
            An async generator that yields the engine.
    """
    logger.info("Creating engine")

    engine = create_async_engine(DATABASE_URI, future=True, echo=False)
    try:
        yield engine
    finally:
        logger.info("Disposing engine")
        await engine.dispose()
        logger.info("Engine disposed")


@pytest_asyncio.fixture(autouse=True)
async def reset_tables(engine: AsyncEngine) -> None:
    """
    Reinitialises the database by dropping all tables and recreating them.

    Args:
    ----
        engine (Engine):
            The asynchronous engine to use for creating the session.

    Returns:
    ----
        None
    """

    logger.info("Reseting tables")
    alembic_cfg = Config()

    # Set the location of the alembic.ini file
    # Assuming it's in the root of your project
    project_root = Path(__file__).parent.parent.parent
    alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))

    # Undo all migrations
    command.downgrade(alembic_cfg, "base")

    # Run the migration
    command.upgrade(alembic_cfg, "head")


@pytest_asyncio.fixture()
async def scoped_session(
    engine: AsyncEngine, reset_tables: None
) -> AsyncGenerator[async_scoped_session[AsyncSession], None]:
    """
    Creates an asynchronous scoped session using the given async_engine.

    Args:
        engine (AsyncEngine): The async engine to use for creating the session.

    Yields:
        AsyncSession: An asynchronous scoped session.
    """

    logger.info("Creating scoped session")

    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    logger.info("scoped session created")

    session = async_scoped_session(session_maker, scopefunc=lambda: id(current_task()))

    logger.info("scoped session created and opened")

    try:
        yield session
    finally:
        logger.info("Closing and removing scoped session")

        await close_all_sessions()

        logger.info("scoped session closed")

        await session.remove()

        logger.info("scoped session removed")


@pytest_asyncio.fixture
async def session(
    scoped_session: async_scoped_session[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Returns an async session.

    Args:
        session (async_scoped_session[AsyncSession]): The async session.

    Yields:
        AsyncSession: The async session.
    """
    logger.info("Creating session")
    session = scoped_session()
    logger.info("Session created")
    try:
        yield session
    finally:
        logger.info("Closing session")
        await session.close()
        logger.info("Session closed")


@pytest.fixture
def fake_sql_tables():
    from sqlalchemy.orm import DeclarativeBase

    class FakeBaseEntity(DeclarativeBase):
        pass

    return FakeBaseEntity


@pytest_asyncio.fixture(scope="session")
async def app() -> Quart:
    """
    Creates a Quart application and returns it.

    Returns:
        Quart: A Quart application.
    """
    quart_manager = QuartManager()
    quart_manager.app.config["WTF_CSRF_ENABLED"] = False
    quart_manager.app.config["QUART_AUTH_COOKIE_SECURE"] = False
    # quart_manager.app.static_folder = os.path.join(
    #     os.path.dirname(quart_manager.app.root_path), os.environ["STATIC_FOLDER"]
    # )

    logger.info("Creating app")
    await quart_manager.create_app()

    logger.info("App created")
    return quart_manager.app


@pytest_asyncio.fixture
async def client(app: Quart) -> AsyncGenerator[TestClientProtocol, None]:
    """
    Returns an authenticated client for testing purposes.
    Args:
        app (Quart): The Quart application instance.
    Yields:
        QuartClient: An authenticated client.
    """
    async with app.test_client() as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_client(
    client: TestClientProtocol,
    user_factory: UserFactory,
    terms_of_use_factory: TermsOfUseFactory,
    signed_terms_of_use_factory: SignedTermsOfUseFactory,
) -> AsyncGenerator[TestClientProtocol, None]:
    """
    Returns an authenticated client for testing purposes.

    Args:
        app (Quart): The Quart application instance.

    Yields:
        QuartClient: An authenticated client.
    """
    terms_of_use = await terms_of_use_factory.create_terms_of_use()
    user = await user_factory.create_user()
    await signed_terms_of_use_factory.create_signed_terms_of_use(
        user_id=user.id, termsofuse_id=terms_of_use.id
    )

    async with logged_in_client(client, str(user.id)):
        yield client


@pytest.fixture
def captured_templates(app) -> Generator[list[Any], None, None]:
    """
    A fixture that captures templates rendered by the application.

    Args:
        app (Quart): The Quart application instance.

    Yields:
        list[Any]: A list of templates rendered by the application.
    """
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def terms_of_use_factory(session: AsyncSession):
    """
    A factory for creating terms of use.

    Args:
        scoped_session (Asyncasync_scoped_session[AsyncSession]): The database session.

    Returns:
        Callable: A factory for creating terms of use.
    """
    from tests.integration.Factory.termsofuse import TermsOfUseFactory

    return TermsOfUseFactory(session=session)


@pytest.fixture
def signed_terms_of_use_factory(session: AsyncSession):
    """
    A factory for creating signed terms of use.

    Args:
        scoped_session (Asyncasync_scoped_session[AsyncSession]): The database session.

    Returns:
        Callable: A factory for creating signed terms of use.
    """
    from tests.integration.Factory.termsofuse import SignedTermsOfUseFactory

    return SignedTermsOfUseFactory(session=session)


@pytest.fixture
def oauth_factory(session: AsyncSession):
    """
    A factory for creating OAuth data.

    Args:
        scoped_session (Asyncasync_scoped_session[AsyncSession]): The database session.

    Returns:
        Callable: A factory for creating OAuth data.
    """
    from tests.integration.Factory.oauth import OauthFactory

    return OauthFactory(session=session)


@pytest.fixture
def user_factory(session: AsyncSession):
    """
    A factory for creating users.

    Args:
        scoped_session (Asyncasync_scoped_session[AsyncSession]): The database session.

    Returns:
        Callable: A factory for creating users.
    """
    from tests.integration.Factory.user import UserFactory

    return UserFactory(session=session)


@pytest.fixture
def passcode_factory(session: AsyncSession):
    """
    A factory for creating passcodes.

    Args:
        scoped_session (Asyncasync_scoped_session[AsyncSession]): The database session.

    Returns:
        Callable: A factory for creating passcodes.
    """
    from tests.integration.Factory.passcode import PasscodeFactory

    return PasscodeFactory(session=session)


@pytest.fixture
def continent_factory(session: AsyncSession):
    """
    A factory for creating continents.

    Args:
        scoped_session (Asyncasync_scoped_session[AsyncSession]): The database session.

    Returns:
        Callable: A factory for creating continents.
    """
    from tests.integration.Factory.geo import ContinentFactory

    return ContinentFactory(session=session)


@pytest.fixture
def region_factory(session: AsyncSession):
    """
    A factory for creating regions.

    Args:
        scoped_session (Asyncasync_scoped_session[AsyncSession]): The database session.

    Returns:
        Callable: A factory for creating regions.
    """
    from tests.integration.Factory.geo import RegionFactory

    return RegionFactory(session=session)


@pytest.fixture
def country_factory(session: AsyncSession):
    """
    A factory for creating countries.

    Args:
        scoped_session (Asyncasync_scoped_session[AsyncSession]): The database session.

    Returns:
        Callable: A factory for creating countries.
    """
    from tests.integration.Factory.geo import CountryFactory

    return CountryFactory(session=session)


@pytest.fixture
def population_factory(session: AsyncSession):
    """
    A factory for creating populations.

    Args:
        scoped_session (Asyncasync_scoped_session[AsyncSession]): The database session.

    Returns:
        Callable: A factory for creating populations.
    """
    from tests.integration.Factory.population import PopulationFactory

    return PopulationFactory(session=session)


@pytest.fixture
def faker():
    """
    Returns a Faker instance.

    Returns:
        Faker: A Faker instance.
    """
    from faker import Faker

    return Faker()


T = TypeVar("T")


async def resolve_query_one(query: Select[tuple[T]], session: AsyncSession) -> T:
    """
    Resolve the query to a string.

    Args:
        query (Select[tuple[T]]):
            The query to resolve.
        session (AsyncSession):
            The session to use for executing the query.

    Returns:
        T:
            The result of the query.
    """
    await session.reset()
    res = await session.execute(query)
    return res.scalar_one()


async def resolve_query_all(
    query: Select[tuple[T]], session: AsyncSession
) -> Sequence[T]:
    """
    Resolve the query to a string.

    Args:
        query (Select[tuple[T]]): The query to resolve.
        session (AsyncSession): The session to use for executing the query.

    Returns:
        Sequence[T]: The result of the query.
    """
    await session.reset()
    res = await session.execute(query)
    return res.scalars().all()
