"""
The User and Account models are all here
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jinja2 import Template
from quart import url_for
from quart_auth import current_user
from sendgrid.helpers.mail import From, Mail, To  # type: ignore

from src.Context.Domain.Passcode import Passcode
from src.Context.Domain.TermsOfUse import SignedTermsOfUse
from src.Context.Domain.User import User
from src.Context.Service import ServiceBase
from src.Context.Service.Exceptions.User import (
    EmailAlreadyUsed,
    IncorrectPassword,
    UserAccountNotActivated,
    UserAccountNotFound,
)
from src.Context.Service.UnitOfWork.Passcode import PasscodeUnitOfWork
from src.Context.Service.UnitOfWork.User import UserUnitOfWork
from src.Context.Service.Utils.login_user import login_user
from src.Infrastructure.Email.sendgrid import EmailManager
from src.Infrastructure.Entities.Passcode import CredChoices
from src.Infrastructure.Repositories.Utils import NoEntityFound
from src.managers import email_manager


@dataclass
class UserLoginDTO:
    """
    Data Container to be user by the controller to create
    a user in the standard way
    """

    email: str
    password: str


@dataclass
class ResetPasswordDTO:
    """
    Data Container to be user by the controller to create
    a user in the standard way
    """

    old_password: str
    new_password: str


class BaseServiceLogin(ServiceBase[UserUnitOfWork]):
    def __init__(self, unit_of_work: UserUnitOfWork) -> None:
        """
        Parameters:
        ----
            :param user_repository: sUserRepositoryPattern: User repository.

        Returns:
        ----
            None
        """

        super().__init__(unit_of_work)

    @abstractmethod
    async def login(self, data: UserLoginDTO) -> str:
        """Not implemented yet"""


class ServiceLogin(BaseServiceLogin):
    """
    Service for standard login
    """

    async def login(self, data: UserLoginDTO) -> str:
        """
        Login user.

        Parameters:
        ----
            data: UserLoginDTO: Data to login user.

        Returns:
        ----
            None
        """
        try:
            user = await self._unit_of_work.user_repository.find_by_email(
                email=data.email
            )
            return await self._login(user, data.password)
        except NoEntityFound:
            raise UserAccountNotFound()

    async def _login(self, user: User, password: str) -> str:
        """
        Login user.

        Parameters:
        ----
            user: User: User to login.

        Returns:
        ----
            None
        """

        if user and user.check_password(password):
            return self._check_if_account_activated_and_login(user)

        else:
            raise UserAccountNotFound()

    def _check_if_account_activated_and_login(self, user: User) -> str:
        """
        Check if the account is activated and login the user

        Parameters:
        ----
            user: User: User to login.

        Returns:
        ----
            None
        """
        if user.is_active:
            login_user(user)
            return "Logged in successfully."
        else:
            raise UserAccountNotActivated()


class BaseServiceSettingsAccount(ServiceBase[UserUnitOfWork]):
    def __init__(self, unit_of_work: UserUnitOfWork) -> None:
        super().__init__(unit_of_work)

    async def _get_user(self) -> User:
        """
        Get the current user.

        Returns:
        ----
            User: The current user.
        """
        user = await current_user.load_user()  # type: ignore
        return user


class BaseServiceDeleteAccount(BaseServiceSettingsAccount):
    @abstractmethod
    async def delete_user_account(self) -> str:
        """Not implemented yet"""


class ServiceDeleteAccount(BaseServiceDeleteAccount):
    """
    Attributes:
    ----
        unit_of_work: UserUnitOfWork

    Returns:
    ----
        None
    """

    async def delete_user_account(self) -> str:
        """
        Delete user account.

        Parameters:
        ----
            None

        Returns:
        ----
            None
        """
        user = await self._get_user()
        await self._unit_of_work.user_repository.remove(user)
        await self._unit_of_work.save()
        return "Account deleted successfully."


class BaseServiceUpdateAccountPassword(BaseServiceSettingsAccount):
    @abstractmethod
    async def update_password(self, data: ResetPasswordDTO) -> str:
        """Not implemented yet"""


class ServiceUpdateAccountPassword(BaseServiceUpdateAccountPassword):
    def __init__(self, unit_of_work: UserUnitOfWork) -> None:
        super().__init__(unit_of_work)

    async def update_password(self, data: ResetPasswordDTO) -> str:
        """
        Update user password.

        Parameters:
        ----
            password_dto: UserChangePasswordSchema

        Returns:
        ----
            None
        """
        user = await self._get_user()
        self._validate_old_password(user, data)
        await self._unit_of_work.user_repository.modify(user)
        await self._unit_of_work.save()
        return "Password updated successfully."

    def _validate_old_password(
        self, user: User, password_dto: ResetPasswordDTO
    ) -> None:
        """
        Validates the old password provided by the user.

        Args:
            password_dto (ResetPasswordDTO): The DTO containing the old password.

        Raises:
            IncorrectInput: If the old password is incorrect.
        """
        is_password_correct = user.check_password(password_dto.old_password)
        if not is_password_correct:
            raise IncorrectPassword()


@dataclass
class UserRegistrationDTO:
    """
    Data Container to be user by the controller to create
    a user in the standard way
    """

    first_name: str
    last_name: str
    email: str
    password: str


class BaseServiceRegistrationUser(ServiceBase[PasscodeUnitOfWork]):
    """
    A service that runs on a two repository to handle the
    creation of the user.
    """

    @abstractmethod
    async def register_user(self, data: UserRegistrationDTO) -> None:
        """Not implemented yet"""


class ServiceRegistrationUser(BaseServiceRegistrationUser):
    """
    Service class for registering a user.
    """

    def __init__(
        self,
        unit_of_work: PasscodeUnitOfWork,
        email_service: EmailManager = email_manager,
    ) -> None:
        """
        Constructor for ServiceRegistrationUser.

        Parameters:
        ----
            :param unit_of_work: PasscodeUnitOfWork
            :param schema: UserRegistrationSchema
            :param email_service: EmailManager
        """

        super().__init__(unit_of_work)
        self._email_service = email_service

    async def register_user(self, data: UserRegistrationDTO) -> None:
        """
        Add a user.

        Parameters:
        ----
            :param data: UserRegistrationDTO

        Returns:
        ----
            User
        """
        await self._validate_data(data)
        user = self._generate_user(data)

        terms = await self._generate_terms_of_use_signature(user)

        passcode = self._generate_activation_passcode(user)

        await self._save_and_send_activation_email(user, terms, passcode)

    async def _validate_data(self, data: UserRegistrationDTO):
        """
        Validate the data.

        Parameters:
        ----
            data: UserRegistrationDTO

        Returns:
        ----
            None
        """
        await self._validate_constraints(data)

    async def _validate_constraints(self, data: UserRegistrationDTO):
        """
        Validate the constraints.

        Parameters:
        ----
            :param data: UserRegistrationDTO

        """
        try:
            await self._unit_of_work.user_repository.find_by_email(data.email)
            raise EmailAlreadyUsed()
        except NoEntityFound:
            pass

    def _generate_user(self, data: UserRegistrationDTO) -> User:
        """
        Generate a user.

        Parameters:
        ----
            :param data: UserRegistrationDTO

        Returns:
        ----
            User
        """
        user = User(
            id=uuid4(),
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password=None,
            is_active=False,
            created=datetime.now(UTC),
        )

        user.set_password(data.password)

        return user

    def _generate_activation_passcode(self, user: User) -> Passcode:
        """
        Generate a passcode.

        Parameters:
        ----
            :param user: User

        Returns:
        ----
            Passcode
        """
        expiration = datetime.now(UTC) + timedelta(days=1)

        passcode = Passcode(
            id=uuid4(),
            user_id=user.id,
            category=CredChoices.ACTIVATION,  # type: ignore
            expiration=expiration,
        )
        return passcode

    async def _generate_terms_of_use_signature(self, user: User) -> SignedTermsOfUse:
        """
        Save the terms of use.

        Parameters:
        ----
            :param user: User

        Returns:
        ----
            None
        """
        term = await self._unit_of_work.terms_of_use_repository.find_latest_version()
        signed_term = SignedTermsOfUse(
            id=uuid4(), user_id=user.id, termsofuse_id=term.id, signed=datetime.now(UTC)
        )
        return signed_term

    async def _save_and_send_activation_email(
        self, user: User, signed_terms: SignedTermsOfUse, passcode: Passcode
    ) -> None:
        """
        Save user and passcode domain and send activation email.

        Parameters:
        ----
            :param user: User
            :param passcode: Passcode

        Returns:
        ----
            None
        """
        self._unit_of_work.user_repository.add(user)
        await self._unit_of_work.flush()
        self._unit_of_work.signed_terms_of_use_repository.add(signed_terms)
        self._unit_of_work.passcode_repository.add(passcode)
        await self._unit_of_work.save()
        await self._send_activation_email(user, passcode)

    async def _send_activation_email(self, user: User, passcode: Passcode) -> None:
        """
        Send activation email.

        Parameters:
        ----
            :param user: User
            :param passcode: Passcode

        Returns:
        ----
            None
        """
        html_body = await self._render_html(user, passcode)
        email = self._create_email(user, html_body)
        await self._email_service.send_email(email)

    async def _render_html(self, user: User, passcode: Passcode) -> str:
        """
        Handle the sending of the activation email.

        Params:
        -----
            user: User
            passcode: Passcode

        Returns:
        -----
            None
        """
        with open("front/activate_account_email.html") as file_:
            template = Template(file_.read(), enable_async=True, autoescape=True)

        body = await template.render_async(
            user=user,
            category="Activation",
            link=url_for(
                "root.web.user.account_activation_app.controller",
                token=passcode.id,
                _external=True,
            ),
        )

        return body

    def _create_email(self, user: User, html_body: str) -> Mail:
        """
        Create the email.

        Params:
        -----
            user: User
            html_body: str

        Returns:
        -----
            Mail
        """

        email = Mail(
            from_email=From("no-reply@livedisplaced.com"),
            to_emails=To(user.email),
            subject="Activation Email",
            html_content=html_body,
        )
        return email
