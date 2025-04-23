"""
This module contains unit tests for the Passcode Mapper module. It tests the
EntityDomainMapperPasscode class which is responsible for mapping between the
PasscodeEntity and Passcode classes.
"""

from datetime import datetime
from unittest.mock import Mock
from uuid import UUID

import pytest

from src.Context.Domain import Passcode
from src.Infrastructure.Entities.Passcode import CredChoices, PasscodeEntity
from src.Infrastructure.Repositories.Mappers.Passcode import EntityDomainMapperPasscode


class TestEntityDomainMapperPasscode:
    """
    This class contains unit tests for the EntityDomainMapperPasscode class.
    """

    @pytest.fixture(autouse=True)
    def _setup_mocks(self) -> None:
        """
        Setup mocks for test methods.
        """
        self._record = Mock(
            spec=PasscodeEntity,
            id=UUID("12345678123456781234567812345671"),
            user_id=UUID("12345678123456781234567812345672"),
            category=CredChoices("ACTIVATION"),
            expiration=datetime(2020, 1, 1),
        )

        self._passcode = Mock(
            spec=Passcode,
            id=UUID("12345678123456781234567812345671"),
            user_id=UUID("12345678123456781234567812345677"),
            category="RESET",
            expiration=datetime(2021, 1, 1),
        )

        self._mapper = EntityDomainMapperPasscode()

    def test_to_domain(self) -> None:
        """
        Test the to_domain method of the EntityDomainMapperPasscode class.
        """
        passcode = self._mapper.to_domain(self._record)

        assert passcode.id == UUID("12345678123456781234567812345671")
        assert passcode.user_id == UUID("12345678123456781234567812345672")
        assert passcode.category == "ACTIVATION"
        assert passcode.expiration == datetime(2020, 1, 1)

    def test_to_entity(self) -> None:
        """
        Test the to_entity method of the EntityDomainMapperPasscode class.
        """
        record = self._mapper.to_entity(self._passcode)

        assert record.id == UUID("12345678123456781234567812345671")
        assert record.user_id == UUID("12345678123456781234567812345677")
        assert record.category == CredChoices("RESET")
        assert record.expiration == datetime(2021, 1, 1)

    def test_map_to_record(self) -> None:
        """
        Test the map_to_record method of the EntityDomainMapperPasscode class.
        """
        self._mapper.map_to_entity(self._passcode, self._record)

        assert self._record.user_id == UUID("12345678123456781234567812345677")
        assert self._record.category == CredChoices("RESET")
        assert self._record.expiration == datetime(2021, 1, 1)
