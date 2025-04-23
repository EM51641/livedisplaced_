from src.Context.Domain.User import User
from src.Infrastructure.Entities.User import UserEntity
from src.Infrastructure.Repositories.Mappers import EntityDomainMapper


class EntityDomainMapperUser(EntityDomainMapper[UserEntity, User]):
    """
    Repository Pattern.
    """

    def to_domain(self, entity: UserEntity) -> User:
        """
        Convert the entity to a domain.

        Params:
        ----
            entity: The entity to convert.

        Returns:
        ----
            User: The converted domain.
        """
        return User(
            id=entity.id,
            email=entity.email,
            password=entity.password,
            first_name=entity.first_name,
            last_name=entity.last_name,
            is_active=entity.is_active,
            created=entity.created,
        )

    def to_entity(self, domain: User) -> UserEntity:
        """
        Convert the domain to an entity.

        Params:
        ----
            domain: The domain to convert.

        Returns:
        ----
            UserEntity: The converted entity.
        """
        entity = UserEntity(
            id=domain.id,
            first_name=domain.first_name,
            last_name=domain.last_name,
            password=domain.password,
            email=domain.email,
            is_active=domain.is_active,
            created=domain.created,
        )
        return entity

    def map_to_entity(self, domain: User, entity: UserEntity) -> None:
        """
        Map User domain to its entity.

        Params:
        ----
            domain: The domain to convert.
            entity: The entity to map the domain on.
        """
        entity.id = domain.id
        entity.first_name = domain.first_name
        entity.last_name = domain.last_name
        entity.is_active = domain.is_active
        entity.password = domain.password
        entity.created = domain.created
        entity.email = domain.email
