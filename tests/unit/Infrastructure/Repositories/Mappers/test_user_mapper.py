from datetime import datetime
from uuid import UUID

import pytest

from src.Context.Domain.User import User
from src.Infrastructure.Entities.User import UserEntity
from src.Infrastructure.Repositories.Mappers.User import EntityDomainMapperUser


class TestUserDomain:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self._record = UserEntity(
            id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd"),
            first_name="John",
            last_name="Doe",
            email=None,
            password=None,
            is_active=False,
            created=datetime(2021, 1, 1),
        )

        self._user = User(
            id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd"),
            first_name="John",
            last_name="Doe",
            email="johndoe@hotmail.com",
            password="hashed_password",
            is_active=True,
            created=datetime(2021, 1, 1),
        )

        self._mapper = EntityDomainMapperUser()

    def test_to_domain(self) -> None:
        """
        Test to_domain method succesfully.
        """
        user = self._mapper.to_domain(self._record)

        assert user.id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email is None
        assert user.password is None
        assert user.is_active is False
        assert user.created == datetime(2021, 1, 1)

    def test_to_entity(self) -> None:
        """
        Test to_entity method succesfully.
        """
        user = self._mapper.to_entity(self._user)

        assert user.id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "johndoe@hotmail.com"
        assert user.password == "hashed_password"
        assert user.is_active is True
        assert user.created == datetime(2021, 1, 1)

    def test_map_to_record(self) -> None:
        """
        Test map_to_record method succesfully.
        """
        self._mapper.map_to_entity(self._user, self._record)

        assert self._record.id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert self._record.first_name == "John"
        assert self._record.last_name == "Doe"
        assert self._record.email == "johndoe@hotmail.com"
        assert self._record.password == "hashed_password"
        assert self._record.is_active is True
        assert self._record.created == datetime(2021, 1, 1)
