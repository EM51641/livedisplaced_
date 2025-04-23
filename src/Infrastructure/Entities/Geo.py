"""
This module contains classes that represent geographic entities such as
continents, regions, and countries.
"""

from uuid import UUID

from sqlalchemy import UUID as UUID_
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Entities import BaseEntity


class ContinentEntity(BaseEntity):
    """
    Represents a continent.

    Attributes:
    ----
        id: UUID
            The unique identifier for the continent.
        name: str
            The name of the continent.
    """

    __tablename__ = "continent"
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    def __init__(self, id: UUID, name: str) -> None:
        super().__init__(id)
        self.name = name


class RegionEntity(BaseEntity):
    """
    Represents a region entity, which stores information about a region.

    Attributes:
        id (UUID): The ID of the region entity.
        name (str): The name of the region.
        continent_id (UUID): The ID of the continent where the region is
                        located.
    """

    __tablename__ = "region"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    continent_id: Mapped[UUID] = mapped_column(
        UUID_(as_uuid=True),
        ForeignKey("continent.id", ondelete="CASCADE"),
        nullable=False,
    )
    continent = relationship(ContinentEntity, lazy="selectin")  # type: ignore

    def __init__(self, id: UUID, name: str, continent_id: UUID) -> None:
        super().__init__(id)
        self.name = name
        self.continent_id = continent_id


class CountryEntity(BaseEntity):
    """
    Stores all the official and
    non-recognized countries by the UN.

    Attributes:
    ----
        id: UUID
            id of the row.
        name: str
            name of the country.
        iso: str
            iso 3 code of the country.
        iso_2: str
            iso 2 code of the country.
        unhcr_code: str
            unhcr code of the country
        is_recognized: bool
            is the country official ?
        subcontinent_id: int
            id of the subcontinent where the country
            is located on
    """

    __tablename__ = "country"
    __mapper_args__ = {"eager_defaults": True}

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    iso: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    iso_2: Mapped[str] = mapped_column(String(2), unique=True, nullable=True)
    is_recognized: Mapped[bool] = mapped_column(Boolean, nullable=False)
    region_id: Mapped[UUID] = mapped_column(
        UUID_(as_uuid=True), ForeignKey("region.id", ondelete="CASCADE"), nullable=False
    )

    region = relationship(RegionEntity, lazy="noload")  # type: ignore

    def __init__(
        self,
        id: UUID,
        name: str,
        iso: str,
        iso_2: str,
        is_recognized: bool,
        region_id: UUID,
    ) -> None:
        """
        Initialize a Geo object.

        Args:
            id (UUID): The unique identifier for the Geo object.
            name (str): The name of the Geo object.
            iso (str): The ISO code of the Geo object.
            iso_2 (str): The ISO 2-letter code of the Geo object.
            is_recognized (bool): Indicates whether the Geo object is recognized.
            region_id (UUID): The unique identifier of the region associated with the Geo object.
        """
        super().__init__(id)
        self.name = name
        self.iso = iso
        self.iso_2 = iso_2
        self.is_recognized = is_recognized
        self.region_id = region_id
