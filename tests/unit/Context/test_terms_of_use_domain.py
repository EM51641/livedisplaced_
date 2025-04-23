"""
Test TermsOfUse Business Model
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pytest

from src.Context.Domain.TermsOfUse import SignedTermsOfUse, TermsOfUse


class TestTermsOfUseDomain:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """
        Setup the test on the TermsOfUse instance.
        """
        self._terms_of_use = TermsOfUse(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            created=datetime(2020, 1, 1),
        )

    def test_terms_of_use_init(self) -> None:
        """
        Test the TermsOfUse instance initialization.
        """

        assert self._terms_of_use.id == UUID("00000000-0000-0000-0000-000000000000")
        assert self._terms_of_use.created == datetime(2020, 1, 1)

    def test_terms_of_use_to_dict(self) -> None:
        """
        Test the TermsOfUse instance to dict.
        """

        assert self._terms_of_use.to_dict() == {
            "id": UUID("00000000-0000-0000-0000-000000000000"),
            "created": datetime(2020, 1, 1),
        }

    def test_terms_of_use_str(self) -> None:
        """
        Test the TermsOfUse instance str.
        """
        assert str(self._terms_of_use) == (
            "TermsOfUse(id=00000000-0000-0000-0000-000000000000, "
            "created=2020-01-01 00:00:00)"
        )  # noqa

    def test_terms_of_use_repr(self) -> None:
        """
        Test the TermsOfUse instance repr.
        """
        assert repr(self._terms_of_use) == (
            "TermsOfUse(id=UUID('00000000-0000-0000-0000-000000000000'), "
            "created=datetime.datetime(2020, 1, 1, 0, 0))"
        )  # noqa


class TestSignedTermsOfUseDomain:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """
        Setup the test on the TermsOfUse instance.
        """
        self._terms_of_use = SignedTermsOfUse(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            user_id=UUID("00000000-0000-0000-0000-000000000001"),
            termsofuse_id=UUID("00000000-0000-0000-0000-000000000002"),
            signed=datetime(2022, 1, 1),
        )

    def test_signed_terms_of_use_init(self) -> None:
        """
        Test the TermsOfUse instance initialization.
        """

        assert self._terms_of_use.id == UUID("00000000-0000-0000-0000-000000000000")
        assert self._terms_of_use.user_id == UUID(
            "00000000-0000-0000-0000-000000000001"
        )
        assert self._terms_of_use.termsofuse_id == UUID(
            "00000000-0000-0000-0000-000000000002"
        )
        assert self._terms_of_use.signed == datetime(2022, 1, 1)

    def test_signed_terms_of_use_to_dict(self) -> None:
        """
        Test the SignedTermsOfUse instance to dict.
        """

        assert self._terms_of_use.to_dict() == {
            "id": UUID("00000000-0000-0000-0000-000000000000"),
            "user_id": UUID("00000000-0000-0000-0000-000000000001"),
            "termsofuse_id": UUID("00000000-0000-0000-0000-000000000002"),
            "signed": datetime(2022, 1, 1),
        }

    def test_signed_terms_of_use_str(self) -> None:
        """
        Test the SignedTermsOfUse instance str.
        """
        assert str(self._terms_of_use) == (
            "SignedTermsOfUse(id=00000000-0000-0000-0000-000000000000, "
            "user_id=00000000-0000-0000-0000-000000000001, "
            "termsofuse_id=00000000-0000-0000-0000-000000000002, "
            "signed=2022-01-01 00:00:00)"
        )  # noqa

    def test_terms_of_use_repr(self) -> None:
        """
        Test the SignedTermsOfUse instance repr.
        """
        assert repr(self._terms_of_use) == (
            "SignedTermsOfUse(id=UUID('00000000-0000-0000-0000-000000000000'), "  # noqa
            "user_id=UUID('00000000-0000-0000-0000-000000000001'), "
            "termsofuse_id=UUID('00000000-0000-0000-0000-000000000002'), "
            "signed=datetime.datetime(2022, 1, 1, 0, 0))"  # noqa
        )
