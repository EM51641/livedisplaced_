from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import UUID as UUID_
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Entities.TermsOfUse import (
    SignedTermsOfUseEntity,
    TermsOfUseEntity,
)


class TestTermsOfUseEntityConfig:
    """Test class for testing the configuration of the TermsOfUse entity."""

    @pytest.fixture(autouse=True)
    def _fake_table(self, fake_sql_tables):
        """Fixture that creates a fake table for testing purposes."""

        class FakeTermsOfUseEntity(fake_sql_tables):
            __tablename__ = "termsofuse"

            id: Mapped[UUID] = mapped_column(UUID_(as_uuid=True), primary_key=True)  # type: ignore
            created: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # type: ignore

        self._table = FakeTermsOfUseEntity

    @pytest.mark.parametrize(
        "field",
        ["id", "created"],
    )
    def test_fields(self, field: str) -> None:
        """
        This test checks if the columns of the fake TermsOfUseEntity table
        match the columns of the actual TermsOfUseEntity table.
        """

        fake_table_field = self._table.__table__.columns[field]
        original_table_field = TermsOfUseEntity.__table__.columns[field]

        assert repr(fake_table_field) == repr(original_table_field)

    def test_constrains(self) -> None:
        """
        Tests if the constrains in the TermsOfUseEntity are correct.
        """
        fake_table_args = getattr(self._table, "__table_args__", "NA")
        original_table_args = getattr(TermsOfUseEntity, "__table_args__", "NA")

        assert repr(fake_table_args) == repr(original_table_args)


class TestSignedTermsOfUseEntityConfig:
    @pytest.fixture(autouse=True)
    def _fake_table(self, fake_sql_tables):
        """
        Creates a fake SQLAlchemy entity class that represents a signed terms
        of use record for a user.

        The entity has the following fields:
        - id: a UUID primary key
        - user_id: a UUID foreign key that references the user table
        - termsofuse_id: a UUID foreign key that references the termsofuse
                            table.
        - signed: a datetime field that represents the date and time when the
                    user signed the terms of use
        """

        class FakeSignedTermsOfUseEntity(fake_sql_tables):
            __tablename__ = "user_termsofuse"
            __table_args__ = (UniqueConstraint("user_id", "termsofuse_id"),)

            id: Mapped[UUID] = mapped_column(UUID_(as_uuid=True), primary_key=True)  # type: ignore
            user_id: Mapped[UUID] = mapped_column(  # type: ignore
                UUID_(as_uuid=True),
                ForeignKey("user.id", ondelete="CASCADE"),
                nullable=False,
            )

            termsofuse_id: Mapped[UUID] = mapped_column(  # type: ignore
                UUID_(as_uuid=True),
                ForeignKey("termsofuse.id", ondelete="CASCADE"),
                nullable=False,
            )

            signed: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # type: ignore

        self._table = FakeSignedTermsOfUseEntity

    def test_fields_number(self):
        """
        Tests if the number of fields in the SignedTermsOfUseEntity is correct.
        """
        assert len(SignedTermsOfUseEntity.__table__.columns) == 4

    @pytest.mark.parametrize(
        "field",
        ["id", "user_id", "termsofuse_id", "signed"],
    )
    def test_fields(self, field: str) -> None:
        """
        This test checks if the columns of the fake SignedTermsOfUseEntity
        table match the columns of the actual SignedTermsOfUseEntity table.
        """

        fake_table_field = self._table.__table__.columns[field]
        original_table_field = SignedTermsOfUseEntity.__table__.columns[field]

        assert repr(fake_table_field) == repr(original_table_field)

    def test_constrains(self) -> None:
        """
        Tests if the constrains in the SignedTermsOfUseEntity are correct.
        """
        fake_table_args = getattr(self._table, "__table_args__", "NA")
        original_table_args = getattr(SignedTermsOfUseEntity, "__table_args__", "NA")

        assert repr(fake_table_args) == repr(original_table_args)
