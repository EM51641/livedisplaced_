from unittest.mock import Mock
from uuid import UUID

import pytest
import pytest_asyncio
from quart import Quart
from quart.typing import TestClientProtocol as MockClientProtocol
from quart_auth import current_user
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.Context.Service.Oauth import (
    ContentTokenResponse,
    OauthFacebookService,
    OauthGoogleService,
    OauthSessionManager,
)
from src.Context.Service.UnitOfWork.Oauth import OAuthUnitOfWork
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from tests.integration.Factory.oauth import OauthFactory
from tests.integration.Factory.termsofuse import TermsOfUseFactory
from tests.integration.Factory.user import UserFactory


class BaseOauth:

    @pytest.fixture(autouse=True)
    def unit_of_work(self, scoped_session: async_scoped_session[AsyncSession]) -> None:
        """
        Setup the test on the PasscodeReset instance.
        """
        self._unit_of_work = OAuthUnitOfWork(
            session=Session(), db_con=DBSession(scoped_session)
        )

    @pytest_asyncio.fixture(autouse=True)
    async def setup_manager(self):
        self._manager = Mock(OauthSessionManager)

    @pytest_asyncio.fixture(autouse=True)
    async def setup_terms_of_use(self, terms_of_use_factory: TermsOfUseFactory):
        await terms_of_use_factory.create_terms_of_use()


class TestAuthFacebook(BaseOauth):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        client: MockClientProtocol,
        oauth_factory: OauthFactory,
        user_factory: UserFactory,
    ):
        self.client = client

        user_ids = [
            "f25494de-b0fc-411e-8cec-313e6fb3dafa",
            "15172ac2-baf0-41ee-ad2f-a6172fdc0e72",
            "c1402fa6-756a-49be-a8c7-d9f108e0eb59",
            "0b6ccca2-c907-4f5d-8a8f-08658fc929bd",
            "46c8a642-7dd8-4bab-8573-3f5bcb4ff2e2",
            "ae09ccfb-a3de-481f-a8b2-99bcebbe1a41",
        ]

        provider_ids = [
            "e87a1613-e443-4f78-9558-867f5ba91faf",
            "5a921187-19c7-4df4-8f4f-f31e78de5857",
            "30e9c5cc-101f-4ccc-9ed7-33e8b421eaeb",
            "4a84eb03-8d1f-49b7-8d2b-9deb1beb3711",
            "b341facd-ff0a-40f1-a425-799aa905d750",
            "964a870c-7c87-4b74-9d87-8f9f9cdf5a86",
        ]
        self.client = client
        users = [await user_factory.create_user(id=UUID(id)) for id in user_ids]

        for user, provider_user_id in zip(users, provider_ids):
            await oauth_factory.create_oauth_account(
                user_id=user.id,
                provider="facebook",
                provider_user_id=provider_user_id,
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "provider_user_id, expected_user_id",
        [
            (
                "e87a1613-e443-4f78-9558-867f5ba91faf",
                "f25494de-b0fc-411e-8cec-313e6fb3dafa",
            ),
            (
                "5a921187-19c7-4df4-8f4f-f31e78de5857",
                "15172ac2-baf0-41ee-ad2f-a6172fdc0e72",
            ),
            (
                "30e9c5cc-101f-4ccc-9ed7-33e8b421eaeb",
                "c1402fa6-756a-49be-a8c7-d9f108e0eb59",
            ),
            (
                "4a84eb03-8d1f-49b7-8d2b-9deb1beb3711",
                "0b6ccca2-c907-4f5d-8a8f-08658fc929bd",
            ),
            (
                "b341facd-ff0a-40f1-a425-799aa905d750",
                "46c8a642-7dd8-4bab-8573-3f5bcb4ff2e2",
            ),
            (
                "964a870c-7c87-4b74-9d87-8f9f9cdf5a86",
                "ae09ccfb-a3de-481f-a8b2-99bcebbe1a41",
            ),
        ],
    )
    async def test_facebook_registered_auth(
        self, app: Quart, provider_user_id: str, expected_user_id: str
    ):
        async with app.test_request_context("/test"):
            service = OauthFacebookService(self._unit_of_work, self._manager)
            response_token = ContentTokenResponse(
                content={
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "id": provider_user_id,
                }
            )

            self._manager.fetch_content.return_value = response_token

            await service.login("123")

            assert await current_user.is_authenticated
            assert current_user.auth_id == expected_user_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "first_name, last_name, provider_user_id",
        [
            ("john", "doe", "f87a1613-e443-4f78-9558-867f5ba91faf"),
            ("jane", "fal", "5b921187-19c7-4df4-8f4f-f31e78de5857"),
            ("joe", "fay", "31e9c5cc-101f-4ccc-9ed7-33e8b421eaeb"),
            ("jim", "magod", "5a84eb03-8d1f-49b7-8d2b-9deb1beb3711"),
            ("jess", "yan", "b441facd-ff0a-40f1-a425-799aa905d750"),
            ("jill", "fine", "a64a870c-7c87-4b74-9d87-8f9f9cdf5a86"),
        ],
    )
    async def test_facebook_new_auth(
        self, app: Quart, first_name: str, last_name: str, provider_user_id: str
    ):
        original_first_name = first_name
        original_last_name = last_name

        async with app.test_request_context("/test"):
            service = OauthFacebookService(self._unit_of_work, self._manager)
            response_token = ContentTokenResponse(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "id": provider_user_id,
                }
            )

            self._manager.fetch_content.return_value = response_token

            await service.login("123")
            assert await current_user.is_authenticated

            user = await current_user.load_user()  # type: ignore

            assert user.first_name == original_first_name
            assert user.last_name == original_last_name


