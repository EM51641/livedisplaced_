from datetime import datetime
from unittest.mock import Mock, patch
from uuid import UUID

import pytest

from src.Context.Domain.User import User


class TestUserDomain:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self._user = User(
            id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd"),
            first_name="John",
            last_name="Doe",
            email=None,
            password=None,
            is_active=False,
            created=datetime(2021, 1, 1),
        )

    def test_constructor(self) -> None:
        assert self._user.id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert self._user.first_name == "John"
        assert self._user.last_name == "Doe"
        assert self._user.email is None
        assert self._user.password is None
        assert self._user.is_active is False
        assert self._user.created == datetime(2021, 1, 1)

    def test_set_active(self) -> None:
        self._user.set_active()
        assert self._user.is_active is True

    def test_set_email(self) -> None:
        self._user.set_email("johndoe@hotmail.com")
        assert self._user.email == "johndoe@hotmail.com"

    @patch("src.Context.Domain.User.generate_password_hash")
    def test_set_password(self, mock: Mock) -> None:
        self._user.set_password("password")
        assert self._user.password is not None

    @patch("src.Context.Domain.User.check_password_hash", return_value=True)
    def test_check_password(self, mock: Mock) -> None:
        self._user.set_password("password")
        assert self._user.check_password("password") is True

    @patch("src.Context.Domain.User.check_password_hash")
    def test_check_password_none(self, mock: Mock) -> None:
        assert self._user.check_password("password") is False

    def test_to_dict(self) -> None:
        assert self._user.to_dict() == {
            "id": UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd"),
            "first_name": "John",
            "last_name": "Doe",
            "email": None,
            "password": None,
            "is_active": False,
            "created": datetime(2021, 1, 1),
        }

    def test_str(self) -> None:
        assert (
            str(self._user)
            == "User(id=a3b8d425-2b60-4ad7-becc-bedf2ef860bd, email=None, first_name=John, last_name=Doe, created=2021-01-01 00:00:00, is_active=False)"  # noqa: E501
        )

    def test_repr(self) -> None:
        assert (
            repr(self._user)
            == "User(id=UUID('a3b8d425-2b60-4ad7-becc-bedf2ef860bd'), email=None, first_name='John', last_name='Doe', created=datetime.datetime(2021, 1, 1, 0, 0), is_active=False)"  # noqa: E501
        )
