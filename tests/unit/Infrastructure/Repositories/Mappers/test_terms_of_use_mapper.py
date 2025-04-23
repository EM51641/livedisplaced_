from datetime import datetime
from uuid import UUID

import pytest

from src.Context.Domain.TermsOfUse import SignedTermsOfUse, TermsOfUse
from src.Infrastructure.Entities.TermsOfUse import (
    SignedTermsOfUseEntity,
    TermsOfUseEntity,
)
from src.Infrastructure.Repositories.Mappers.TermsOfUse import (
    EntityDomainMapperSignedTermsOfUse,
    EntityDomainMapperTermsOfUse,
)


class TestEntityDomainMapperTermsOfUse:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self._record = TermsOfUseEntity(
            id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd"),
            created=datetime(2021, 1, 1),
        )

        self._user = TermsOfUse(
            id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd"),
            created=datetime(2021, 1, 1),
        )

        self._mapper = EntityDomainMapperTermsOfUse()

    def test_to_domain(self) -> None:
        """
        Test to_domain method succesfully.
        """
        user = self._mapper.to_domain(self._record)

        assert user.id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert user.created == datetime(2021, 1, 1)

    def test_to_entity(self) -> None:
        """
        Test to_entity method succesfully.
        """
        user = self._mapper.to_entity(self._user)

        assert user.id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert user.created == datetime(2021, 1, 1)

    def test_map_to_record(self) -> None:
        """
        Test map_to_record method succesfully.
        """
        self._mapper.map_to_entity(self._user, self._record)

        assert self._record.id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert self._record.created == datetime(2021, 1, 1)


class TestEntityDomainMapperSignedTermsOfUse:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self._record = SignedTermsOfUseEntity(
            id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd"),
            user_id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd"),
            termsofuse_id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd"),
            signed=datetime(2021, 1, 1),
        )

        self._user = SignedTermsOfUse(
            id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd"),
            user_id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef861bd"),
            termsofuse_id=UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860ba"),
            signed=datetime(2021, 1, 1),
        )

        self._mapper = EntityDomainMapperSignedTermsOfUse()

    def test_to_domain(self) -> None:
        """
        Test to_domain method succesfully.
        """
        user = self._mapper.to_domain(self._record)

        assert user.id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert user.user_id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert user.termsofuse_id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert user.signed == datetime(2021, 1, 1)

    def test_to_entity(self) -> None:
        """
        Test to_entity method succesfully.
        """
        user = self._mapper.to_entity(self._user)

        assert user.id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert user.user_id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef861bd")
        assert user.termsofuse_id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860ba")
        assert user.signed == datetime(2021, 1, 1)

    def test_map_to_record(self) -> None:
        """
        Test map_to_record method succesfully.
        """
        self._mapper.map_to_entity(self._user, self._record)

        assert self._record.id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef860bd")
        assert self._record.user_id == UUID("a3b8d425-2b60-4ad7-becc-bedf2ef861bd")
        assert self._record.termsofuse_id == UUID(
            "a3b8d425-2b60-4ad7-becc-bedf2ef860ba"
        )
        assert self._record.signed == datetime(2021, 1, 1)
