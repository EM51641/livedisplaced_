from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import UUID as UUID_
from sqlalchemy import DateTime
from sqlalchemy import Enum as ColEnum
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Entities import BaseEntity


class DisplacedCategory(Enum):
    """
    Displaced categories

    Attributes:
    ----
        REFUGEES: Refugees.
        ASYLIUM_SEEKERS: asylium seekers.
        INTERNALLY_DISPLACED: internally displaced.
        PEOPLE_OF_CONCERNS: people of concerns.
        RETURNED_INTERNALLY_DISPLACED: returned internally displaced.
    """

    REFUGEES = 0
    ASYLIUM_SEEKERS = 1
    INTERNALLY_DISPLACED = 2
    PEOPLE_OF_CONCERNS = 3


class PopulationEntity(BaseEntity):
    """
    Represents a population entity.

    Attributes:
    ----------
    id : UUID
        The unique identifier of the population entity.
    number : int
        The number of people of a given category.
    year : int
        The year at which the transfer happened.
    category : DisplacedCategory
        The category of the population affected.
    country_id : UUID
        The id of origin country.
    country_arrival_id : UUID
        The id of arrival country.
    created : datetime
        The date and time when the entity was created.

    """

    __tablename__ = "population"
    __table_args__ = (
        UniqueConstraint("year", "country_id", "country_arrival_id", "category"),
        {"extend_existing": True},
    )

    number: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped["DisplacedCategory"] = mapped_column(
        ColEnum(DisplacedCategory, validate_strings=True), nullable=False
    )

    country_id: Mapped[UUID] = mapped_column(
        UUID_(as_uuid=True),
        ForeignKey("country.id", ondelete="CASCADE"),
        nullable=False,
    )

    country_arrival_id: Mapped[UUID] = mapped_column(
        UUID_(as_uuid=True),
        ForeignKey("country.id", ondelete="CASCADE"),
        nullable=False,
    )

    created: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __init__(
        self,
        id: UUID,
        number: int,
        year: int,
        category: DisplacedCategory,
        country_id: UUID,
        country_arrival_id: UUID,
        created: datetime,
    ) -> None:
        self.id = id
        self.number = number
        self.year = year
        self.category = category
        self.country_id = country_id
        self.country_arrival_id = country_arrival_id
        self.created = created
