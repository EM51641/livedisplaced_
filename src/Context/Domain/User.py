"""
The User and Account models are all here
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from werkzeug.security import check_password_hash, generate_password_hash

from src.Context.Domain import BusinessObject

if TYPE_CHECKING:
    from datetime import datetime
    from typing import Optional, TypedDict
    from uuid import UUID

    class TUserDomainDict(TypedDict):
        id: UUID
        first_name: str
        last_name: str
        email: str | None
        password: str | None
        is_active: bool
        created: datetime


class UserBusinessObject(BusinessObject):
    """
    User Business Object pattern
    """

    def __init__(
        self,
        id: UUID,
        first_name: str,
        last_name: str,
        email: Optional[str],
        password: Optional[str],
        is_active: bool,
        created: datetime,
    ) -> None:
        """
        Initialise the user object.

        Params:
        ----
            id: UUID
                The unique identifier for the user.
            first_name: str
                The first name of the user.
            last_name: str
                The last name of the user.
            email: Optional[str]
                The email address of the user (optional).
            password: Optional[str]
                The password of the user (optional).
            is_active: bool
                Whether the user is active or not.
            created: datetime
                The date and time the user was created.

        Returns:
        ----
            None
        """
        super().__init__(id)
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._password = password
        self._is_active = is_active
        self._created = created

    @property
    @abstractmethod
    def first_name(self) -> str:
        """Not implemented yet"""

    @property
    @abstractmethod
    def last_name(self) -> str:
        """Not implemented yet"""

    @property
    @abstractmethod
    def email(self) -> Optional[str]:
        """Not implemented yet"""

    @property
    @abstractmethod
    def password(self) -> Optional[str]:
        """Not implemented yet"""

    @property
    @abstractmethod
    def is_active(self) -> bool:
        """Not implemented yet"""

    @property
    @abstractmethod
    def created(self) -> datetime:
        """Not implemented yet"""

    @abstractmethod
    def set_password(self, value: str) -> None:
        """Not implemented yet"""

    @abstractmethod
    def check_password(self, value: str) -> bool:
        """Not implemented yet"""

    @abstractmethod
    def set_email(self, email: str) -> None:
        """Not implemented yet"""

    @abstractmethod
    def set_active(self) -> None:
        """Not implemented yet"""


class User(UserBusinessObject):
    """
    User Business Object.
    """

    @property
    def first_name(self) -> str:
        return self._first_name

    @property
    def last_name(self) -> str:
        return self._last_name

    @property
    def email(self) -> Optional[str]:
        return self._email

    @property
    def password(self) -> Optional[str]:
        return self._password

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created(self) -> datetime:
        return self._created

    def set_password(self, value: str) -> None:
        """
        Set a password for the user account

        Parameters:
        ----
            value: str
                password

        Returns:
        ----
            None
        """
        self._password = generate_password_hash(value)

    def check_password(self, value: str) -> bool:
        """
        check password of an user account.

        Parameters:
        ----
            value: str

        Returns:
        ----
            None
        """
        if self._password:
            return check_password_hash(self._password, value)

        return False

    def set_active(self) -> None:
        """
        Set the user account active.

        Parameters:
        ----
            None

        Returns:
        ----
            None
        """
        self._is_active = True

    def set_email(self, email: str) -> None:
        """
        Set the user email

        Parameters:
        ----
            email: email

        Returns:
        ----
            None
        """
        self._email = email

    def to_dict(self) -> TUserDomainDict:
        """
        Return the dictionary containing the user's data.

        Params:
        ----
            None

        Returns:
        ----
            None
        """
        return {
            "id": self._id,
            "first_name": self._first_name,
            "last_name": self._last_name,
            "email": self._email,
            "password": self._password,
            "is_active": self._is_active,
            "created": self._created,
        }

    def __str__(self) -> str:
        """
        Return a string representation of the user.

        Params:
        ----
            None

        Returns:
        ----
            None
        """
        return (
            f"User(id={self._id}, email={self._email}, "
            f"first_name={self._first_name}, last_name={self._last_name}, "
            f"created={self._created}, is_active={self._is_active})"
        )

    def __repr__(self) -> str:
        """
        Return a string representation of the user.

        Params:
        ----
            None

        Returns:
        ----
            None
        """
        return (
            f"User(id={repr(self._id)}, email={repr(self._email)}, "
            f"first_name={repr(self._first_name)}, last_name={repr(self._last_name)}, "
            f"created={repr(self._created)}, is_active={repr(self._is_active)})"
        )
