"""
This module contains integration tests for the PasscodeEntity model.
It tests if the columns of the fake PasscodeEntity table match the columns
of the actual PasscodeEntity table, and if the unique constraints of the
PasscodeEntity table are correctly set.
"""

from datetime import datetime
from typing import Literal

import pytest
from sqlalchemy import UUID, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Entities.Passcode import CredChoices, PasscodeEntity


class TestPasscodeEntityConfig:
    """
    This class contains tests for the PasscodeEntity model.
    """

    @pytest.fixture(autouse=True)
    def _fake_table(self, fake_sql_tables):
        """
        This fixture creates a fake PasscodeEntity table for testing purposes.
        """

        class FakePasscodeEntity(fake_sql_tables):
            __tablename__ = "passcode"
            __table_args__ = (UniqueConstraint("user_id", "category"),)

            id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)  # type: ignore

            user_id: Mapped[UUID] = mapped_column(  # type: ignore
                UUID(as_uuid=True),
                ForeignKey("user.id", ondelete="CASCADE"),
                nullable=False,
            )

            category: Mapped[Literal["RESET", "ACTIVATION"]] = mapped_column(  # type: ignore
                Enum(CredChoices), nullable=False
            )

            expiration: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # type: ignore

        self._table = FakePasscodeEntity

    def test_fields_number(self):
        """
        Tests if the number of fields in the PasscodeEntity is correct.
        """
        assert len(PasscodeEntity.__table__.columns) == 4

    @pytest.mark.parametrize(
        "field",
        [
            "id",
            "user_id",
            "category",
            "expiration",
        ],
    )
    def test_fields(self, field: str) -> None:
        """
        This test checks if the columns of the fake PasscodeEntity table
        match the columns of the actual PasscodeEntity table.
        """

        fake_table_field = self._table.__table__.columns[field]
        original_table_field = PasscodeEntity.__table__.columns[field]

        assert repr(fake_table_field) == repr(original_table_field)

    def test_constrains(self) -> None:
        """
        Tests if the constrains in the PasscodeEntity are correct.
        """
        fake_table_args = self._table.__table_args__
        original_table_args = PasscodeEntity.__table_args__

        assert repr(fake_table_args) == repr(original_table_args)
