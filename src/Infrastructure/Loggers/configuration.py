"""
This module provides a custom logger class that extends the default Logger
class from the logging module. It also provides a custom queue listener
class that extends the default QueueListener class from the logging module.
The module also provides a NoSQL database class that provides methods for
initializing the database.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from logging import LogRecord
from typing import TYPE_CHECKING

from quart import has_request_context, request

if TYPE_CHECKING:

    class CustomLogRecord(LogRecord):
        time: str
        remote: str
        endpoint: str


original_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs) -> CustomLogRecord:
    record = original_factory(*args, **kwargs)
    record.time = datetime.now(UTC)
    if has_request_context():
        record.remote = request.remote_addr
        record.endpoint = request.url
    else:
        record.remote = None
        record.endpoint = None
    return record  # type: ignore


class BaseAsyncLogger(ABC):
    @abstractmethod
    def init_app(self) -> None:
        """Not implemented yet"""


class AsyncLogger(BaseAsyncLogger):
    """
    Configures an Asynchronous logger linked to a NoSQL database.
    This class that provides methods for initializing the database.
    """

    def init_app(self):
        """
        Initializes the database using the Quart app configuration.
        """
        self._init_config_logger_factory()
        self._init_config_cloudwatch()

    def _init_config_logger_factory(self) -> None:
        """
        Initializes the logger configuration.
        """
        logging.setLogRecordFactory(record_factory)

    def _init_config_cloudwatch(self) -> None:
        """
        Initializes the logger configuration for CloudWatch.
        """
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
