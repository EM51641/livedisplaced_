"""
This module contains the PasscodeUnitOfWork class, which is a unit
of work class for the Passcode module that provides access to repositories.
"""

from __future__ import annotations

from src.Context.Service.UnitOfWork import UnitOfWork
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Repositories.Passcode import PasscodeRepository
from src.Infrastructure.Repositories.TermsOfUse import (
    SignedTermsOfUseRepository,
    TermsOfUseRepository,
)
from src.Infrastructure.Repositories.User import UserRepository


class PasscodeUnitOfWork(UnitOfWork):
    """
    A unit of work class for Passcode module that provides access
    to repositories.

    Attributes:
        _passcode_repository (PasscodeRepository): An instance of
        PasscodeRepository.
        _user_repository (UserRepository): An instance of UserRepository.
    """

    def __init__(self, session: Session | None = None, db_con: DBSession | None = None):
        """
        Initializes a new instance of PasscodeUnitOfWork.

        Args:
            session (Session): The session object.
            db_con (Database, optional): The database object. Defaults to db.
        """
        super().__init__(session, db_con)
        self._passcode_repository = PasscodeRepository(self._session, self._db)
        self._user_repository = UserRepository(self._session, self._db)
        self._user_terms_of_use_repository = SignedTermsOfUseRepository(
            self._session, self._db
        )
        self._terms_of_use_repository = TermsOfUseRepository(self._session, self._db)

    @property
    def passcode_repository(self) -> PasscodeRepository:
        """
        Returns an instance of PasscodeRepository.
        """
        return self._passcode_repository

    @property
    def user_repository(self) -> UserRepository:
        """
        Returns an instance of UserRepository.
        """
        return self._user_repository

    @property
    def signed_terms_of_use_repository(self) -> SignedTermsOfUseRepository:
        """
        Returns an instance of SignedTermsOfUseRepository.
        """
        return self._user_terms_of_use_repository

    @property
    def terms_of_use_repository(self) -> TermsOfUseRepository:
        """
        Returns an instance of TermsOfUseRepository.
        """
        return self._terms_of_use_repository
