from quart_auth import login_user as login_user_quart

from src.Context.Domain.User import User
from src.Middlewares.global_middleware import CustomAuthUser


def login_user(user: User) -> None:
    """
    Log in a user.

    This function takes a User object and logs in the user by creating a CustomAuthUser object
    with the user's ID and calling the login_user_quart function from the quart_auth module.

    Args:
        user (User): The user to log in.
    """
    auth_user = CustomAuthUser(str(user.id))
    login_user_quart(auth_user)
