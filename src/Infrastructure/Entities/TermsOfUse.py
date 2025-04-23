from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as UUID_
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Entities import BaseEntity


class TermsOfUseEntity(BaseEntity):
    """
    This class stores the terms of use information.

    Attributes:
    ----
        id: id of the row.
        created: Date at which the agreeent was created.
    """

    __tablename__ = "termsofuse"

    created: Mapped[datetime] = mapped_column(DateTime, nullable=False, unique=True)

    def __init__(self, id: UUID, created: datetime) -> None:
        """
        Initialise a terms of use object.

        Parameters:
        ----
            created: The terms of use creation date record.

        Returns:
        ----
            None
        """
        super().__init__(id)
        self.created = created


class SignedTermsOfUseEntity(BaseEntity):
    """
    Holds mapping between TermsAndConditions and Users
    aka keep track of the version for which the user
    agreed to be compliant.

    Attributes:
    ----
        id: id of the row.
        user_id: id of the concerned user.
        termofuse_id: id of the terms the user agreed to.
        signed: date of signature of the agreement.
    """

    __tablename__ = "user_termsofuse"
    __table_args__ = (UniqueConstraint("user_id", "termsofuse_id"),)

    user_id: Mapped[UUID] = mapped_column(
        UUID_(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )

    termsofuse_id: Mapped[UUID] = mapped_column(
        UUID_(as_uuid=True),
        ForeignKey("termsofuse.id", ondelete="CASCADE"),
        nullable=False,
    )

    signed: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __init__(
        self, id: UUID, user_id: UUID, termsofuse_id: UUID, signed: datetime
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.termsofuse_id = termsofuse_id
        self.signed = signed
