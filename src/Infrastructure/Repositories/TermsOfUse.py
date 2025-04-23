"""
This module contains repository classes for managing terms of use information.

TermsOfUseRepository:
    This class stores the terms of use information.

BaseSignedTermsOfUseRepository:
    Abstract base class for managing signed terms of use information.

SignedTermsOfUseRepository:
    This class stores the signed terms of use information.
"""

from abc import abstractmethod
from uuid import UUID

from sqlalchemy import Select

from src.Context.Domain.TermsOfUse import SignedTermsOfUse, TermsOfUse
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities.TermsOfUse import (
    SignedTermsOfUseEntity,
    TermsOfUseEntity,
)
from src.Infrastructure.Repositories.Mappers.TermsOfUse import (
    EntityDomainMapperSignedTermsOfUse,
    EntityDomainMapperTermsOfUse,
)
from src.Infrastructure.Repositories.Utils import RepositoryBase


class TermsOfUseRepositoryBase(RepositoryBase[TermsOfUseEntity, TermsOfUse]):
    """
    Abstract Oauth repo pattern
    """

    @abstractmethod
    async def find_latest_version(self) -> TermsOfUse:
        """Not implemented yet"""


class TermsOfUseRepository(TermsOfUseRepositoryBase):
    """
    This class stores the terms of use information.

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
        entity_cls: type[TermsOfUseEntity] = TermsOfUseEntity,
        mapper: EntityDomainMapperTermsOfUse = EntityDomainMapperTermsOfUse(),
    ) -> None:
        super().__init__(session, db, entity_cls, mapper)

    async def find_latest_version(self) -> TermsOfUse:
        """
        Return the latest version of the terms of use.

        Params:
        ----
            None

        Returns:
        ----
            TermsOfUse: The latest version of the terms of use.
        """
        query = self._query_last_agreement()
        terms = await self._find_first_domain(query)
        return terms

    def _query_last_agreement(self) -> Select[tuple[TermsOfUseEntity]]:
        """
        get the query giving the last agreement.

        Returns:
        ----
           Query[TermsOfUseModel]
        """
        table = self._db.select(self._entity_type)
        query = table.order_by(self._entity_type.created.desc()).limit(1)
        return query


class BaseSignedTermsOfUseRepository(
    RepositoryBase[SignedTermsOfUseEntity, SignedTermsOfUse]
):
    """
    Abstract Oauth repo pattern
    """

    @abstractmethod
    async def find_latest_compliant_term_per_user(
        self, user_id: UUID
    ) -> SignedTermsOfUse:
        """Not implemented yet"""


class SignedTermsOfUseRepository(BaseSignedTermsOfUseRepository):
    """
    This class stores the terms of use information.

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
        entity_cls: type[SignedTermsOfUseEntity] = SignedTermsOfUseEntity,
        mapper: EntityDomainMapperSignedTermsOfUse = EntityDomainMapperSignedTermsOfUse(),
    ) -> None:
        super().__init__(session, db, entity_cls, mapper)

    async def find_latest_compliant_term_per_user(
        self, user_id: UUID
    ) -> SignedTermsOfUse:
        """
        Return the latest version of the terms of use.

        Params:
        ----
            user_id: The user id.

        Returns:
        ----
            SignedTermsOfUse:
                The latest terms of use signed of the terms of use.
        """
        query = self._query_latest_compliant_term_per_user(user_id)
        terms = await self._find_first_domain(query)
        return terms

    def _query_latest_compliant_term_per_user(
        self, user_id: UUID
    ) -> Select[tuple[SignedTermsOfUseEntity]]:
        """
        Get the query giving the last compliant agreement the user signed.

        Parameters:
        ----
            user_id: UUID

        Returns:
        ----
           Select[tuple[SignedTermsOfUseEntity]]
        """
        table = self._db.select(self._entity_type)
        query = (
            table.filter(self._entity_type.user_id == user_id)
            .order_by(self._entity_type.signed)
            .limit(1)
        )
        return query
