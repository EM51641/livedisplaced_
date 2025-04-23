from src.Context.Service.UnitOfWork import UnitOfWork
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Repositories.TermsOfUse import (
    SignedTermsOfUseRepository,
    TermsOfUseRepository,
)


class TermsOfUseUnitOfWork(UnitOfWork):
    """
    Unit of work for handling multiple repositories related to terms of use.

    Attributes:
        session (Session | None): The session context.
        db_con (Database | None): The database connection (optional).

    Properties:
        terms_of_use_repository (TermsOfUseRepository):
                The repository for terms of use.
        signed_terms_of_use_repository (SignedTermsOfUseRepository):
                The repository for signed terms of use.
    """

    def __init__(self, session: Session | None = None, db_con: DBSession | None = None):
        super().__init__(session, db_con)
        self._terms_of_use_repository = TermsOfUseRepository(self.session, self._db)
        self._signed_terms_of_use_repository = SignedTermsOfUseRepository(
            self.session, self._db
        )

    @property
    def terms_of_use_repository(self) -> TermsOfUseRepository:
        return self._terms_of_use_repository

    @property
    def signed_terms_of_use_repository(self) -> SignedTermsOfUseRepository:
        return self._signed_terms_of_use_repository
