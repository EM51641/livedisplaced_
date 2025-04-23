"""
This module contains functions for handling errors in the API.

Functions:
- handle_internal_error_request(e):
    Handles internal server errors and logs the exception
    with stack trace.
"""

import logging

from quart import Blueprint, redirect, url_for
from quart_auth import Unauthorized
from werkzeug import Response
from werkzeug.exceptions import InternalServerError

from src.Controllers.Exceptions.Users import AlreadyAuthenticatedUser

app = Blueprint("error_handler", __name__)
logger = logging.getLogger(__name__)


@app.app_errorhandler(InternalServerError)
async def handle_internal_error_request(*args, **kwargs) -> tuple[str, int]:
    """
    Handles internal server errors and logs the exception with stack trace.
    Args:
        *args
        **kwargs
    Returns:
        tuple: A tuple containing the error message and status code.
    """
    logger.error("Oups something wrong happened.", exc_info=True, stack_info=True)
    return "Something went wrong.\nWe are troubleshooting the issue", 500


@app.app_errorhandler(Unauthorized)
async def handle_unauthorized_request(*args, **kwargs) -> Response:
    """
    Handles internal server errors and logs the exception with stack trace.

    Args:
        *args
        **kwargs

    Returns:
        tuple: A tuple containing the error message and status code.
    """
    return redirect(url_for("root.web.user.account_login_app.controller"))


@app.app_errorhandler(AlreadyAuthenticatedUser)
async def handle_already_authenticated_request(*args, **kwargs) -> Response:
    """
    Handles internal server errors and logs the exception with stack trace.

    Args:
        *args
        **kwargs

    Returns:
        tuple: A tuple containing the error message and status code.
    """
    return redirect(url_for("root.web.overview_app.controller"))


@app.app_errorhandler(404)
async def handle_no_found(*args, **kwargs) -> tuple[str, int]:
    """
    Handles internal server errors and logs the exception with stack trace.
    Args:
        *args
        **kwargs
    Returns:
        tuple: A tuple containing the error message and status code.
    """
    return "Page not found", 404
