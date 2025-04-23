from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest
import pytest_asyncio
from faker import Faker
from quart import Quart
from quart_auth import authenticated_client as logged_in_client
from quart_auth import login_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.Context.Service.Exceptions.User import (
    EmailAlreadyUsed,
    IncorrectPassword,
    UserAccountNotActivated,
    UserAccountNotFound,
)
from src.Context.Service.Oauth import OauthFacebookService, OauthSessionManager
from src.Context.Service.UnitOfWork.Oauth import OAuthUnitOfWork
from src.Context.Service.UnitOfWork.Passcode import PasscodeUnitOfWork
from src.Context.Service.UnitOfWork.User import UserUnitOfWork
from src.Context.Service.User import (
    ResetPasswordDTO,
    ServiceDeleteAccount,
    ServiceLogin,
    ServiceRegistrationUser,
    ServiceUpdateAccountPassword,
    UserLoginDTO,
    UserRegistrationDTO,
)
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Email.sendgrid import EmailManager
from src.Infrastructure.Entities.Passcode import CredChoices, PasscodeEntity
from src.Infrastructure.Entities.TermsOfUse import SignedTermsOfUseEntity
from src.Infrastructure.Entities.User import UserEntity
from src.Middlewares.global_middleware import CustomAuthUser
from tests.integration.conftest import resolve_query_all, resolve_query_one
from tests.integration.Factory.termsofuse import TermsOfUseFactory
from tests.integration.Factory.user import UserFactory


class BaseTestUserService:
    """
    Base class for the user services.
    """

    @pytest_asyncio.fixture(autouse=True)
    async def setup_additional_data(
        self, user_factory: UserFactory, terms_of_use_factory: TermsOfUseFactory
    ) -> None:
        """
        Setup the test on the PasscodeReset instance.
        """

        await terms_of_use_factory.create_terms_of_use()

        for _ in range(20):
            await user_factory.create_user()


class TestServiceRegisterUser(BaseTestUserService):
    """
    Test class for the ServiceRegisterUser class.
    """

    @pytest.fixture
    def unit_of_work(
        self, scoped_session: async_scoped_session[AsyncSession]
    ) -> PasscodeUnitOfWork:
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        return PasscodeUnitOfWork(session=Session(), db_con=DBSession(scoped_session))

    @pytest.fixture(autouse=True)
    def setup_service(self, unit_of_work: PasscodeUnitOfWork):
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        email_service = EmailManager(url="http://localhost:3000/v3/mail/send")
        self._service = ServiceRegistrationUser(unit_of_work, email_service)

    @pytest_asyncio.fixture(autouse=True)
    async def setup_default_user(self, user_factory: UserFactory) -> None:
        """
        Setup the test on the ServiceRegisterUser instance.
        """
        await user_factory.create_user(email="myname@example.com")

    @pytest.mark.asyncio
    async def test_register_user(
        self, faker: Faker, session: AsyncSession, app: Quart
    ) -> None:
        """
        Test the register_user method.
        """
        from werkzeug.security import check_password_hash

        first_name, last_name, email, password = (
            faker.first_name(),
            faker.last_name(),
            faker.email(),
            faker.password(),
        )

        now = datetime.now(UTC)

        data = UserRegistrationDTO(
            first_name=first_name, last_name=last_name, email=email, password=password
        )

        async with app.test_request_context(""):
            await self._service.register_user(data)

        query = select(UserEntity).where(UserEntity.email == email)
        user = await resolve_query_one(query, session)

        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.email == email
        assert check_password_hash(user.password, password)  # type: ignore
        assert user.is_active is False
        assert now - timedelta(minutes=1) < user.created < now + timedelta(minutes=1)

    @pytest.mark.asyncio
    async def test_register_user_user_signed_terms(
        self, faker: Faker, session: AsyncSession, app: Quart
    ) -> None:
        """
        Test the register_user method with an already used email.
        """
        first_name, last_name, email, password = (
            faker.first_name(),
            faker.last_name(),
            faker.email(),
            faker.password(),
        )

        data = UserRegistrationDTO(
            first_name=first_name, last_name=last_name, email=email, password=password
        )

        async with app.test_request_context(""):
            await self._service.register_user(data)

        query_user = select(UserEntity).where(UserEntity.email == email)
        user = await resolve_query_one(query_user, session)

        query_terms = select(SignedTermsOfUseEntity).where(
            SignedTermsOfUseEntity.user_id == user.id
        )
        signed_terms = await resolve_query_one(query_terms, session)

        assert signed_terms

    @pytest.mark.asyncio
    async def test_register_user_activation_passcode(
        self, faker: Faker, session: AsyncSession, app: Quart
    ) -> None:
        """
        Test the register_user method with an already used email.
        """
        first_name, last_name, email, password = (
            faker.first_name(),
            faker.last_name(),
            faker.email(),
            faker.password(),
        )

        data = UserRegistrationDTO(
            first_name=first_name, last_name=last_name, email=email, password=password
        )

        async with app.test_request_context(""):
            await self._service.register_user(data)

        query_user = select(UserEntity).where(UserEntity.email == email)
        user = await resolve_query_one(query_user, session)

        query_passcode = select(PasscodeEntity).where(
            PasscodeEntity.user_id == user.id,
            PasscodeEntity.expiration
            > datetime.now(UTC) + timedelta(hours=23, minutes=59),
            PasscodeEntity.expiration
            < datetime.now(UTC) + timedelta(hours=24, minutes=1),
        )
        passcode = await resolve_query_one(query_passcode, session)

        assert passcode
        assert passcode.category == CredChoices.ACTIVATION

    @pytest.mark.asyncio
    async def test_register_user_with_already_used_email(self, faker: Faker) -> None:
        """
        Test the register_user method with an already used email.
        """
        data = UserRegistrationDTO(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email="myname@example.com",
            password=faker.password(),
        )

        with pytest.raises(EmailAlreadyUsed):
            await self._service.register_user(data)


