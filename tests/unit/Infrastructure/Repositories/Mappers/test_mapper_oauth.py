from unittest.mock import Mock
from uuid import UUID

import pytest

from src.Context.Domain import Oauth
from src.Infrastructure.Entities.Oauth import OAuthEntity
from src.Infrastructure.Repositories.Mappers.Oauth import EntityDomainMapperOauth


class TestEntityDomainMapperOauth:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        """
        Setup inversion control.
        """
        self._mapper = EntityDomainMapperOauth()

    @pytest.fixture(autouse=True)
    def _setup_data(self) -> None:
        self._record = Mock(
            spec=OAuthEntity,
            id=UUID("12345678123456781234567812345671"),
            user_id=UUID("12345678123456781234567812345672"),
            provider="google",
            provider_user_id="123456",
        )

        self._domain = Mock(
            spec=Oauth,
            id=UUID("12345678123456781234567812345671"),
            user_id=UUID("12345678123456781234567812345673"),
            provider="facebook",
            provider_user_id="1234",
        )

    def test_to_domain(self) -> None:
        """
        Test to_domain.
        """
        oauth = self._mapper.to_domain(self._record)

        assert oauth.id == UUID("12345678123456781234567812345671")
        assert oauth.user_id == UUID("12345678123456781234567812345672")
        assert oauth.provider == "google"
        assert oauth.provider_user_id == "123456"

    def test_to_entity(self) -> None:
        """
        Test to_entity.
        """
        record = self._mapper.to_entity(self._domain)

        assert record.id == UUID("12345678123456781234567812345671")
        assert record.user_id == UUID("12345678123456781234567812345673")
        assert record.provider == "facebook"
        assert record.provider_user_id == "1234"

    def test_map_to_record(self) -> None:
        """
        Test map domain to record.
        """
        self._mapper.map_to_entity(self._domain, self._record)

        assert self._record.id == UUID("12345678123456781234567812345671")
        assert self._record.user_id == UUID("12345678123456781234567812345673")
        assert self._record.provider == "facebook"
        assert self._record.provider_user_id == "1234"
