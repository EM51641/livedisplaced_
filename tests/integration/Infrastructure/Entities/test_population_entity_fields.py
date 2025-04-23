from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import UUID as UUID_
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Entities.Geo import ContinentEntity, CountryEntity, RegionEntity
from src.Infrastructure.Entities.Population import DisplacedCategory, PopulationEntity


class TestPopulationEntityConfig:
    """
    This class contains tests for the Population model.
    """

    @pytest.fixture(autouse=True)
    def _fake_table(self, fake_sql_tables):
        """
        This fixture creates a fake PopulationEntity table for testing
        purposes.
        """

        class FakePopulationEntityEntity(fake_sql_tables):
            __tablename__ = "population"
            __table_args__ = (
                UniqueConstraint(
                    "year", "country_id", "country_arrival_id", "category"
                ),
                {"extend_existing": True},
            )

            id: Mapped[UUID] = mapped_column(UUID_(as_uuid=True), primary_key=True)  # type: ignore

            number: Mapped[int] = mapped_column(Integer, nullable=False)  # type: ignore
            year: Mapped[int] = mapped_column(Integer, nullable=False)  # type: ignore
            category: Mapped["DisplacedCategory"] = mapped_column(  # type: ignore
                Enum(DisplacedCategory, validate_strings=True), nullable=False
            )

            country_id: Mapped[UUID] = mapped_column(  # type: ignore
                UUID_(as_uuid=True),
                ForeignKey(CountryEntity.id, ondelete="CASCADE"),
                nullable=False,
            )

            country_arrival_id: Mapped[UUID] = mapped_column(  # type: ignore
                UUID_(as_uuid=True),
                ForeignKey(CountryEntity.id, ondelete="CASCADE"),
                nullable=False,
            )

            created: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # type: ignore

        self._table = FakePopulationEntityEntity

    def test_fields_number(self):
        """
        Tests if the number of fields in the PopulationEntity is correct.
        """
        assert len(PopulationEntity.__table__.columns) == 7

    @pytest.mark.parametrize(
        "field",
        [
            "id",
            "number",
            "year",
            "category",
            "country_id",
            "country_arrival_id",
            "created",
        ],
    )
    def test_fields(self, field: str) -> None:
        """
        Tests if the constrains in the PopulationEntity are correct.
        """
        fake_table_field = self._table.__table__.columns[field]
        original_table_field = PopulationEntity.__table__.columns[field]

        assert repr(fake_table_field) == repr(original_table_field)

    def test_constrains(self) -> None:
        """
        Tests if the constrains in the PopulationEntity are correct.
        """
        fake_table_args = self._table.__table_args__
        original_table_args = PopulationEntity.__table_args__

        assert repr(fake_table_args) == repr(original_table_args)


class TestContinentEntityConfig:
    @pytest.fixture(autouse=True)
    def _fake_table(self, fake_sql_tables) -> None:
        class FakeContinentEntity(fake_sql_tables):
            __tablename__ = "continent"

            id: Mapped[UUID] = mapped_column(UUID_(as_uuid=True), primary_key=True)

            name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

        self._table = FakeContinentEntity

    def test_fields_number(self):
        """
        Tests if the number of fields in the ContinentEntity is correct.
        """
        assert len(ContinentEntity.__table__.columns) == 2

    @pytest.mark.parametrize("field", ["id", "name"])
    def test_fields(self, field: str) -> None:
        """
        Tests if the fields in the ContinentEntity are correct.
        """
        fake_table_field = self._table.__table__.columns[field]
        original_table_field = ContinentEntity.__table__.columns[field]

        assert repr(fake_table_field) == repr(original_table_field)


class TestRegionEntityConfig:
    """
    This class tests the RegionEntity configuration.

    Methods:
    - _fake_table: A fixture that creates a fake table for the RegionEntity.
    - test_fields_number: Tests if the number of fields in the RegionEntity
            is correct.
    - test_fields: Tests if the fields in the RegionEntity are correct.
    """

    @pytest.fixture(autouse=True)
    def _fake_table(self, fake_sql_tables) -> None:
        """
        A fixture that creates a fake table for the RegionEntity.
        """

        class FakeRegionEntity(fake_sql_tables):
            __tablename__ = "region"

            id: Mapped[UUID] = mapped_column(UUID_(as_uuid=True), primary_key=True)

            name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

            continent_id: Mapped[UUID] = mapped_column(
                UUID_(as_uuid=True),
                ForeignKey("continent.id", ondelete="CASCADE"),
                nullable=False,
            )

        self._table = FakeRegionEntity

    def test_fields_number(self):
        """
        Tests if the number of fields in the RegionEntity is correct.
        """
        assert len(RegionEntity.__table__.columns) == 3

    @pytest.mark.parametrize("field", ["id", "name", "continent_id"])
    def test_fields(self, field: str) -> None:
        """
        Tests if the fields in the RegionEntity are correct.
        """
        fake_table_field = self._table.__table__.columns[field]
        original_table_field = RegionEntity.__table__.columns[field]

        assert repr(fake_table_field) == repr(original_table_field)


class TestCountryEntityConfig:
    @pytest.fixture(autouse=True)
    def _fake_table(self, fake_sql_tables) -> None:
        class FakeCountryEntity(fake_sql_tables):
            __tablename__ = "country"

            id: Mapped[UUID] = mapped_column(UUID_(as_uuid=True), primary_key=True)

            name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

            iso: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)

            iso_2: Mapped[str] = mapped_column(String(2), unique=True, nullable=True)

            is_recognized: Mapped[bool] = mapped_column(Boolean, nullable=False)

            region_id: Mapped[UUID] = mapped_column(
                UUID_(as_uuid=True),
                ForeignKey("region.id", ondelete="CASCADE"),
                nullable=False,
            )

        self._table = FakeCountryEntity

    def test_fields_number(self) -> None:
        assert len(CountryEntity.__table__.columns) == 6

    @pytest.mark.parametrize(
        "field",
        [
            "id",
            "name",
            "iso",
            "iso_2",
            "is_recognized",
            "region_id",
        ],
    )
    def test_fields(self, field: str):
        """
        Test that the given field in the fake table matches the corresponding
        field in the original table.

        Args:
            field (str): The name of the field to test.

        Returns:
            None
        """
        fake_table_field = self._table.__table__.columns[field]
        original_table_field = CountryEntity.__table__.columns[field]

        assert repr(fake_table_field) == repr(original_table_field)
