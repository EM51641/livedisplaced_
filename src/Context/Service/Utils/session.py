from abc import ABC, abstractmethod
from typing import Literal, NamedTuple

from src.Infrastructure.Entities import BaseEntity


class SessionEntity(NamedTuple):
    """
    Session Entity.
    """

    operation: Literal["add", "remove"]
    entity: BaseEntity


class SessionBase(ABC):
    """
    Session Manager
    """

    @property
    @abstractmethod
    def session(self) -> list[SessionEntity]:
        """Not implemented yet"""

    @abstractmethod
    def remove(self, item: BaseEntity) -> None:
        """Not implemented yet"""

    @abstractmethod
    def add(self, item: BaseEntity) -> None:
        """Not implemented yet"""


class Session(SessionBase):
    """
    Session Manager
    """

    _session: list[SessionEntity]

    def __init__(self) -> None:
        self._session = []

    @property
    def session(self) -> list[SessionEntity]:
        return self._session

    def add(self, item: BaseEntity) -> None:
        """
        Add object to session.

        Params:
        ----
           item: Entity

        Returns:
        ----
           None.

        Usage:
        ----
            >>> from app.repositories.session import SessionManager
            >>> session_manager = SessionManager()
            >>> session_manager.add(item)

        Raises:
        ----
            Any Exception.
        """
        session_entity = SessionEntity(operation="add", entity=item)
        self._session.append(session_entity)

    def remove(self, item: BaseEntity) -> None:
        """
        Add delete object from a session.

        Params:
        ----
           item: Entity

        Returns:
        ----
           None.

        Usage:
        ----
            >>> from app.repositories.session import SessionManager
            >>> session_manager = SessionManager()
            >>> session_manager.delete(item)

        Raises:
        ----
            Any Exception.
        """
        session_entity = SessionEntity(operation="remove", entity=item)
        self._session.append(session_entity)
