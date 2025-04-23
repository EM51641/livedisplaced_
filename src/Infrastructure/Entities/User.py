"""
This module contains the UserEntity class which stores the user authentication
information.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Entities import BaseEntity


class UserEntity(BaseEntity):
    """
    This class stores the user authentication information.

    Attributes
    ----------
    id : UUID
        Internal unique user identifier
    first_name : str
        First name of the user
    last_name : str
        Last name of the user
    email : Optional[str]
        Account's email
    password : Optional[str]
        Account's password
    is_active : bool
        Is the Account active ?
    created : datetime
        The creation date of the account
    """

    __tablename__ = "user"

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(
        String(120), unique=True, nullable=True
    )
    password: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

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
        Initialise the user object by assigning
        first and last name of the user account

        Parameters
        ----------
        id : UUID
            Internal unique user identifier
        first_name : str
            First name of the user
        last_name : str
            Last name of the user
        email : Optional[str]
            Account's email
        password : Optional[str]
            Account's password
        is_active : bool
            Is the Account active ?
        created : datetime
            The creation date of the account

        Returns
        -------
        None
        """
        super().__init__(id)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_active = is_active
        self.created = created
