"""
This module contains unit tests for the Passcode domain class.

The Passcode domain class is responsible for representing a passcode
entity in the system. It contains attributes such as id, user_id, category,
and expiration.

This module contains test cases for the initialization of a Passcode instance,
conversion of a Passcode instance to a dictionary, and the string and
representation representation of a Passcode instance.
"""

from datetime import datetime
from uuid import UUID

import pytest

from src.Context.Domain.Passcode import Passcode


class TestDomainPasscode:
    """
    A test suite for the Passcode domain class.
    """

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """
        Setup the test on the Passcode instance.
        """
        self._passcode = Passcode(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            user_id=UUID("00000000-0000-0000-0000-000000000001"),
            category="Activ",
            expiration=datetime(2020, 1, 1),
        )

    def test_passcode_init(self) -> None:
        """
        Test the initialization of the Passcode instance.

        Asserts:
            The id, user_id, category, and expiration of the Passcode instance.
        """

        assert self._passcode.id == UUID("00000000-0000-0000-0000-000000000000")
        assert self._passcode.user_id == UUID("00000000-0000-0000-0000-000000000001")
        assert self._passcode.category == "Activ"
        assert self._passcode.expiration == datetime(2020, 1, 1)

    def test_passcode_to_dict(self) -> None:
        """
        Test the conversion of the Passcode instance to a dictionary.

        Asserts:
            The dictionary representation of the Passcode instance.
        """

        assert self._passcode.to_dict() == {
            "id": UUID("00000000-0000-0000-0000-000000000000"),
            "user_id": UUID("00000000-0000-0000-0000-000000000001"),
            "category": "Activ",
            "expiration": datetime(2020, 1, 1),
        }

    def test_passcode_str(self) -> None:
        """
        Test the string representation of the Passcode instance.

        Asserts:
            The string representation of the Passcode instance.
        """
        assert str(self._passcode) == (
            "Passcode(id=00000000-0000-0000-0000-000000000000, "
            "user_id=00000000-0000-0000-0000-000000000001, "
            "category=Activ, expiration=2020-01-01 00:00:00)"
        )

    def test_passcode_repr(self) -> None:
        """
        Test the representation of the Passcode instance.

        Asserts:
            The representation of the Passcode instance.
        """
        assert repr(self._passcode) == (
            "Passcode(id=UUID('00000000-0000-0000-0000-000000000000'), "
            "user_id=UUID('00000000-0000-0000-0000-000000000001'), "
            "category='Activ', expiration=datetime.datetime(2020, 1, 1, 0, 0))"
        )
