from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import UUID as UUID_
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Entities.User import UserEntity


class TestUserEntityConfig:
    """
    This class contains tests for the UserEntity class.

    The tests ensure that the UserEntity class has the correct fields and that
    they match the expected fields.
    """

    @pytest.fixture(autouse=True)
    def _fake_table(self, fake_sql_tables):
        """Create a fake user entity table for testing purposes."""

        class FakeUserEntity(fake_sql_tables):
            __tablename__ = "user"

            id: Mapped[UUID] = mapped_column(UUID_(as_uuid=True), primary_key=True)  # type: ignore

            first_name: Mapped[str] = mapped_column(String(50), nullable=False)  # type: ignore
            last_name: Mapped[str] = mapped_column(String(50), nullable=False)  # type: ignore
            email: Mapped[str | None] = mapped_column(  # type: ignore
                String(120), unique=True, nullable=True
            )
            password: Mapped[str | None] = mapped_column(String(300), nullable=True)  # type: ignore
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)  # type: ignore
            created: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # type: ignore

        self._table = FakeUserEntity

    def test_fields_number(self):
        """
        Tests if the number of fields in the UserEntity is correct.
        """
        assert len(UserEntity.__table__.columns) == 7

    @pytest.mark.parametrize(
        "field",
        [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "is_active",
            "created",
        ],
    )
    def test_fields(self, field: str) -> None:
        """
        This test checks if the columns of the fake UserEntity
        table match the columns of the actual UserEntity table.
        """

        fake_table_field = self._table.__table__.columns[field]
        original_table_field = UserEntity.__table__.columns[field]

        assert repr(fake_table_field) == repr(original_table_field)

    def test_constrains(self) -> None:
        """
        Tests if the constrains in the UserEntity are correct.
        """
        fake_table_args = getattr(self._table, "__table_args__", "NA")
        original_table_args = getattr(UserEntity, "__table_args__", "NA")

        assert repr(fake_table_args) == repr(original_table_args)
