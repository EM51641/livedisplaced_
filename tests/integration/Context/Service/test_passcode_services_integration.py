from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.Context.Service.Exceptions import IncorrectInput
from src.Context.Service.Exceptions.Passcode import (
    InvalidActivationToken,
    InvalidResetToken,
)
from src.Context.Service.Passcode import (
    PasscodeDTO,
    RequestPasswordChangeDTO,
    ServiceActivateUser,
    ServicePasswordReset,
    ServiceRequestPasswordReset,
)
from src.Context.Service.UnitOfWork.Passcode import PasscodeUnitOfWork
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Email.sendgrid import EmailManager
from src.Infrastructure.Entities.Passcode import CredChoices, PasscodeEntity
from src.Infrastructure.Entities.User import UserEntity
from tests.integration.conftest import resolve_query_one
from tests.integration.Factory.passcode import PasscodeFactory
from tests.integration.Factory.user import UserFactory


class BaseTestPasscodeService:
    """
    Base class for the passcode service.
    """

    @pytest_asyncio.fixture(autouse=True)
    async def setup_additional_data(
        self, passcode_factory: PasscodeFactory, user_factory: UserFactory
    ) -> None:
        """
        Setup the test on the PasscodeReset instance.
        """
        for _ in range(20):
            user = await user_factory.create_user()
            await passcode_factory.create_passcode(user_id=user.id)


class TestServicePasscodeReset(BaseTestPasscodeService):

    @pytest.fixture(autouse=True)
    def setup_service(self, scoped_session: async_scoped_session[AsyncSession]) -> None:
        """
        Setup the test on the PasscodeReset instance.
        """
        unit_of_work = PasscodeUnitOfWork(
            session=Session(), db_con=DBSession(scoped_session)
        )
        self._service = ServicePasswordReset(unit_of_work)

    @pytest_asyncio.fixture(autouse=True)
    async def user_and_valid_passcode(
        self, passcode_factory: PasscodeFactory, user_factory: UserFactory
    ) -> tuple[UserEntity, PasscodeEntity]:
        """
        Setup the test on the PasscodeReset instance.
        """
        user = await user_factory.create_user()
        passcode = await passcode_factory.create_passcode(
            user_id=user.id,
            category=CredChoices.RESET,  # type: ignore
            expiration=datetime.now(UTC) + timedelta(minutes=1),
        )
        return user, passcode

    @pytest_asyncio.fixture(autouse=True)
    async def user_and_expired_passcode(
        self, passcode_factory: PasscodeFactory, user_factory: UserFactory
    ) -> tuple[UserEntity, PasscodeEntity]:
        """
        Create an expired passcode.
        """
        user = await user_factory.create_user()
        passcode = await passcode_factory.create_passcode(
            user_id=user.id,
            category=CredChoices.RESET,  # type: ignore
            expiration=datetime.now(UTC) - timedelta(minutes=1),
        )
        return user, passcode

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "password",
        [
            "password",
            "password123",
            "password123!",
            "password123!@#",
            "password123!@#123",
        ],
    )
    async def test_reset_passcode(
        self,
        user_and_valid_passcode: tuple[UserEntity, PasscodeEntity],
        session: AsyncSession,
        password: str,
    ) -> None:
        """
        Test that the reset_passcode method resets the passcode.
        """
        from werkzeug.security import check_password_hash

        user, passcode = user_and_valid_passcode

        param = PasscodeDTO(
            token=passcode.id,
            password=password,
        )
        await self._service.reset_user_password(param)

        query = select(UserEntity).where(UserEntity.id == user.id)
        user = await resolve_query_one(query, session)

        assert check_password_hash(user.password, password)  # type: ignore

    async def test_reset_passcode_is_deleted(
        self,
        faker: Faker,
        user_and_valid_passcode: tuple[UserEntity, PasscodeEntity],
        session: AsyncSession,
    ) -> None:
        """
        Test that the reset_passcode method resets the passcode.
        """
        password = faker.password()
        _, passcode = user_and_valid_passcode
        param = PasscodeDTO(token=passcode.id, password=password)

        await self._service.reset_user_password(param)

        query = select(PasscodeEntity).where(PasscodeEntity.id == passcode.id)

        with pytest.raises(NoResultFound):
            await resolve_query_one(query, session)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "uid",
        [
            UUID("f87a1613-e443-4f78-9558-867f5ba91faf"),
            UUID("5b921187-19c7-4df4-8f4f-f31e78de5857"),
            UUID("31e9c5cc-101f-4ccc-9ed7-33e8b421eaeb"),
        ],
    )
    async def test_reset_invalid_passcode(
        self, user_and_expired_passcode: UserFactory, faker: Faker, uid: UUID
    ) -> None:
        """
        Test that the reset_passcode method raises an error when the passcode is expired.
        """
        password = faker.password()
        param = PasscodeDTO(token=uid, password=password)

        with pytest.raises(InvalidResetToken):
            await self._service.reset_user_password(param)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "password",
        ["password", "password123", "password123!"],
    )
    async def test_reset_expired_passcode(
        self,
        user_and_expired_passcode: tuple[UserEntity, PasscodeEntity],
        password: str,
    ) -> None:
        """
        Test that the reset_passcode method raises an error when the passcode is expired.
        """
        _, passcode = user_and_expired_passcode
        param = PasscodeDTO(token=passcode.id, password=password)

        with pytest.raises(InvalidResetToken):
            await self._service.reset_user_password(param)


