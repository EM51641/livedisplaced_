"""
This module contains the Passcode domain business object and its related
classes.

Classes:
- PasscodeBusinessObject: Base class for Passcode business object.
- Passcode: Passcode business object.
"""

from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID

from src.Context.Domain import BusinessObject

if TYPE_CHECKING:
    from typing import TypedDict

    class TPasscodeDomainDict(TypedDict):
        id: UUID
        user_id: UUID
        category: Literal["RESET", "ACTIVATION"]
        expiration: datetime


class PasscodeBusinessObject(BusinessObject):
    @property
    @abstractmethod
    def category(self) -> Literal["RESET", "ACTIVATION"]:
        """Not implemented yet"""

    @property
    @abstractmethod
    def user_id(self) -> UUID:
        """Not implemented yet"""

    @property
    @abstractmethod
    def expiration(self) -> datetime:
        """Not implemented yet"""


class Passcode(PasscodeBusinessObject):
    """
    Passcode business object
    """

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        category: Literal["RESET", "ACTIVATION"],
        expiration: datetime,
    ) -> None:
        """
        Initialise the passcode business object.

        Parameters:
        ----
            :param id: UUID
                The unique identifier for the passcode.
            :param user_id: UUID
                The unique identifier for the user associated with the
                passcode.
            :param category: CredChoices
                The category of the passcode.
            :param expiration: datetime
                The expiration date and time of the passcode.

        Returns:
        ----
            None
        """
        super().__init__(id)
        self._user_id = user_id
        self._category = category
        self._expiration = expiration

    @property
    def category(self) -> Literal["RESET", "ACTIVATION"]:
        """
        Get the category of the passcode.
        """
        return self._category  # type: ignore

    @property
    def user_id(self) -> UUID:
        """
        Get the unique identifier for the user associated with the passcode.

        Returns:
        ----
            UUID
                The unique identifier for the user associated with the
                passcode.
        """
        return self._user_id

    @property
    def expiration(self) -> datetime:
        """
        Get the expiration date and time of the passcode.

        Returns:
        ----
            datetime
                The expiration date and time of the passcode.
        """
        return self._expiration

    def to_dict(self) -> TPasscodeDomainDict:
        """
        Return the passcode as a dictionary.

        Returns:
        ----
            TPasscodeDomainDict
                The passcode as a dictionary.
        """
        return {
            "id": self._id,
            "user_id": self._user_id,
            "category": self._category,  # type: ignore
            "expiration": self._expiration,
        }

    def __str__(self) -> str:
        """
        Return a string representation of the passcode.

        Returns:
        ----
            str
                A string representation of the passcode.
        """
        return (
            f"Passcode(id={self._id}, user_id={self._user_id}, "
            f"category={self._category}, expiration={self._expiration})"
        )

    def __repr__(self) -> str:
        """
        Return a string representation of the passcode.

        Returns:
        ----
            str
                A string representation of the passcode.
        """
        return (
            f"Passcode(id={repr(self._id)}, user_id={repr(self._user_id)}, "
            f"category={repr(self._category)}, expiration={repr(self._expiration)})"  # noqa
        )
