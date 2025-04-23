"""
This module contains the EntityDomainMapperOauth class, which is responsible for mapping between
OAuthEntity and Oauth domain objects.
"""

from src.Context.Domain.Oauth import Oauth
from src.Infrastructure.Entities.Oauth import OAuthEntity
from src.Infrastructure.Repositories.Mappers import EntityDomainMapper


class EntityDomainMapperOauth(EntityDomainMapper[OAuthEntity, Oauth]):
    """
    Repository Pattern.

    This class is responsible for mapping between OAuthEntity and Oauth domain objects.
    """

    def to_domain(self, entity: OAuthEntity) -> Oauth:
        """
        Convert an OAuthEntity to an Oauth domain object.

        Parameters:
        ----
        entity (OAuthEntity): The OAuthEntity object to be converted.

        Returns:
        ----
        Oauth: The converted Oauth domain object.
        """

        domain = Oauth(
            id=entity.id,
            user_id=entity.user_id,
            provider=entity.provider,
            provider_user_id=entity.provider_user_id,
        )

        return domain

    def to_entity(self, domain: Oauth) -> OAuthEntity:
        """
        Convert the domain object to an OAuthEntity.

        Parameters:
        ----------
        domain : Oauth
            The domain object to convert.

        Returns:
        -------
        OAuthEntity
            The converted OAuthEntity object.
        """
        entity = OAuthEntity(
            id=domain.id,
            user_id=domain.user_id,
            provider=domain.provider,
            provider_user_id=domain.provider_user_id,
        )

        return entity

    def map_to_entity(self, domain: Oauth, entity: OAuthEntity) -> None:
        """
        Map the entity domain.

        Parameters:
        ----
        :param domain: Oauth. The domain object to be mapped.
        :param entity: OAuthEntity. The entity object to be mapped to.

        Returns:
        ----
        None. This function does not return any value.

        Raises:
        ----
        AssertionError: If the ID of the domain object does not match the ID of the entity object.

        """
        entity.id = domain.id
        entity.user_id = domain.user_id
        entity.provider = domain.provider
        entity.provider_user_id = domain.provider_user_id