class TestServiceLoginUser(BaseTestUserService):
    """
    Test class for the ServiceLoginUser class.
    """

    @pytest.fixture
    def unit_of_work(
        self, scoped_session: async_scoped_session[AsyncSession]
    ) -> UserUnitOfWork:
        """
        Setup the test on the ServiceLoginUser instance.
        """
        return UserUnitOfWork(session=Session(), db_con=DBSession(scoped_session))

    @pytest.fixture(autouse=True)
    def setup_service(self, unit_of_work: UserUnitOfWork):
        """
        Setup the test on the ServiceLoginUser instance.
        """
        self._service = ServiceLogin(unit_of_work)

    @pytest.fixture
    def login_params(self, faker: Faker) -> tuple[str, str]:
        """
        Generate an email and password for the test.
        """
        return faker.unique.email(), faker.password()

    @pytest_asyncio.fixture
    async def setup_active_user(
        self, login_params: tuple[str, str], user_factory: UserFactory
    ) -> None:
        """
        Setup the test on the ServiceLoginUser instance.
        """
        from werkzeug.security import generate_password_hash

        email, hashed_password = login_params

        stored_pwd = generate_password_hash(hashed_password)

        await user_factory.create_user(email=email, password=stored_pwd, is_active=True)

    @pytest_asyncio.fixture
    async def setup_inactive_user(
        self, login_params: tuple[str, str], user_factory: UserFactory
    ) -> None:
        """
        Setup the test on the ServiceLoginUser instance.
        """
        from werkzeug.security import generate_password_hash

        email, uhashed_password = login_params
        stored_pwd = generate_password_hash(uhashed_password)
        await user_factory.create_user(
            email=email, password=stored_pwd, is_active=False
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_active_user")
    async def test_login_user_success(
        self, login_params: tuple[str, str], app: Quart
    ) -> None:
        """
        Test the login_user method.
        """
        email, password = login_params
        data = UserLoginDTO(email=email, password=password)
        async with app.test_request_context("/"):
            res = await self._service.login(data)
        assert res == "Logged in successfully."

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_inactive_user")
    async def test_login_inactive_user(self, login_params: tuple[str, str]) -> None:
        """
        Test the login_user method with an inactive user.
        """
        email, password = login_params
        data = UserLoginDTO(email=email, password=password)
        with pytest.raises(UserAccountNotActivated):
            await self._service.login(data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "login_params",
        [
            ("fakeuser@example.com", "fakepassword"),
            ("newuser2@example.com", "newpassword21"),
        ],
    )
    async def test_login_user_with_incorrect_email_password(
        self, login_params: tuple[str, str]
    ) -> None:
        """
        Test the login_user method with an incorrect password.
        """
        email, password = login_params
        data = UserLoginDTO(email=email, password=password)
        with pytest.raises(UserAccountNotFound):
            await self._service.login(data)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_active_user")
    async def test_login_user_with_incorrect_email(
        self, login_params: tuple[str, str]
    ) -> None:
        """
        Test the login_user method with an incorrect email.
        """
        email, _ = login_params
        data = UserLoginDTO(email=email, password="fakepassword")
        with pytest.raises(UserAccountNotFound):
            await self._service.login(data)


class TestServiceDeleteAccount(BaseTestUserService):
    """
    Test class for the ServiceDeleteAccount class.
    """

    @pytest.fixture
    def unit_of_work(
        self, scoped_session: async_scoped_session[AsyncSession]
    ) -> UserUnitOfWork:
        """
        Setup the test on the ServiceDeleteAccount instance.
        """
        return UserUnitOfWork(session=Session(), db_con=DBSession(scoped_session))

    @pytest.fixture(autouse=True)
    def setup_service(self, unit_of_work: UserUnitOfWork):
        """
        Setup the test on the ServiceDeleteAccount instance.
        """
        self._service = ServiceDeleteAccount(unit_of_work)

    @pytest_asyncio.fixture
    async def user(self, user_factory: UserFactory) -> UserEntity:
        """
        Setup the test on the ServiceDeleteAccount instance.
        """
        user = await user_factory.create_user()
        return user

    @pytest.mark.asyncio
    async def test_delete_account_success_message(
        self, user: UserEntity, app: Quart
    ) -> None:
        """
        Test the delete_account method.
        """
        test_client = app.test_client()
        async with app.test_request_context("/"), logged_in_client(
            test_client, str(user.id)
        ):
            login_user(CustomAuthUser(auth_id=str(user.id)))
            result = await self._service.delete_user_account()
        assert result == "Account deleted successfully."

    @pytest.mark.asyncio
    async def test_delete_account_success(
        self, user: UserEntity, app: Quart, session: AsyncSession
    ) -> None:
        """
        Test the delete_account method.
        """
        test_client = app.test_client()
        async with logged_in_client(
            test_client, str(user.id)
        ), app.test_request_context("/"):
            login_user(CustomAuthUser(auth_id=str(user.id)))
            await self._service.delete_user_account()

        query = select(UserEntity).where(UserEntity.id == user.id)
        result = await resolve_query_all(query, session)
        assert len(result) == 0


class TestServiceUpdateAccountPassword(BaseTestUserService):

    @pytest.fixture
    def unit_of_work(
        self, scoped_session: async_scoped_session[AsyncSession]
    ) -> UserUnitOfWork:
        """
        Setup the test on the ServiceDeleteAccount instance.
        """
        return UserUnitOfWork(session=Session(), db_con=DBSession(scoped_session))

    @pytest.fixture(autouse=True)
    def setup_service(self, unit_of_work: UserUnitOfWork):
        """
        Setup the test on the ServiceDeleteAccount instance.
        """
        self._service = ServiceUpdateAccountPassword(unit_of_work)

    @pytest.fixture
    def login_params(self, faker: Faker) -> tuple[str, str]:
        """
        Generate an email and password for the test.
        """
        return faker.unique.email(), faker.password()

    @pytest_asyncio.fixture
    async def user(
        self, login_params: tuple[str, str], user_factory: UserFactory
    ) -> UserEntity:
        """
        Setup the test on the ServiceLoginUser instance.
        """
        from werkzeug.security import generate_password_hash

        email, pwd = login_params
        stored_pwd = generate_password_hash(pwd)
        user = await user_factory.create_user(email=email, password=stored_pwd)
        return user

    @pytest.mark.asyncio
    async def test_update_password_success(
        self, login_params: tuple[str, str], user: UserEntity, app: Quart, faker: Faker
    ) -> None:
        """
        Test the update_password method.
        """
        _, old_password = login_params
        new_password = faker.password()
        data = ResetPasswordDTO(old_password=old_password, new_password=new_password)  # type: ignore

        test_client = app.test_client()
        async with app.test_request_context("/"), logged_in_client(
            test_client, str(user.id)
        ):
            login_user(CustomAuthUser(auth_id=str(user.id)))
            res = await self._service.update_password(data)

        assert res == "Password updated successfully."

    @pytest.mark.asyncio
    async def test_update_password_with_incorrect_old_password(
        self, user: UserEntity, app: Quart, faker: Faker
    ) -> None:
        """
        Test the update_password method with an incorrect old password.
        """
        data = ResetPasswordDTO(
            old_password="fakepassword", new_password=faker.password()
        )

        test_client = app.test_client()
        async with app.test_request_context("/"), logged_in_client(
            test_client, str(user.id)
        ):
            login_user(CustomAuthUser(auth_id=str(user.id)))
            with pytest.raises(IncorrectPassword):
                await self._service.update_password(data)


class TestLoginOrRegisterOauthService:

    @pytest.fixture
    def unit_of_work(
        self, scoped_session: async_scoped_session[AsyncSession]
    ) -> OAuthUnitOfWork:
        """
        Setup the unit of work for the test.
        """
        return OAuthUnitOfWork(session=Session(), db_con=DBSession(scoped_session))

    @pytest.fixture
    def oauth_session(self) -> OauthSessionManager:
        return Mock(OauthSessionManager)

    @pytest.fixture(autouse=True)
    def setup_service(
        self, unit_of_work: OAuthUnitOfWork, oauth_session: OauthSessionManager
    ) -> None:
        """
        Setup the service for the test.
        """
        self._service = OauthFacebookService(unit_of_work, oauth_session)
