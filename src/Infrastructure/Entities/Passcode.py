"""
The User and Account models are all here
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import UUID as UUID_
from sqlalchemy import DateTime
from sqlalchemy import Enum as ColEnum
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Entities import BaseEntity


class CredChoices(Enum):
    """
    key of the operation and value
    representing the state of the passcode.
    """

    RESET: str = "RESET"  # type: ignore
    ACTIVATION: str = "ACTIVATION"  # type: ignore


class PasscodeEntity(BaseEntity):
    """
    This class stores the request for resetting the account's
    password or the activating the account.

    Attributes
    ----
        id: uuid token used to generate the link in order
            to activate the account or get back the password.
        user_id:
            The unique user identifier, same as the User.id.
        category:
            Resetting password or activating the account.
        expiration:
            Expiration time.
    """

    __tablename__ = "passcode"
    __table_args__ = (UniqueConstraint("user_id", "category"),)

    user_id: Mapped[UUID] = mapped_column(
        UUID_(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )

    category: Mapped[CredChoices] = mapped_column(ColEnum(CredChoices), nullable=False)

    expiration: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __init__(
        self, id: UUID, user_id: UUID, category: CredChoices, expiration: datetime
    ) -> None:
        """
        Initialise

        Parameters:
        ----
            id: UUID
            user_id: UUID
            category: CredChoiceType
            expiration: datetime

        Returns:
        ----
            None
        """
        self.id = id
        self.user_id = user_id
        self.category = category
        self.expiration = expiration
