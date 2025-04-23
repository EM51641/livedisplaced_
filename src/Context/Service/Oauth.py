from __future__ import annotations

import logging
import json

from abc import abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from authlib.integrations.httpx_client import AsyncOAuth2Client  # type: ignore
from quart import url_for

from src.Context.Domain.Oauth import Oauth
from src.Context.Domain.TermsOfUse import SignedTermsOfUse, TermsOfUse
from src.Context.Domain.User import User
from src.Context.Service import ServiceBase
from src.Context.Service.UnitOfWork.Oauth import OAuthUnitOfWork
from src.Context.Service.Utils.login_user import login_user
from src.Infrastructure.Repositories.Utils import NoEntityFound

if TYPE_CHECKING:
    from typing import Any


@dataclass
class UserOAuthDTO:
    """
    Represents user OAuth information.

    Attributes:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        provider_user_id (str): The ID of the user provided by the OAuth provider.
        provider (str): The OAuth provider used for authentication.
    """

    first_name: str
    last_name: str
    provider_user_id: str
    provider: str


@dataclass
class ContentTokenResponse:
    """
    Represents a response containing content token information.

    Attributes:
        content (dict[Any, Any]): The content token information.
    """

    content: dict[Any, Any]


@dataclass
class LinkedAccounts:
    """
    Represents a user's linked accounts.

    Attributes:
        user (User): The user associated with the linked accounts.
        oauth (Oauth): The OAuth information for the linked accounts.
        agreement (SignedTermsOfUse): The signed terms of use agreement for the linked accounts.
    """

    user: User
    oauth: Oauth
    agreement: SignedTermsOfUse


