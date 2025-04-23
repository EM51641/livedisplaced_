from datetime import datetime
from uuid import UUID

from src.Infrastructure.Entities.TermsOfUse import (
    SignedTermsOfUseEntity,
    TermsOfUseEntity,
)
from tests.integration.Factory import BaseFactory


class TermsOfUseFactory(BaseFactory):
    """
    Factory class for creating TermsOfUseEntity objects.
    """

    async def create_terms_of_use(
        self, id: UUID | None = None, creation_date: datetime | None = None
    ) -> TermsOfUseEntity:
        """
        Create a new TermsOfUseEntity object with the given attributes.

        Args:
            user_id (UUID):
                The ID of the user. If None, a random UUID will be generated.
            id (UUID | None):
                The ID of the user. If None, a random UUID will be generated.
            category (CredChoices | None):
                The category of the terms of use. If None, a random category will be generated.
            expiration (datetime | None):
                The expiration date of the terms of use. If None, a random datetime will be generated.

        Returns:
            TermsOfUseEntity: The created TermsOfUseEntity object.
        """
        if id is None:
            id = UUID(self._faker.unique.uuid4())

        if creation_date is None:
            creation_date = self._faker.date_time_this_decade()

        termsofuse = TermsOfUseEntity(id=id, created=creation_date)  # type: ignore
        self._session.add(termsofuse)
        await self._session.commit()
        return termsofuse


class SignedTermsOfUseFactory(BaseFactory):
    """
    Factory class for creating SignedTermsOfUseEntity objects.
    """

    async def create_signed_terms_of_use(
        self,
        user_id: UUID,
        termsofuse_id: UUID,
        id: UUID | None = None,
        signed_date: datetime | None = None,
    ) -> SignedTermsOfUseEntity:
        """
        Create a new SignedTermsOfUseEntity object with the given attributes.

        Args:
            user_id (UUID):
                The ID of the user. If None, a random UUID will be generated.
            id (UUID | None):
                The ID of the user. If None, a random UUID will be generated.
            terms_of_use_id (UUID):
                The ID of the terms of use. If None, a random UUID will be generated.
            signed_date (datetime | None):
                The signed date of the terms of use. If None, a random datetime will be generated.

        Returns:
            SignedTermsOfUseEntity: The created SignedTermsOfUseEntity object.
        """
        if id is None:
            id = UUID(self._faker.unique.uuid4())

        if signed_date is None:
            signed_date = self._faker.date_time_this_decade()

        signed_terms_of_use = SignedTermsOfUseEntity(
            id=id, user_id=user_id, termsofuse_id=termsofuse_id, signed=signed_date  # type: ignore
        )

        self._session.add(signed_terms_of_use)
        await self._session.commit()

        return signed_terms_of_use
