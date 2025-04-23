from typing import TypeVar
from uuid import UUID

from sqlalchemy import UUID as UUID_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseEntity(Base):  # type: ignore[name-defined]
    """
    Base model for all models.

    Attributes:
        id (Mapped[UUID]): The primary key of the entity.

    Args:
        id (UUID): The unique identifier for the entity.
    """

    __abstract__ = True
    __tablename__ = "base"

    id: Mapped[UUID] = mapped_column(UUID_(as_uuid=True), primary_key=True)

    def __init__(self, id: UUID):
        """
        Initializes a new instance of the BaseEntity class.

        Args:
            id (UUID): The unique identifier for the entity.
        """
        self.id = id


TEntity = TypeVar("TEntity", bound=BaseEntity)
