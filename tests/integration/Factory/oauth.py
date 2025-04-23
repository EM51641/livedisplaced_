from uuid import UUID

from src.Infrastructure.Entities.Oauth import OAuthEntity
from tests.integration.Factory import BaseFactory


class OauthFactory(BaseFactory):
    """
    Factory class for creating OauthEntity objects.
    """

    async def create_oauth_account(
        self,
        user_id: UUID,
        id: UUID | None = None,
        provider: str | None = None,
        provider_user_id: str | None = None,
    ) -> OAuthEntity:
        """
        Create a new OauthEntity object with the given attributes.

        Args:
            user_id (UUID):
                The ID of the linked user account.
            id (UUID | None):
                The ID of the Oauth entity. If None, a random UUID will be generated.
            provider (str | None):
                The OAuth provider name. If None, a random provider name will be generated.
            provider_user_id (str | None):
                The unique identifier of the user by the provider. If None, a random user ID will be generated.

        Returns:
            OAuthEntity: The created OauthEntity object.
        """
        if id is None:
            id = UUID(self._faker.unique.uuid4())

        if provider is None:
            provider = self._faker.random_element(
                ["google", "facebook", "x", "instagram"]
            )

        if provider_user_id is None:
            provider_user_id = str(self._faker.uuid4())

        oauth = OAuthEntity(
            id=id,  # type: ignore
            user_id=user_id,  # type: ignore
            provider=provider,  # type: ignore
            provider_user_id=provider_user_id,  # type: ignore
        )
        self._session.add(oauth)
        await self._session.commit()
        return oauth
