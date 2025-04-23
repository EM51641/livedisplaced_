from datetime import datetime
from uuid import UUID

from src.Infrastructure.Entities.User import UserEntity
from tests.integration.Factory import BaseFactory


class UserFactory(BaseFactory):
    """
    Factory class for creating UserEntity objects.
    """

    async def create_user(
        self,
        id: UUID | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        is_active: bool | None = None,
        created: datetime | None = None,
    ) -> UserEntity:
        """
        Create a new UserEntity object with the given attributes.

        Args:
            id (UUID | None): The ID of the user. If None, a random UUID will be generated.
            first_name (str | None): The first name of the user. If None, a random first name will be generated.
            last_name (str | None): The last name of the user. If None, a random last name will be generated.
            email (str | None): The email address of the user. If None, a random email address will be generated.
            password (str | None): The password of the user. If None, a random password will be generated.
            is_active (bool | None): The active status of the user. If None, a random boolean value will be generated.
            created (datetime | None):
                The creation date of the user. If None, a random datetime within the current decade will be generated.

        Returns:
            UserEntity: The created UserEntity object.
        """
        if id is None:
            id = UUID(self._faker.unique.uuid4())

        if first_name is None:
            first_name = self._faker.first_name()

        if last_name is None:
            last_name = self._faker.last_name()

        if email is None:
            email = self._faker.unique.email()

        if password is None:
            password = self._faker.password()

        if is_active is None:
            is_active = self._faker.boolean()

        if created is None:
            created = self._faker.date_time_this_decade()

        user = UserEntity(
            id=id,  # type: ignore
            first_name=first_name,  # type: ignore
            last_name=last_name,  # type: ignore
            email=email,
            password=password,
            is_active=is_active,  # type: ignore
            created=created,  # type: ignore
        )

        self._session.add(user)
        await self._session.commit()
        return user
