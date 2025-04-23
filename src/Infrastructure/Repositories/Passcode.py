"""
Passcode Repository Connector
"""

from __future__ import annotations

from abc import abstractmethod
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Select

from src.Context.Domain.Passcode import Passcode
from src.Context.Domain.User import User
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities.Passcode import CredChoices, PasscodeEntity
from src.Infrastructure.Repositories.Mappers.Passcode import EntityDomainMapperPasscode
from src.Infrastructure.Repositories.Utils import RepositoryBase


class BasePasscodeRepository(RepositoryBase[PasscodeEntity, Passcode]):
    """
    Abstract Passcode repo pattern
    """

    @abstractmethod
    async def find_activation_by_uid_before_exp(self, uid: UUID) -> Passcode:
        """Not implemented yet"""

    @abstractmethod
    async def find_reset_by_uid_before_exp(self, uid: UUID) -> Passcode:
        """Not implemented yet"""

    @abstractmethod
    async def find_activation_by_user(self, user: User) -> Passcode:
        """Not implemented yet"""

    @abstractmethod
    async def find_reset_by_user(self, user: User) -> Passcode:
        """Not implemented yet"""


class PasscodeRepository(BasePasscodeRepository):
    """
    Passcode Repository Connector.
    """

    def __init__(
        self,
        session: Session,
        db: DBSession,
        entity_cls: type[PasscodeEntity] = PasscodeEntity,
        mapper: EntityDomainMapperPasscode = EntityDomainMapperPasscode(),
    ) -> None:
        """
        Initializes a new instance of the Repository class.

        Args:
            session (Session):
                The session object used for database operations.
            db (Database):
                The database object used for database operations.
            entity_cls (type[PasscodeEntity], optional):
                The class representing the passcode entity.
                Defaults to PasscodeEntity.
            mapper (type[EntityDomainMapperPasscode], optional):
                The mapper class used for mapping between entity and
                domain models. Defaults to EntityDomainMapperPasscode.
        """
        super().__init__(
            entity_type=entity_cls, session=session, db=db, entity_domain_mapper=mapper
        )

    async def find_activation_by_user(self, user: User) -> Passcode:
        """
        Get activation passcode by user.

        Parameters:
            user (User): The user domain.

        Returns:
            Passcode: The activation passcode.
        """
        query = self._query_by_user_id_by_category(user, CredChoices.ACTIVATION)
        passcode = await self._find_first_domain(query)
        return passcode

    async def find_reset_by_user(self, user: User) -> Passcode:
        """
        Get reset passcode by user.

        Parameters:
            user (User): The user domain.

        Returns:
            Passcode: The reset passcode.
        """
        query = self._query_by_user_id_by_category(user, CredChoices.RESET)
        passcode = await self._find_first_domain(query)
        return passcode

    async def find_activation_by_uid_before_exp(self, uid: UUID) -> Passcode:
        """
        Find activation passcode by uid.

        Parameters:
            uid (UUID): The uid of the passcode.

        Returns:
            Passcode: The activation passcode.
        """
        query = self._query_by_uid_by_category_before_exp(uid, CredChoices.ACTIVATION)
        passcode = await self._find_first_domain(query)
        return passcode

    async def find_reset_by_uid_before_exp(self, uid: UUID) -> Passcode:
        """
        Find reset passcode by uid.

        Parameters:
            uid (UUID): The uid of the passcode.

        Returns:
            Passcode: The reset passcode.
        """
        query = self._query_by_uid_by_category_before_exp(uid, CredChoices.RESET)
        passcode = await self._find_first_domain(query)
        return passcode

    def _query_by_user_id_by_category(
        self, user: User, category: CredChoices
    ) -> Select[tuple[PasscodeEntity]]:
        """
        Get query for passcode reset by user id.

        Parameters:
            user (User): The user domain.
            category (CredChoices): The category of the passcode.

        Returns:
            Select[tuple[PasscodeEntity]]: The query for passcode reset by user id.
        """
        query = self._db.select(PasscodeEntity).where(
            PasscodeEntity.user_id == user.id,
            PasscodeEntity.category == category.name,
        )
        return query

    def _query_by_uid_by_category_before_exp(
        self, uid: UUID, category: CredChoices
    ) -> Select[tuple[PasscodeEntity]]:
        """
        Get passcode by uid.

        Parameters:
            uid (UUID): The uid of the passcode.
            category (CredChoices): The category of the passcode.

        Returns:
            Select[tuple[PasscodeEntity]]: The query for passcode by uid.
        """
        current_time = datetime.now(UTC)

        query = self._db.select(PasscodeEntity).where(
            PasscodeEntity.id == uid,
            PasscodeEntity.category == category.name,
            PasscodeEntity.expiration > current_time,
        )

        return query