class TestServiceActivateUser(BaseTestPasscodeService):

    @pytest.fixture(autouse=True)
    def setup_service(self, scoped_session: async_scoped_session[AsyncSession]) -> None:
        """
        Setup the test on the PasscodeReset instance.
        """
        unit_of_work = PasscodeUnitOfWork(
            session=Session(), db_con=DBSession(scoped_session)
        )
        self._service = ServiceActivateUser(unit_of_work)

    @pytest_asyncio.fixture(autouse=True)
    async def user_and_valid_passcode(
        self, passcode_factory: PasscodeFactory, user_factory: UserFactory
    ) -> tuple[UserEntity, PasscodeEntity]:
        """
        Setup the test on the PasscodeReset instance.
        """
        user = await user_factory.create_user(is_active=False)
        passcode = await passcode_factory.create_passcode(
            user_id=user.id,
            category=CredChoices.ACTIVATION,  # type: ignore
            expiration=datetime.now(UTC) + timedelta(minutes=1),
        )
        return user, passcode

    @pytest_asyncio.fixture(autouse=True)
    async def user_and_expired_passcode(
        self, passcode_factory: PasscodeFactory, user_factory: UserFactory
    ) -> tuple[UserEntity, PasscodeEntity]:
        """
        Create an expired passcode.
        """
        user = await user_factory.create_user(is_active=False)
        passcode = await passcode_factory.create_passcode(
            user_id=user.id,
            category=CredChoices.ACTIVATION,  # type: ignore
            expiration=datetime.now(UTC) - timedelta(minutes=1),
        )
        return user, passcode

    @pytest.mark.asyncio
    async def test_activate_user(
        self,
        user_and_valid_passcode: tuple[UserEntity, PasscodeEntity],
        session: AsyncSession,
    ) -> None:
        """
        Test that the reset_passcode method resets the passcode.
        """
        user, token = user_and_valid_passcode

        await self._service.activate_user(token.id)

        query = select(UserEntity).where(UserEntity.id == user.id)
        user = await resolve_query_one(query, session)

        assert user.is_active

    @pytest.mark.asyncio
    async def test_activation_passcode_is_deleted(
        self,
        user_and_valid_passcode: tuple[UserEntity, PasscodeEntity],
        session: AsyncSession,
    ) -> None:

        _, token = user_and_valid_passcode

        await self._service.activate_user(token.id)

        query = select(PasscodeEntity).where(PasscodeEntity.id == token.id)

        with pytest.raises(NoResultFound):
            await resolve_query_one(query, session)

    @pytest.mark.asyncio
    async def test_activate_invalid_passcode(
        self, user_and_expired_passcode: tuple[UserEntity, PasscodeEntity], faker: Faker
    ) -> None:
        """
        Test that the reset_passcode method raises an error when the passcode is expired.
        """
        uid = faker.uuid4()

        with pytest.raises(InvalidActivationToken):
            await self._service.activate_user(uid)

    @pytest.mark.asyncio
    async def test_activate_expired_passcode(
        self, user_and_expired_passcode: tuple[UserEntity, PasscodeEntity]
    ) -> None:
        """
        Test that the reset_passcode method raises an error when the passcode is expired.
        """
        _, passcode = user_and_expired_passcode

        with pytest.raises(InvalidActivationToken):
            await self._service.activate_user(passcode.id)


class TestServiceRequestPasswordReset(BaseTestPasscodeService):

    @pytest.fixture
    def unit_of_work(
        self, scoped_session: async_scoped_session[AsyncSession]
    ) -> PasscodeUnitOfWork:
        """
        Setup the test on the PasscodeReset instance.
        """
        return PasscodeUnitOfWork(session=Session(), db_con=DBSession(scoped_session))

    @pytest.fixture(autouse=True)
    def setup_service(self, unit_of_work: PasscodeUnitOfWork) -> None:
        """
        Setup the test on the PasscodeReset instance.
        """
        email_manager = EmailManager(url="http://localhost:3000/v3/mail/send")
        self._service = ServiceRequestPasswordReset(
            unit_of_work, email_service=email_manager
        )

    @pytest_asyncio.fixture(autouse=True)
    async def user(self, faker: Faker, user_factory: UserFactory) -> UserEntity:
        """
        Setup the test on the PasscodeReset instance.
        """
        email = faker.email()
        user = await user_factory.create_user(email=email)
        return user

    @pytest.mark.asyncio
    async def test_request_password_reset(
        self, session: AsyncSession, user: UserEntity
    ) -> None:
        """
        Test that the reset_passcode method resets the passcode.
        """
        data = RequestPasswordChangeDTO(email=user.email)  # type: ignore

        await self._service.send_reset_email(data)

        query = select(PasscodeEntity).where(PasscodeEntity.user_id == user.id)
        passcode = await resolve_query_one(query, session)
        assert passcode.category == CredChoices.RESET

    @pytest.mark.asyncio
    async def test_request_password_reset_invalid_email(self, faker: Faker) -> None:
        """
        Test that the reset_passcode method raises an error when the passcode is expired.
        """
        email = faker.email()
        data = RequestPasswordChangeDTO(email=email)

        with pytest.raises(IncorrectInput):
            await self._service.send_reset_email(data)
