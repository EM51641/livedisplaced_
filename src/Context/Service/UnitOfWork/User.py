"""
This module contains the UserUnitOfWork class, which is used to handle
multiple repositories related to user data.

Classes:
- UserUnitOfWork: Passcode Unit of Work, used to handle multiple repositories.
"""

from src.Context.Service.UnitOfWork import UnitOfWork
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Repositories.User import UserRepository


class UserUnitOfWork(UnitOfWork):
    """
    Passcode Unit of Work, used to handle multiple repositories related to
    user data.
    """

    def __init__(self, session: Session | None = None, db_con: DBSession | None = None):
        """
        Initializes a new instance of the UnitOfWork class.

        :param session: The current session.
            :type session: Session
        :param db_con: The database connection.
            :type db_con: Database | None
        """

        super().__init__(session, db_con)
        self._user_repository = UserRepository(self.session, self._db)

    @property
    def user_repository(self) -> UserRepository:
        """
        Returns the user repository instance associated with this Unit of Work.
        :return: The user repository instance.
        :rtype: UserRepository
        """
        return self._user_repository