class TestAuthGoogle(BaseOauth):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        client: MockClientProtocol,
        oauth_factory: OauthFactory,
        user_factory: UserFactory,
    ):
        user_ids = [
            "7c6fe9db-4e3a-4452-9cf8-80e923a59293",
            "645cc176-b3f1-45d0-95c7-a82023f3e5ae",
            "eb37f4c2-63a1-413b-b2f7-7b343d5207a9",
            "7e279a25-434c-4c53-a07a-301ca5d7ce9b",
            "7a042e34-130a-4345-9816-ee40ecb9f48a",
            "148a23d2-ad09-4b96-980b-9ba8a0013df0",
        ]

        provider_ids = [
            "7c65c1e5-82e2-4662-b728-b4fa42485e3a",
            "fcbd04c3-4021-4ef7-8ca5-a5a19e4d6e3c",
            "71545a13-7a1d-4006-8d72-3104f77383c1",
            "1759edc3-72ae-4244-8b01-63c1cd9d2b7d",
            "a81ad477-fb36-45b8-9cde-b3e60870e15c",
            "09e469e6-ec62-42c8-a648-ee38e07405eb",
        ]
        self.client = client
        users = [await user_factory.create_user(id=UUID(id)) for id in user_ids]

        for user, provider_user_id in zip(users, provider_ids):
            await oauth_factory.create_oauth_account(
                user_id=user.id,
                provider="google",
                provider_user_id=provider_user_id,
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "provider_user_id, expected_user_id",
        [
            (
                "7c65c1e5-82e2-4662-b728-b4fa42485e3a",
                "7c6fe9db-4e3a-4452-9cf8-80e923a59293",
            ),
            (
                "fcbd04c3-4021-4ef7-8ca5-a5a19e4d6e3c",
                "645cc176-b3f1-45d0-95c7-a82023f3e5ae",
            ),
            (
                "71545a13-7a1d-4006-8d72-3104f77383c1",
                "eb37f4c2-63a1-413b-b2f7-7b343d5207a9",
            ),
            (
                "1759edc3-72ae-4244-8b01-63c1cd9d2b7d",
                "7e279a25-434c-4c53-a07a-301ca5d7ce9b",
            ),
            (
                "a81ad477-fb36-45b8-9cde-b3e60870e15c",
                "7a042e34-130a-4345-9816-ee40ecb9f48a",
            ),
            (
                "09e469e6-ec62-42c8-a648-ee38e07405eb",
                "148a23d2-ad09-4b96-980b-9ba8a0013df0",
            ),
        ],
    )
    async def test_google_registered_auth(
        self, app: Quart, provider_user_id: str, expected_user_id: str
    ):
        async with app.test_request_context("/test"):
            service = OauthGoogleService(self._unit_of_work, self._manager)
            response_token = ContentTokenResponse(
                {
                    "given_name": "first_name",
                    "family_name": "last_name",
                    "sub": provider_user_id,
                }
            )

            self._manager.fetch_content.return_value = response_token
            await service.login("123")

            assert await current_user.is_authenticated
            assert current_user.auth_id == expected_user_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "first_name, last_name, provider_user_id",
        [
            ("jimmy", "fallon", "7c65c1e5-82e2-4662-b728-b4fb42485e3a"),
            ("jane", "fonda", "fcbd04c3-4021-4ef7-8ca5-a5a1ae4d6e3c"),
            ("joe", "frazier", "71545a13-7a1d-4006-8d72-310ff77383c1"),
            ("jim", "morrison", "1759edc3-72ae-4244-8a0f-63c1cd9d2b7d"),
            ("jessica", "alba", "a81ad477-ff37-45b8-9cde-b3e60870e15c"),
            ("jill", "foster", "09e469e6-ec62-42c8-f648-ee38e07405eb"),
        ],
    )
    async def test_google_new_auth(
        self, app: Quart, first_name: str, last_name: str, provider_user_id: str
    ):
        original_first_name = first_name
        original_last_name = last_name

        async with app.test_request_context("/test"):
            service = OauthGoogleService(self._unit_of_work, self._manager)
            response_token = ContentTokenResponse(
                {
                    "given_name": first_name,
                    "family_name": last_name,
                    "sub": provider_user_id,
                }
            )

            self._manager.fetch_content.return_value = response_token

            await service.login("123")
            assert await current_user.is_authenticated

            user = await current_user.load_user()  # type: ignore

            assert user.first_name == original_first_name
            assert user.last_name == original_last_name


