"""
This module contains the Passcode Service Layer, which is responsible for
resetting user passwords and activating user accounts. It imports the
necessary modules and classes to perform these tasks, including logging,
marshmallow, uuid, datetime, and sendgrid. It also defines abstract and
concrete classes for resetting passwords and activating users, and includes
methods for validating input, retrieving users, and changing passwords.
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from jinja2 import Template
from sendgrid.helpers.mail import From, Mail, To  # type: ignore

from src.Context.Domain.Passcode import Passcode
from src.Context.Domain.User import User
from src.Context.Service import ServiceBase
from src.Context.Service.Exceptions import IncorrectInput
from src.Context.Service.Exceptions.Passcode import (
    InvalidActivationToken,
    InvalidResetToken,
)
from src.Context.Service.UnitOfWork.Passcode import PasscodeUnitOfWork
from src.Infrastructure.Email.sendgrid import EmailManager
from src.Infrastructure.Entities.Passcode import CredChoices
from src.Infrastructure.Repositories.Utils import NoEntityFound
from src.managers import email_manager


@dataclass
class PasscodeDTO:
    """
    Data Transfer Object for storing passcode information.

    Attributes:
        token (UUID): The token associated with the passcode.
        password (str): The passcode password.
    """

    token: UUID
    password: str


@dataclass
class RequestPasswordChangeDTO:
    """
    Represents a data transfer object for requesting a password change.

    Attributes:
        email (str): The email address associated with the password change request.
    """

    email: str


class BaseServicePasscodeReset(ServiceBase):
    """
    This class provides an abstract base for resetting a user's passcode.

    It defines an abstract method `reset_user_password` that must be
    implemented by any concrete subclass.

    The `reset_user_password` method takes a `PasscodeDTO` object as input and
    returns `None`.
    """

    def __init__(self, unit_of_work: PasscodeUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    @abstractmethod
    async def reset_user_password(self, data: PasscodeDTO) -> User:
        """Not implemented yet"""


class ServicePasswordReset(BaseServicePasscodeReset):
    """
    Service for resetting user passwords.

    Methods:
    ----
        reset_user_password(data: PasscodeDTO) -> None:
            Validates the form and resets the user's password.

    Attributes:
    ----
        _user_schema: PasscodeSchema
            The schema for validating user data.
        _unit_of_work: UnitOfWork
            The unit of work for managing database transactions.
    """

    async def reset_user_password(self, data: PasscodeDTO) -> User:
        """
        Validates the form and resets the user's password.

        Parameters:
        ----
            data: PasscodeDTO
                The data containing the user's new password and reset token.

        Returns:
        ----
            None

        Raises:
        ----
            IncorrectInput:
                If the input data is invalid.
        """
        user = await self._reset_user_password(data)
        return user

    async def check_valid_reset_token(self, token: UUID) -> Passcode:
        """
        Gets the user with a valid passcode.

        Parameters:
        ----
            data: PasscodeDTO
                The data containing the user's new password and reset token.

        Returns:
        ----
            Passcode:
                The passcode object.

        Raises:
        ----
            InvalidResetToken:
                If the reset token is invalid.
        """
        try:
            passcode = await self._unit_of_work.passcode_repository.find_reset_by_uid_before_exp(  # noqa
                token
            )
        except NoEntityFound:
            raise InvalidResetToken()

        return passcode

    async def _reset_user_password(self, data: PasscodeDTO) -> User:
        """
        Resets the user's password.

        Parameters:
        ----
            data: PasscodeDTO
                The data containing the user's new password and reset token.

        Returns:
        ----
            None
        """
        user, passcode = await self._find_user_and_change_password(data)
        await self._save_to_session_and_commit(user, passcode)
        return user

    async def _find_user_and_change_password(
        self, data: PasscodeDTO
    ) -> tuple[User, Passcode]:
        """
        Resets the user's password.

        Parameters:
        ----
            data: PasscodeDTO
                The data containing the user's new password and reset token.

        Returns:
        ----
            tuple[User, Passcode]

        Raises:
        ----
            InvalidResetToken:
                If the reset token is invalid.
        """
        passcode = await self.check_valid_reset_token(data.token)
        user = await self._unit_of_work.user_repository.find_by_id(passcode.user_id)
        user.set_password(data.password)
        return user, passcode

    async def _save_to_session_and_commit(self, user: User, passcode: Passcode) -> None:
        """
        Save user to session and commit.

        Parameters:
        ----
            user: User
                The user object.
            passcode: Passcode
                The passcode object.

        Returns:
        ----
            None
        """
        await self._unit_of_work.user_repository.modify(user)
        await self._unit_of_work.passcode_repository.remove(passcode)
        await self._unit_of_work.save()


class BaseActivateUser(ServiceBase):
    """
    Abstract control user activation Service Layer.
    """

    def __init__(self, unit_of_work: PasscodeUnitOfWork) -> None:
        """
        Parameters:
        ----
            :param unit_of_work: PasscodeUnitOfWork

        Returns:
        ----
            None
        """
        self._unit_of_work = unit_of_work

    @abstractmethod
    async def activate_user(self, token: UUID) -> None:
        """Not implemented yet"""


class ServiceActivateUser(BaseActivateUser):
    """
    Service to activate a user's account using an activation token.
    """

    async def activate_user(self, token: UUID) -> None:
        """
        Activate the user's account.

        Parameters:
        ----
            token: UUID
                The activation token.

        Returns:
        ----
            None
        """
        passcode = await self._get_valid_activation_passcode_token(token)
        await self._activate_user_and_delete_token(passcode)
        await self._unit_of_work.save()

    async def _get_valid_activation_passcode_token(self, token: UUID) -> Passcode:
        """
        Get the a valid activation passcode.

        Parameters:
        ----
            token: UUID
                The activation token.

        Returns:
        ----
            Passcode
                The activation passcode.
        """
        try:
            passcode = await self._unit_of_work.passcode_repository.find_activation_by_uid_before_exp(  # noqa
                token
            )

        except NoEntityFound:
            raise InvalidActivationToken()

        return passcode

    async def _activate_user_and_delete_token(self, passcode: Passcode) -> None:
        """
        Activate user and delete token.

        Params:
        ----
            passcode: Passcode
                The activation passcode.

        Returns:
        ----
            None
        """
        user = await self._unit_of_work.user_repository.find_by_id(passcode.user_id)
        user.set_active()
        await self._unit_of_work.user_repository.modify(user)
        await self._unit_of_work.passcode_repository.remove(passcode)


class BaseServiceRequestPasswordReset(ServiceBase):
    """
    Abstract Passcode Service Layer.
    """

    def __init__(
        self,
        unit_of_work: PasscodeUnitOfWork,
        email_service: EmailManager = email_manager,
    ) -> None:
        """
        Parameters:
        ----
            :param unit_of_work: PasscodeUnitOfWork
            :param schema: ForgetPasswordSchema
            :param email_service: EmailManager

        Returns:
        ----
            None
        """
        self._unit_of_work = unit_of_work
        self._email_service = email_service

    @abstractmethod
    async def send_reset_email(self, email_dto: RequestPasswordChangeDTO) -> None:
        """Not implemented yet"""


class ServiceRequestPasswordReset(BaseServiceRequestPasswordReset):
    """
    Service class for handling password reset requests.

    Methods:
    ----
        send_reset_email(email_dto: RequestPasswordChangeDTO) -> None:
            Create a reset passcode and send it to the user's email.

        _validate_input_and_get_user_account(email_dto: RequestPasswordChangeDTO) -> User:  # noqa
            Validate the input and get the user account.

        _validate_form(email_dto: RequestPasswordChangeDTO) -> None:
            Validate the input form.

        _get_user_account(email: str) -> User:
            Get the user account by email.

        _create_reset_token(user: User) -> Passcode:
            Create a reset passcode.

        _invalidate_other_requests_if_exists(user: User) -> None:
            Invalidate other requests if they exist.

        _remove_old_passcode(user: User) -> None:
            Remove old passcode.

        _generate_reset_passcode(user: User) -> Passcode:
            Generate a reset passcode.

        _send_passcode_by_email(user: User, passcode: Passcode) -> None:
            Send the reset passcode to the user's email.

        _render_html(user: User, passcode: Passcode) -> str:
            Render the HTML template.

        _create_email(user: User, html_body: str) -> Mail:
            Create the email.
    """

    async def send_reset_email(self, email_dto: RequestPasswordChangeDTO) -> None:
        """
        Create an reset passcode.

        Parameters:
        ----
            email_dto: RequestPasswordChangeDTO

        Returns:
        ----
            None
        """
        user = await self._validate_input_and_get_user_account(email_dto)
        passcode = await self._create_reset_token(user)
        await self._unit_of_work.save()
        await self._send_passcode_by_email(user, passcode)

    async def _validate_input_and_get_user_account(
        self, data: RequestPasswordChangeDTO
    ) -> User:
        """
        Validate the input.

        Parameters:
        ----
            data: RequestPasswordChangeDTO

        Returns:
        ----
            None
        """
        user = await self._get_user_account(data.email)
        return user

    async def _get_user_account(self, email: str) -> User:
        """
        Get the user by email.

        Parameters:
        ----
            email: str

        Returns:
        ----
            User
        """
        try:
            user = await self._unit_of_work.user_repository.find_by_email(email)

        except NoEntityFound:
            raise IncorrectInput({"email": "Email not found"})

        return user

    async def _create_reset_token(self, user: User) -> Passcode:
        """
        Create a reset passcode.

        Parameters:
        ----
            user: User

        Returns:
        ----
            None
        """
        await self._invalidate_other_requests_if_exists(user)
        passcode = self._generate_reset_passcode(user)
        self._unit_of_work.passcode_repository.add(passcode)
        return passcode

    async def _invalidate_other_requests_if_exists(self, user: User) -> None:
        """
        Delete token if exists.

        Parameters:
        ----
            :param user: User

        Returns:
        ----
            None
        """
        try:
            await self._remove_old_passcode(user)

        except NoEntityFound:
            logging.info("No reset token found, creating a new one")

    async def _remove_old_passcode(self, user: User) -> None:
        """
        Remove old passcode.

        Parameters:
        ----
            user: User

        Returns:
        ----
            None
        """
        passcode = (
            await self._unit_of_work.passcode_repository.find_reset_by_user(  # noqa
                user
            )
        )
        await self._unit_of_work.passcode_repository.remove(passcode)

    def _generate_reset_passcode(self, user: User) -> Passcode:
        """
        Generate a passcode.

        Parameters:
        ----
            user: User

        Returns:
        ----
            None
        """
        expiration = datetime.now(UTC) + timedelta(minutes=15)
        passcode = Passcode(
            id=uuid4(),
            user_id=user.id,
            category=CredChoices.RESET.name,  # type: ignore
            expiration=expiration,
        )
        return passcode

    async def _send_passcode_by_email(self, user: User, passcode: Passcode) -> None:
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
        html_body = await self._render_html(user, passcode)
        email = self._create_email(user, html_body)
        await self._email_service.send_email(email)

    async def _render_html(self, user: User, passcode: Passcode) -> str:
        """
        Render the html template.

        Params:
        -----
            user: User
            passcode: Passcode

        Returns:
        -----
            str
        """
        template = Template("Email", enable_async=True, autoescape=True)
        email = await template.render_async(
            user=user, token=passcode.id, category="Reset"
        )

        return email

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
        return Mail(
            from_email=From("no-reply@livedisplaced.com"),
            to_emails=To(user.email),
            subject="Reset Email",
            html_content=html_body,
        )
