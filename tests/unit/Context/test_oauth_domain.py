"""
Test Oauth Business Model
"""

from uuid import UUID

import pytest

from src.Context.Domain.Oauth import Oauth


class TestDomainOauth:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """
        Setup the test on the Oauth instance.
        """
        self._oauth = Oauth(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            user_id=UUID("00000000-0000-0000-0000-000000000001"),
            provider="google",
            provider_user_id="123456",
        )

    def test_oauth_init(self) -> None:
        """
        Test the Oauth instance initialization.
        """

        assert self._oauth.id == UUID("00000000-0000-0000-0000-000000000000")
        assert self._oauth.user_id == UUID("00000000-0000-0000-0000-000000000001")
        assert self._oauth.provider == "google"
        assert self._oauth.provider_user_id == "123456"

    def test_oauth_to_dict(self) -> None:
        """
        Test the Oauth instance to dict.
        """

        assert self._oauth.to_dict() == {
            "id": UUID("00000000-0000-0000-0000-000000000000"),
            "user_id": UUID("00000000-0000-0000-0000-000000000001"),
            "provider": "google",
            "provider_user_id": "123456",
        }

    def test_oauth_str(self) -> None:
        """
        Test the Oauth instance str.
        """
        assert str(self._oauth) == (
            "Oauth(id=00000000-0000-0000-0000-000000000000, "
            "user_id=00000000-0000-0000-0000-000000000001, "
            "provider=google, provider_user_id=123456)"
        )  # noqa

    def test_oauth_repr(self) -> None:
        """
        Test the Oauth instance repr.
        """
        assert repr(self._oauth) == (
            "Oauth(id=UUID('00000000-0000-0000-0000-000000000000'), "
            "user_id=UUID('00000000-0000-0000-0000-000000000001'), "
            "provider='google', provider_user_id='123456')"
        )  # noqa
