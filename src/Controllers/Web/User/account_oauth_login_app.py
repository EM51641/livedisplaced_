from __future__ import annotations

import os
from typing import Generic, TypeVar

from quart import Blueprint, redirect, request, url_for
from quart.views import MethodView
from werkzeug import Response

from src.Context.Service.Oauth import (
    BaseOauthService,
    OauthFacebookService,
    OauthGoogleService,
    OauthSessionManager,
)
from src.Context.Service.UnitOfWork.Oauth import OAuthUnitOfWork

facebook_session_manager = OauthSessionManager(
    client_id=os.environ["FACEBOOK_CLIENT_ID"],
    client_secret=os.environ["FACEBOOK_CLIENT_SECRET"],
    authorization_uri=os.environ["FACEBOOK_AUTHORIZATION_URI"],
    scope=os.environ["FACEBOOK_SCOPE"],
    content_uri=os.environ["FACEBOOK_CONTENT_URI"],
    access_token_uri=os.environ["FACEBOOK_ACCESS_TOKEN_URI"],
    url_for=os.environ["FACEBOOK_URL_FOR"],
)


google_session_manager = OauthSessionManager(
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    authorization_uri=os.environ["GOOGLE_AUTHORIZATION_URI"],
    scope=os.environ["GOOGLE_SCOPE"],
    content_uri=os.environ["GOOGLE_CONTENT_URI"],
    access_token_uri=os.environ["GOOGLE_ACCESS_TOKEN_URI"],
    url_for=os.environ["GOOGLE_URL_FOR"],
)

account_oauth_login_app = Blueprint("oauth_app", __name__, url_prefix="/oauth")


@account_oauth_login_app.route("/facebook", methods=["GET"])
async def facebook_auth_redirect_controller() -> Response:
    """
    Facebook login redirect route.

    Redirects the user to the Facebook authorization URL for login.
    """
    url = await facebook_session_manager.fetch_authorization_url()
    return redirect(url)


@account_oauth_login_app.route("/google", methods=["GET"])
async def google_auth_redirect_controller() -> Response:
    """
    Google login redirect route.

    Redirects the user to the Google authorization URL for login.
    """
    url = await google_session_manager.fetch_authorization_url()
    return redirect(url)


TOauthService = TypeVar("TOauthService", bound=BaseOauthService)


class OAuthCallback(MethodView, Generic[TOauthService]):
    """
    OAuth callback view.

    This view handles the callback from the OAuth provider after successful login.
    """

    def __init__(self, oauth_service: TOauthService) -> None:
        """
        Initializes an instance of the account_oauth_login_page class.

        Args:
            oauth_service: An instance of the TOauthService class.

        Returns:
            None
        """
        self._oauth_service = oauth_service

    @property
    def oauth_service(self) -> TOauthService:
        return self._oauth_service

    async def get(self) -> Response:
        """
        Login callback route.

        Handles the callback from the OAuth provider after successful login.
        """
        code = request.args["code"]
        await self.oauth_service.login(code)
        return redirect(url_for("root.web.overview_app.controller"))


class FacebookOAuthCallback(OAuthCallback[OauthFacebookService]):
    """
    Represents a callback handler for Facebook OAuth authentication.

    Args:
        oauth_service (OauthFacebookService): An instance of the Facebook OAuth service.
    """


class GoogleOAuthCallback(OAuthCallback[OauthGoogleService]):
    """
    Represents a callback handler for Google OAuth authentication.

    Args:
        oauth_service (OauthGoogleService): An instance of the Google OAuth service.
    """


facebook_callback_controller = FacebookOAuthCallback.as_view(
    "facebook_callback_controller",
    OauthFacebookService(OAuthUnitOfWork(), facebook_session_manager),
)

google_callback_controller = GoogleOAuthCallback.as_view(
    "google_callback_controller",
    OauthGoogleService(OAuthUnitOfWork(), google_session_manager),
)

account_oauth_login_app.add_url_rule(
    "/facebook/callback", view_func=facebook_callback_controller
)
account_oauth_login_app.add_url_rule(
    "/google/callback", view_func=google_callback_controller
)
