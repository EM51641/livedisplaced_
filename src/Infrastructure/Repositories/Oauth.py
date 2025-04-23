"""
The Oauth Repository.
"""

from __future__ import annotations

from abc import abstractmethod

from sqlalchemy import Select

from src.Context.Domain.Oauth import Oauth
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities.Oauth import OAuthEntity
from src.Infrastructure.Repositories.Mappers.Oauth import EntityDomainMapperOauth
from src.Infrastructure.Repositories.Utils import RepositoryBase


class OauthRepositoryBase(RepositoryBase[OAuthEntity, Oauth]):
    """
    Abstract Oauth repo pattern
    """

    @abstractmethod
    async def find_by_provider_by_uid(
        self, provider: str, provider_user_id: str
    ) -> Oauth:
        """Not implemented yet"""


class OauthRepository(OauthRepositoryBase):
    """
    Oauth Repository Connector.

    Attributes:
    ----
        :param session_context: The session context.
        :param db: The database connection.
        :param entity_cls: The entity class.
        :param mapper: The mapper class.
    """

    def __init__(
        self,
        session: Session,
        db: DBSession,
        entity_cls: type[OAuthEntity] = OAuthEntity,
        mapper: EntityDomainMapperOauth = EntityDomainMapperOauth(),
    ) -> None:
        super().__init__(session, db, entity_cls, mapper)

    async def find_by_provider_by_uid(
        self, provider: str, provider_user_id: str
    ) -> Oauth:
        """
        Get an oauth by provider and provider user id.

        Parameters:
        ----
            :param provider: name of the oauth provider.
            :param provider_user_id:  id of the provider assigned to the user.

        Returns:
        ----
            Oauth
        """
        query = self._query_by_provider_and_by_uid_query(provider, provider_user_id)
        oauth = await self._find_first_domain(query)
        return oauth

    def _query_by_provider_and_by_uid_query(
        self, provider: str, provider_user_id: str
    ) -> Select[tuple[OAuthEntity]]:
        """
        Get an oauth by provider and provider user id.

        Parameters:
        ----
            :param provider: name of the oauth provider.
            :param provider_user_id:  id of the provider assigned to the user.

        Returns:
        ----
            Oauth
        """
        table = self._db.select(self._entity_type)
        query = table.where(
            self._entity_type.provider_user_id == provider_user_id,
            self._entity_type.provider == provider,  # type: ignore
        )
        return query
