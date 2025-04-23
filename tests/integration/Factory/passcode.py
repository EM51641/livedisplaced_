from datetime import datetime
from uuid import UUID

from src.Infrastructure.Entities.Passcode import CredChoices, PasscodeEntity
from tests.integration.Factory import BaseFactory


class PasscodeFactory(BaseFactory):
    """
    Factory class for creating PasscodeEntity objects.
    """

    async def create_passcode(
        self,
        user_id: UUID,
        id: UUID | None = None,
        category: CredChoices | None = None,
        expiration: datetime | None = None,
    ) -> PasscodeEntity:
        """
        Create a new UserEntity object with the given attributes.

        Args:
            user_id (UUID):
                The ID of the user. If None, a random UUID will be generated.
            id (UUID | None):
                The ID of the user. If None, a random UUID will be generated.
            category (CredChoices | None):
                The category of the passcode. If None, a random category will be generated.
            expiration (datetime | None):
                The expiration date of the passcode. If None, a random datetime will be generated.

        Returns:
            PasscodeEntity: The created PasscodeEntity object.
        """
        if id is None:
            id = UUID(self._faker.unique.uuid4())

        if category is None:
            category = self._faker.random_element(CredChoices)

        if expiration is None:
            expiration = self._faker.date_time_this_decade()

        passcode = PasscodeEntity(
            id=id,  # type: ignore
            user_id=user_id,  # type: ignore
            category=category,  # type: ignore
            expiration=expiration,  # type: ignore
        )
        self._session.add(passcode)
        await self._session.commit()
        return passcode
