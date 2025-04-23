import os
from unittest.mock import Mock, patch

import pytest
from quart import Quart, Request
from quart.typing import TestClientProtocol as MockClientProtocol

from src.Context.Service.Oauth import OauthFacebookService, OauthGoogleService
from src.Controllers.Web.User.account_oauth_login_app import (
    FacebookOAuthCallback,
    GoogleOAuthCallback,
)


@pytest.mark.asyncio
async def test_facebook_endpoint(client: MockClientProtocol):
    """Test facebook endpoint."""
    response = await client.get("/user/oauth/facebook")
    assert response.status_code == 302
    assert (
        f"https://www.facebook.com/dialog/oauth?response_type=code&client_id={os.environ["FACEBOOK_CLIENT_ID"]}&redirect_uri=https%3A%2F%2Flocalhost%2F&scope=email+public_profile"  # noqa
        in response.location
    )


@pytest.mark.asyncio
async def test_google_endpoint(client: MockClientProtocol):
    """Test google endpoint."""
    response = await client.get("/user/oauth/google")
    assert response.status_code == 302
    assert (
        f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={os.environ["GOOGLE_CLIENT_ID"]}&redirect_uri=https%3A%2F%2Flocalhost%2F&scope=profile+email+openid&state="  # noqa
        in response.location
    )


@pytest.mark.asyncio
@patch(
    "src.Controllers.Web.User.account_oauth_login_app.request",
    Mock(Request, args={"code": "123"}),
)
async def test_facebook_callback_endpoint(app: Quart):
    """Test facebook callback endpoint."""
    mocked_service = Mock(OauthFacebookService)

    app.view_functions["root.web.user.oauth_app.facebook_callback_controller"] = (
        FacebookOAuthCallback.as_view("facebook_callback_controller", mocked_service)
    )

    async with app.test_client() as client:
        response = await client.get("/user/oauth/facebook/callback")

        assert response.status_code == 302
        assert response.location == "/"


@pytest.mark.asyncio
@patch(
    "src.Controllers.Web.User.account_oauth_login_app.request",
    Mock(Request, args={"code": "123"}),
)
async def test_google_callback_endpoint(app: Quart):
    """Test google callback endpoint."""
    mocked_service = Mock(OauthGoogleService)

    app.view_functions["root.web.user.oauth_app.google_callback_controller"] = (
        GoogleOAuthCallback.as_view("google_callback_controller", mocked_service)
    )

    async with app.test_client() as client:
        response = await client.get("/user/oauth/google/callback")

        assert response.status_code == 302
        assert response.location == "/"
