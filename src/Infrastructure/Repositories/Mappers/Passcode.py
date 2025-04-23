"""
This module contains the EntityDomainMapperPasscode class, which is
responsible for mapping PasscodeEntity objects to Passcode objects
and vice versa. It implements the Repository Pattern.
"""

from src.Context.Domain.Passcode import Passcode
from src.Infrastructure.Entities.Passcode import CredChoices, PasscodeEntity
from src.Infrastructure.Repositories.Mappers import EntityDomainMapper


class EntityDomainMapperPasscode(EntityDomainMapper[PasscodeEntity, Passcode]):
    """
    This class is responsible for mapping PasscodeEntity objects to Passcode
    objects and vice versa. It implements the Repository Pattern.
    """

    def to_domain(self, entity: PasscodeEntity) -> Passcode:
        """
        Convert a PasscodeEntity object to a Passcode object.

        Parameters:
        ----
            :param entity: PasscodeEntity.
                    The PasscodeEntity object to convert.

        Returns:
        ----
            Passcode. The converted Passcode object.
        """

        passcode = Passcode(
            id=entity.id,
            user_id=entity.user_id,
            category=entity.category.name,  # type: ignore
            expiration=entity.expiration,
        )

        return passcode

    def to_entity(self, domain: Passcode) -> PasscodeEntity:
        """
        Create a new PasscodeEntity object.

        Parameters:
        ----
            :param passcode: Passcode.
                The Passcode object to create the PasscodeEntity from.

        Returns:
        ----
            PasscodeEntity. The new PasscodeEntity object.
        """
        entity = PasscodeEntity(
            id=domain.id,
            user_id=domain.user_id,
            category=CredChoices(domain.category),
            expiration=domain.expiration,
        )

        return entity

    def map_to_entity(self, domain: Passcode, entity: PasscodeEntity) -> None:
        """
        Map the Passcode object to the PasscodeEntity object.

        Parameters:
        ----
            :param passcode: Passcode. The Passcode object to map.
            :param entity: PasscodeEntity. The PasscodeEntity object to map to.
        """
        entity.id = domain.id
        entity.user_id = domain.user_id
        entity.category = CredChoices(domain.category)
        entity.expiration = domain.expiration