class OauthSessionManager:
    """
    Session manager for oauth authentication.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: str,
        authorization_uri: str,
        access_token_uri: str,
        content_uri: str,
        url_for: str,
    ):
        """
        Initializes an instance of the Oauth class.

        Args:
            client_id (str): The client ID for the OAuth application.
            client_secret (str): The client secret for the OAuth application.
            scope (str): The scope of the OAuth application.
            authorization_uri (str): The authorization URI for the OAuth application.
            access_token_uri (str): The access token URI for the OAuth application.
            content_uri (str): The content URI for the OAuth application.
            url_for (str): The URL for the OAuth application.

        Returns:
            None
        """

        self._config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
            "authorization_uri": authorization_uri,
            "access_token_uri": access_token_uri,
            "content_uri": content_uri,
            "url_for": url_for,
        }

    @property
    def config(self) -> dict[str, str]:
        """
        Returns the configuration.

        Returns:
        -------
        dict[str, str]
            The configuration.
        """
        return self._config

    @property
    def session(self) -> AsyncOAuth2Client:
        """
        Returns the session object for OAuth authentication.

        Returns:
        ----
            AsyncOAuth2Client
                The session object.
        """
        session = AsyncOAuth2Client(
            client_id=self._config["client_id"],
            client_secret=self._config["client_secret"],
            redirect_uri=url_for(
                self._config["url_for"], _external=True, _scheme="https"
            ),
            scope=self._config["scope"],
        )
        return session

    async def fetch_authorization_url(self, **kwargs: Any) -> str:
        """
        Fetch the authorization url from the oauth provider.

        Params:
        ----
            None

        Returns:
        ----
            url (str):
                url sent by the oauth provider.
        """
        async with self.session as session:
            uri, _ = session.create_authorization_url(
                self._config["authorization_uri"], response_type="code", **kwargs
            )
            logging.error(uri)
        return uri

    async def fetch_content(self, code: str) -> ContentTokenResponse:
        """
        Fetch the token from the oauth provider.

        Params:
        ----
            code (str):
                code sent by the oauth provider.

        Returns:
        ----
            content, token (tuple[dict[Any, Any], dict[Any, Any]]):
                content: json http response sent by the oath provider.
                token: token sent by the oauth provider.
        """

        async with self.session as session:
            await session.fetch_token(
                self._config["access_token_uri"],
                grant_type="authorization_code",
                code=code,
            )  # type: ignore

            data = await session.get(self.config["content_uri"])
            content = json.loads(data.content)

        return ContentTokenResponse(content=content)


class BaseOauthService(ServiceBase[OAuthUnitOfWork]):
    """
    A base class for OAuth services.

    Attributes:
    ----------
    oauth_session : OauthSessionManager
        The OAuth session manager.

    Methods:
    -------
    oauth_session() -> OauthSessionManager:
        Returns the OAuth session manager.

    _login(data: UserOAuthDTO) -> None:
        Logs in a user using OAuth.

    _find_registered_third_party_account(data: UserOAuthDTO) -> Oauth | None:
        Finds a registered third-party account.

    _find_user_by_id(oauth: Oauth) -> User:
        Finds a user by ID.

    _create_user_linked_account(data: UserOAuthDTO) -> User:
        Creates a user linked account.

    _set_linked_accounts(data: UserOAuthDTO) -> LinkedAccounts:
        Sets a user account.

    _set_user_account(data: UserOAuthDTO) -> User:
        Sets a user account.

    _set_new_user_as_compliant(user: User) -> SignedTermsOfUse:
        Sets a new user as compliant.

    _generate_signed_terms_of_use(user: User, terms_agreed_on: TermsOfUse):
        Generates signed terms of use.

    """

    def __init__(
        self, unit_of_work: OAuthUnitOfWork, oauth_session: OauthSessionManager
    ) -> None:
        """
        Initializes a new instance of the BaseOauthService class.

        Parameters:
        ----------
        oauth_session : OauthSessionManager
            The OAuth session manager.
        """
        super().__init__(unit_of_work)
        self._oauth_session = oauth_session

    @property
    def oauth_session(self) -> OauthSessionManager:
        """
        Returns the OAuth session manager.

        Returns:
        -------
        OauthSessionManager
            The OAuth session manager.
        """
        return self._oauth_session

    @abstractmethod
    async def login(self, code: str) -> None:
        """
        Logs in the user using the provided authorization code.

        Args:
        ----
            code (str): The authorization code to use for logging in.

        Returns:
        ----
            None
        """

    async def _login(self, data: UserOAuthDTO) -> None:
        """
        Logs in a user using OAuth.

        Parameters:
        ----
            data : UserOAuthDTO
                The user OAuth data.

        Returns:
        ----
            None
        """
        oauth = await self._find_registered_third_party_account(data)

        if oauth:
            user = await self._find_user_by_id(oauth)
        else:
            user = await self._create_user_linked_account(data)

        login_user(user)

    async def _find_registered_third_party_account(
        self, data: UserOAuthDTO
    ) -> Oauth | None:
        """
        Finds a registered third-party account.

        Parameters:
        ----
            data : UserOAuthDTO
                The user OAuth data.

        Returns:
        ----
            Oauth | None
                The registered third-party account, or None if not found.
        """
        try:
            oauth = await self._unit_of_work.oauth_repository.find_by_provider_by_uid(  # noqa
                provider=data.provider,
                provider_user_id=data.provider_user_id,
            )
            return oauth
        except NoEntityFound:
            return None

    async def _find_user_by_id(self, oauth: Oauth) -> User:
        """
        Finds a user by ID.

        Parameters:
        ----
            oauth : Oauth
                The OAuth data.

        Returns:
        ----
            User
                The user.
        """
        user = await self._unit_of_work.user_repository.find_by_id(id=oauth.user_id)
        return user

    async def _create_user_linked_account(self, data: UserOAuthDTO) -> User:
        """
        Creates a user linked account.

        Parameters:
        ----
            data: UserOAuthDTO
                The user OAuth data.

        Returns:
        ----
            User: User
                The created user.
        """
        user, oauth, agreement = await self._set_linked_accounts(data)
        self._unit_of_work.user_repository.add(user)
        await self._unit_of_work.flush()

        self._unit_of_work.signed_terms_of_use_repository.add(agreement)
        self._unit_of_work.oauth_repository.add(oauth)
        await self._unit_of_work.save()
        return user

    async def _set_linked_accounts(
        self, data: UserOAuthDTO
    ) -> tuple[User, Oauth, SignedTermsOfUse]:
        """
        Sets a user account.

        Parameters:
        ----
            data : UserOAuthDTO
                The user OAuth data.

        Returns:
        ----
            LinkedAccounts
                The linked accounts.
        """
        user = self._build_user(data)
        oauth = self._build_oauth(user, data)
        agreement = await self._set_new_user_as_compliant(user)
        return user, oauth, agreement

    async def _set_new_user_as_compliant(self, user: User) -> SignedTermsOfUse:
        """
        Sets a new user as compliant.

        Parameters:
        ----
            user: User
                The user

        Returns:
        ----
            SignedTermsOfUse
                The signed terms of use
        """
        latest_term = (
            await self._unit_of_work.terms_of_use_repository.find_latest_version()  # noqa
        )
        agreement = self._build_agreement(user, latest_term)
        return agreement

    def _build_user(self, data: UserOAuthDTO) -> User:
        """
        Sets a user account.

        Parameters:
        ----
            data : UserOAuthDTO
                The user OAuth data.

        Returns:
        ----
            User
                The created user.
        """
        return User(
            id=uuid4(),
            first_name=data.first_name,
            last_name=data.last_name,
            email=None,
            password=None,
            is_active=True,
            created=datetime.now(UTC),
        )

    def _build_oauth(self, user: User, data: UserOAuthDTO) -> Oauth:
        """
        Sets OAuth data.
        Parameters:
        ----------
            user : User
                The user.
            data : UserOAuthDTO
                The user OAuth data.
        Returns:
        -------
            Oauth
                The OAuth data.
        """
        return Oauth(
            id=uuid4(),
            user_id=user.id,
            provider=data.provider,
            provider_user_id=data.provider_user_id,
        )

    def _build_agreement(self, user: User, terms: TermsOfUse) -> SignedTermsOfUse:
        """
        Sets a new user as compliant.

        Parameters:
        ----
            user: User
                The user

        Returns:
        ----
            SignedTermsOfUse
                The signed terms of use
        """
        return SignedTermsOfUse(
            id=uuid4(),
            user_id=user.id,
            termsofuse_id=terms.id,
            signed=user.created,
        )


class OauthGoogleService(BaseOauthService):
    """
    Oauth using google api's.
    """

    async def login(self, code: str) -> None:
        """
        Logs in the user using the provided authorization code.

        Parms:
        ----
            code (str): The authorization code.

        Returns:
        ----
            None
        """
        user_data = await self._request_user_data(code)
        await self._login(user_data)

    async def _request_user_data(self, code: str) -> UserOAuthDTO:
        """
        Request the account data from the oauth provider.

        Params:
        ----
           code(str):
                code sent by the oauth provider.

        Returns:
        ----
           UserOAuthDTO
        """
        response = await self._oauth_session.fetch_content(code)
        return UserOAuthDTO(
            first_name=response.content["given_name"],
            last_name=response.content["family_name"],
            provider_user_id=response.content["sub"],
            provider="google",
        )


class OauthFacebookService(BaseOauthService):
    """
    Oauth using Facebook api's.
    """

    async def login(self, code: str) -> None:
        """
        Logs in the user using the provided authorization code.

        Params:
        ----
            code (str):
                The authorization code to use for logging in.

        Returns:
        ----
             None
        """
        user_data = await self._request_user_data(code)
        await self._login(user_data)

    async def _request_user_data(self, code: str) -> UserOAuthDTO:
        """
        Request the account data from the oauth provider.

        Params:
        ----
           code(str):
                code sent by the oauth provider.

        Returns:
        ----
           UserOAuthDTO
        """
        response = await self._oauth_session.fetch_content(code)
        return UserOAuthDTO(
            first_name=response.content["first_name"],
            last_name=response.content["last_name"],
            provider_user_id=response.content["id"],
            provider="facebook",
        )
