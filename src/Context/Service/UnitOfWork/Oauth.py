from __future__ import annotations

from src.Context.Service.UnitOfWork import UnitOfWork
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Repositories.Oauth import OauthRepository
from src.Infrastructure.Repositories.TermsOfUse import (
    SignedTermsOfUseRepository,
    TermsOfUseRepository,
)
from src.Infrastructure.Repositories.User import UserRepository


class OAuthUnitOfWork(UnitOfWork):
    """
    A class representing a unit of work for the Oauth module.

    ...

    Attributes
    ----------
    _oauth_repository : OauthRepository
        The repository for Oauth-related data.

    Methods
    -------
    oauth_repository() -> OauthRepository:
        Returns the Oauth repository.
    """

    def __init__(
        self, session: Session | None = None, db_con: DBSession | None = None
    ) -> None:
        """
        Parameters:
        ----
            :param session: Session.
            :param db_con: Database connection.

        Returns:
        ----
            None
        """
        super().__init__(session, db_con)
        self._oauth_repository = OauthRepository(self._session, self._db)
        self._user_repository = UserRepository(self._session, self._db)
        self._terms_of_use_repository = TermsOfUseRepository(self._session, self._db)
        self._signed_terms_of_use_repository = SignedTermsOfUseRepository(
            self._session, self._db
        )

    @property
    def oauth_repository(self) -> OauthRepository:
        """
        Returns the Oauth repository.

        Returns
        -------
        OauthRepository
            The repository for Oauth-related data.
        """
        return self._oauth_repository

    @property
    def user_repository(self) -> UserRepository:
        """
        Returns the user repository instance associated with this unit of work.

        :return: UserRepository instance
        """
        return self._user_repository

    @property
    def terms_of_use_repository(self) -> TermsOfUseRepository:
        return self._terms_of_use_repository

    @property
    def signed_terms_of_use_repository(self) -> SignedTermsOfUseRepository:
        return self._signed_terms_of_use_repository
