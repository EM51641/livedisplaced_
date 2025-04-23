"""
This module defines a Quart application manager that initializes
the Quart app, registers blueprints, and prepares queries to be used.
It also defines an abstract base class for Quart app and an exception
class for when no engine is found.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from alembic.config import Config
from alembic import command
from urllib.parse import urljoin
from quart import Quart, redirect
from sqlalchemy import TextClause, text
from sqlalchemy.ext.asyncio import AsyncConnection
from src.managers import db

logger = logging.getLogger(__name__)


class _BaseQuartApp(ABC):
    """
    Abstract base class for Quart applications.
    """

    @abstractmethod
    async def create_app(self) -> None:
        """
        Abstract method to create a Quart app.
        """


class QuartManager(_BaseQuartApp):
    """
    A class for managing the Quart app.

    Attributes:
    ----
        app: Quart
            The Quart app instance.
    """

    def __init__(self) -> None:
        """
        Initialise the Quart app.

        This method is called when an instance of the class is created. It sets up the Quart app by
        configuring the template and static folders.

        Parameters:
        ----------
            None

        Returns:
        ----------
            None
        """
        self.app = Quart(__name__)
        self.app.template_folder = os.path.join(
            os.path.dirname(self.app.root_path), os.environ["TEMPLATE_FOLDER"]
        )
        # self.app.static_folder = os.path.join(
        #     os.path.dirname(self.app.root_path), os.environ["STATIC_FOLDER"]
        # )
        self.app.config["SECRET_KEY"] = os.environ["APP_SECRET_KEY"]

    async def create_app(self) -> None:
        """
        Initializes the app, registers blueprints,
        and builds the database.
        """
        self._initialize_apps()
        self._register_blueprints()
        await self._build_db()

    def _initialize_apps(self) -> None:
        """
        Initialise third party apps.

        This method initializes various third-party apps used in the application.
        It sets up the login manager, CSRF protection, cache, email manager, log database,
        and the database itself. It also logs a message indicating that the external applications
        have been initialized.
        """

        from src.managers import csrf_protection, log_db, login_manager

        csrf_protection.init_app(self.app)

        login_manager.init_app(self.app)
        log_db.init_app()
        db.init(self.app)

        logger.info("External Application are initialized")

    def _register_blueprints(self) -> None:
        """
        Register the different blueprints.

        This method is responsible for registering the different blueprints in the application.
        It imports the necessary modules and creates blueprint objects for each blueprint.
        Then, it registers the blueprints with the root blueprint and finally registers the root blueprint
        with the application.

        Note: Make sure to import the required modules before calling this method.

        Example usage:
        _register_blueprints()
        """
        from src.Controllers import root_app
        from src.Controllers.Exceptions import app as exceptions_app

        @self.app.endpoint("static")
        async def _static(filename):
            static_url = os.environ.get("STATIC_URL")

            if static_url:
                return redirect(urljoin(static_url, filename))

            raise Exception("Static URL is not set")

        logger.info("Registring Blueprints")

        self.app.register_blueprint(root_app)
        self.app.register_blueprint(exceptions_app)

        for rule in self.app.url_map.iter_rules():
            logger.info(f"Endpoint: {rule.endpoint}, Path: {rule}")

        logger.info("Blueprints are registred")

    async def _build_db(self) -> None:
        """
        Get the engine and build the database.

        This method creates the necessary tables in the database and prepares the queries.

        Parameters:
        ----------
            None

        Returns:
        ----------
            None
        """
        assert db.engine

        async with db.engine.begin() as conn:
            run_migrations()
            await self._prepare_queries(conn)

        logger.info("Database is ready !!")

    async def _prepare_queries(self, connection: AsyncConnection) -> None:
        """
        Prepare queries to be used.

        Parameters:
        ----
            connection: AsyncConnection
                The database connection.
        """

        for filename in [
            "src/Extra/SQL/Home.sql",
            "src/Extra/SQL/Dashboard.sql",
            "src/Extra/SQL/Report.sql",
        ]:
            query = self._read_query(filename)
            await connection.execute(query)
            logger.info(f"Prepared queries at {filename}")

    def _read_query(self, filename: str) -> TextClause:
        """
        Read a file and return its content.

        Parameters:
        ----------
        filename : str
            The name of the file to be read.

        Returns:
        -------
        TextClause
            The query read from the file.
        """
        with open(filename) as file:
            query = text(file.read())

        return query


def run_migrations():
    """Run the alembic migrations programmatically"""
    # Create Alembic configuration object
    alembic_cfg = Config()

    # Set the location of the alembic.ini file
    # Assuming it's in the root of your project
    project_root = Path(__file__).parent.parent
    alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))

    # Optional: Set other config values
    # alembic_cfg.set_main_option('sqlalchemy.url', your_db_url)

    # Run the migration
    command.upgrade(alembic_cfg, "head")


async def create_app_manager() -> QuartManager:
    """
    Creates a new instance of QuartManager and initializes the Quart app.

    Returns:
        A new instance of QuartManager.

    Raises:
        Any exceptions that occur during the creation of the QuartManager or initialization of the Quart app.
    """
    quart_manager = QuartManager()
    await quart_manager.create_app()
    return quart_manager


class EngineNotFound(Exception):
    """
    Exception raised when an engine is not found.

    Attributes:
        message (str): Explanation of the error
    """

    def __init__(self, message: str = "Engine not found"):
        super().__init__(message)
