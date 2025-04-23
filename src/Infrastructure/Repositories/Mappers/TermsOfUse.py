"""
The TermsOfUse Repository.
"""

from src.Context.Domain.TermsOfUse import SignedTermsOfUse, TermsOfUse
from src.Infrastructure.Entities.TermsOfUse import (
    SignedTermsOfUseEntity,
    TermsOfUseEntity,
)
from src.Infrastructure.Repositories.Mappers import EntityDomainMapper


class EntityDomainMapperTermsOfUse(EntityDomainMapper[TermsOfUseEntity, TermsOfUse]):
    """
    Repository Pattern.
    """

    def to_domain(self, entity: TermsOfUseEntity) -> TermsOfUse:
        """
        Convert a TermsOfUse to a model.

        Parameters:
        ----
            :param TermsOfUse: TermsOfUse.

        Returns:
        ----
            TermsOfUseEntity
        """
        domain = TermsOfUse(
            id=entity.id,
            created=entity.created,
        )
        return domain

    def to_entity(self, domain: TermsOfUse) -> TermsOfUseEntity:
        """
        Convert the domain to an entity.

        Params:
        ----
            domain: The domain to convert.

        Returns:
        ----
            TermsOfUseEntity
        """
        entity = TermsOfUseEntity(
            id=domain.id,
            created=domain.created,
        )

        return entity

    def map_to_entity(self, domain: TermsOfUse, entity: TermsOfUseEntity) -> None:
        """
        Map the entity domain.

        Parameters:
        ----
            :param TermsOfUse: TermsOfUse.
            :param entity: TermsOfUseEntity

        Returns:
        ----
            None
        """
        entity.id = domain.id
        entity.created = domain.created


class EntityDomainMapperSignedTermsOfUse(
    EntityDomainMapper[SignedTermsOfUseEntity, SignedTermsOfUse]
):
    """
    Repository Pattern.
    """

    def to_domain(self, entity: SignedTermsOfUseEntity) -> SignedTermsOfUse:
        """
        Convert a domain to a model.

        Parameters:
        ----
            :param entity: SignedTermsOfUseEntity.

        Returns:
        ----
            SignedTermsOfUseEntity
        """
        signed_domain = SignedTermsOfUse(
            id=entity.id,
            user_id=entity.user_id,
            termsofuse_id=entity.termsofuse_id,
            signed=entity.signed,
        )
        return signed_domain

    def to_entity(self, domain: SignedTermsOfUse) -> SignedTermsOfUseEntity:
        """
        Convert the domain to an entity.

        Params:
        ----
            domain: The domain to convert.

        Returns:
        ----
            SignedTermsOfUseEntity
        """
        entity = SignedTermsOfUseEntity(
            id=domain.id,
            user_id=domain.user_id,
            termsofuse_id=domain.termsofuse_id,
            signed=domain.signed,
        )

        return entity

    def map_to_entity(
        self, domain: SignedTermsOfUse, entity: SignedTermsOfUseEntity
    ) -> None:
        """
        Map the entity domain.

        Parameters:
        ----
            :param signed_domain: SignedTermsOfUse.
            :param entity: SignedTermsOfUseEntity.

        Returns:
        ----
            None
        """
        entity.id = domain.id
        entity.user_id = domain.user_id
        entity.termsofuse_id = domain.termsofuse_id
        entity.signed = domain.signed
