"""
This module contains integration tests for the OAuthEntity class.

The tests ensure that the OAuthEntity table has the correct number of columns
and that each column matches the expected column in the test table.
"""

from uuid import UUID

import pytest
from sqlalchemy import UUID as UUID_
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Entities.Oauth import OAuthEntity


class TestOAuthEntityEntityConfig:
    @pytest.fixture(autouse=True)
    def _fake_table(self, fake_sql_tables) -> None:
        """Create a fake OAuth entity table for testing purposes."""

        class FakeOAuthEntityEntity(fake_sql_tables):
            """
            A fake OAuth entity class for testing purposes.

            Attributes:
                id (Mapped[UUID]):
                    A mapped UUID column representing the entity ID.
                user_id (Mapped[UUID]):
                    A mapped UUID column representing the user ID.
                provider (Mapped[str]):
                    A mapped string column representing the provider.
                provider_user_id (Mapped[str]):
                    A mapped string column representing the provider user ID.
            """

            __tablename__ = "oauth"

            id: Mapped[UUID] = mapped_column(UUID_(as_uuid=True), primary_key=True)

            user_id: Mapped[UUID] = mapped_column(
                UUID_(as_uuid=True),
                ForeignKey("user.id", ondelete="CASCADE"),
                unique=True,
                nullable=False,
            )

            provider: Mapped[str] = mapped_column(String(50), nullable=False)

            provider_user_id: Mapped[str] = mapped_column(String, nullable=False)

        self._table = FakeOAuthEntityEntity

    def test_fields_number(self):
        """
        Tests if the number of fields in the OAuthEntity is correct.
        """
        assert len(OAuthEntity.__table__.columns) == 4

    @pytest.mark.parametrize(
        "field",
        ["id", "user_id", "provider", "provider_user_id"],
    )
    def test_fields(self, field: str) -> None:
        """
        This test checks if the columns of the fake OAuthEntity table
        match the columns of the actual OAuthEntity table.
        """

        fake_table_field = self._table.__table__.columns[field]
        original_table_field = OAuthEntity.__table__.columns[field]

        assert repr(fake_table_field) == repr(original_table_field)

    def test_constrains(self) -> None:
        """
        Tests if the constrains in the OAuthEntity are correct.
        """
        fake_table_args = getattr(self._table, "__table_args__", "NA")
        original_table_args = getattr(OAuthEntity, "__table_args__", "NA")

        assert repr(fake_table_args) == repr(original_table_args)