class TestOauthSessionManager:
    @pytest_asyncio.fixture
    async def prepare_google_session(self, app: Quart):
        async with app.test_client():
            self._session_manager = OauthSessionManager(
                client_id="123425",
                client_secret="12345",
                authorization_uri="http://localhost/",
                scope="email",
                content_uri="http://localhost/",
                access_token_uri="http://localhost/",
                url_for="root.web.user.oauth_app.google_auth_redirect_controller",
            )

    @pytest_asyncio.fixture
    async def prepare_facebook_session(self, app: Quart):
        async with app.test_client():
            self._session_manager = OauthSessionManager(
                client_id="91741",
                client_secret="14141",
                authorization_uri="http://localhost/",
                scope="profile",
                content_uri="http://localhost/",
                access_token_uri="http://localhost/",
                url_for="root.web.user.oauth_app.facebook_auth_redirect_controller",
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("prepare_facebook_session")
    async def test_session_facebook(self, app: Quart):
        async with app.test_request_context("/"):
            assert self._session_manager.session.client_id == "91741"
            assert self._session_manager.session.client_secret == "14141"
            assert (
                self._session_manager.session.redirect_uri
                == "https://localhost/user/oauth/facebook"
            )
            assert self._session_manager.session.scope == "profile"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("prepare_google_session")
    async def test_session_google(self, app: Quart):
        async with app.test_request_context("/"):
            assert self._session_manager.session.client_id == "123425"
            assert self._session_manager.session.client_secret == "12345"
            assert (
                self._session_manager.session.redirect_uri
                == "https://localhost/user/oauth/google"
            )
            assert self._session_manager.session.scope == "email"
