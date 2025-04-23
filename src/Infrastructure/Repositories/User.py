"""
The User class.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from src.Context.Domain.User import User
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Entities.User import UserEntity
from src.Infrastructure.Repositories.Mappers.User import EntityDomainMapperUser
from src.Infrastructure.Repositories.Utils import RepositoryBase

if TYPE_CHECKING:
    from sqlalchemy import Select

    from src.Infrastructure.Database import DBSession


class UserRepositoryBase(RepositoryBase[UserEntity, User]):
    @abstractmethod
    async def find_by_email(self, email: str) -> User:
        """Not implemented yet"""


class UserRepository(UserRepositoryBase):
    """
    User Repository
    """

    def __init__(
        self,
        session: Session,
        db: DBSession,
        entity_cls: type[UserEntity] = UserEntity,
        mapper: EntityDomainMapperUser = EntityDomainMapperUser(),
    ) -> None:
        super().__init__(
            entity_type=entity_cls, session=session, db=db, entity_domain_mapper=mapper
        )

    async def find_by_email(self, email: str) -> User:
        """
        Get user given an email.

        Parameters:
        ----
            :param email: email.

        Returns:
        ----
            User
        """
        query = self._query_by_email(email)
        user = await self._find_first_domain(query)
        return user

    def _query_by_email(self, email: str) -> Select[tuple[UserEntity]]:
        """
        Get a query giving an email.

        Parameters:
        ----
            email: str

        Returns:
        ----
            Query[UserEntity]
        """
        table = self._db.select(self._entity_type)
        query = table.where(self._entity_type.email == email)
        return query
