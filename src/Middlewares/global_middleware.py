"""
This module defines a blueprint for global app context and contains helper
functions for loading and injecting the current user into the global app
context.

The blueprint is defined in `global_app_ctx` and is used to store global
variables that can be accessed across different parts of the application.

The `CustomAuthUser` class extends the `AuthUser` class from `quart_auth` and
provides a method to load a user from the database by their ID.

The `inject_current_user` function checks if the user is authenticated and
loads the user if they are. The loaded user is then returned as a dictionary
with the key "current_user". If the user is not authenticated, None is returned
with the key "current_user".
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from quart import Blueprint
from quart_auth import AuthUser, current_user

from src.Infrastructure.Database import DBSession
from src.Infrastructure.Repositories.Mappers.User import EntityDomainMapperUser

if TYPE_CHECKING:
    from src.Context.Domain.User import User


global_app_ctx = Blueprint("global_app_ctx", __name__)


class CustomAuthUser(AuthUser):
    async def load_user(self, mapper=EntityDomainMapperUser()):
        """
        Load a user from the database by their ID.

        Args:
            mapper (type[EntityDomainMapperUser], optional):
                The mapper to use to convert the database record to a domain
                object. Defaults to EntityDomainMapperUser.

        Returns:
            User: The loaded user, or None if no user was found.
        """
        from src.Infrastructure.Entities.User import UserEntity
        from src.managers import db

        db_session = DBSession(db.session)

        assert self._auth_id is not None
        select_user = db_session.select(UserEntity).filter(
            UserEntity.id == self._auth_id  # type: ignore
        )
        result = await db_session.execute(select_user)
        user_record = result.scalar_one()
        user = mapper.to_domain(user_record)
        return user


async def inject_current_user() -> dict[str, User | None]:
    """
    Inject the current user into the global app context.

    This function checks if the user is authenticated and loads the user
    if they are.
    The loaded user is then returned as a dictionary with the key
    "current_user".
    If the user is not authenticated, None is returned with the key
    "current_user".

    Returns:
        A dictionary with the key "current_user" and the value of the loaded
        user or None.
    """
    auth_user: CustomAuthUser = current_user  # type: ignore
    if auth_user.auth_id:
        user = await auth_user.load_user()
        return dict(user=user)
    else:
        return dict(user=None)


global_app_ctx.app_context_processor(inject_current_user)
