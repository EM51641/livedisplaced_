from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar

from quart import current_app
from quart_auth import current_user

from src.Controllers.Exceptions.Users import AlreadyAuthenticatedUser

T = TypeVar("T")
P = ParamSpec("P")


def only_logged_out(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """
    A decorator to restrict route access to authenticated users.
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if await current_user.is_authenticated:
            raise AlreadyAuthenticatedUser("User is already authenticated.")
        else:
            return await current_app.ensure_async(func)(*args, **kwargs)

    return wrapper
