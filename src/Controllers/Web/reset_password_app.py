"""
This module contains controllers for handling password reset and request
password reset functionality. It includes two blueprints: reset-password and
request_reset_password. The reset-password blueprint handles the password reset
functionality, while the request_reset_password blueprint handles the request
password reset functionality. The module also contains two classes:
ForgetPasswordController and PasswordResetController. ForgetPasswordController
handles the request password reset functionality, while PasswordResetController
handles the password reset functionality.
"""

from __future__ import annotations

from uuid import UUID

from quart import Blueprint, abort, flash, redirect, render_template, url_for
from quart.views import MethodView
from quart_wtf import QuartForm  # type: ignore
from werkzeug import Response
from wtforms import PasswordField, SubmitField  # type: ignore
from wtforms.validators import EqualTo, InputRequired, Length  # type: ignore

from src.Context.Service.Exceptions import IncorrectInput
from src.Context.Service.Exceptions.Passcode import InvalidResetToken
from src.Context.Service.Passcode import PasscodeDTO, ServicePasswordReset
from src.Context.Service.UnitOfWork.Passcode import PasscodeUnitOfWork


class ResetPasswordForm(QuartForm):
    """
    A form for resetting a password.
    """

    password = PasswordField(
        "password",
        validators=[
            InputRequired("Please enter your password."),
            Length(min=8, max=80),
        ],
        render_kw={"placeholder": "password"},
    )

    password_2 = PasswordField(
        "password_2",
        validators=[
            InputRequired("Please enter a password"),
            Length(min=8, max=30),
            EqualTo("password", message="Password is not the same"),
        ],
        render_kw={"placeholder": "confirm password"},
    )

    submit = SubmitField("Submit")


class PasswordResetController(MethodView):
    """
    Controller for resetting user password.

    Methods:
    ----
        get(token: UUID) -> tuple[str, int]:
            Get Reset Password Page

        post(token: UUID) -> Response:
            Request Password Reset

    Attributes:
    ----
        _service: ServicePasswordReset
            Service for resetting user password.
    """

    def __init__(self, service: ServicePasswordReset) -> None:
        """
        Initialize PasswordResetController.

        Parameters:
        ----
            service: ServicePasswordReset
                Service for resetting user password.
        """
        self._service = service

    async def get(self, token: UUID) -> tuple[str, int]:
        """
        Get Reset Password Page

        Parameters:
        ----
            token: UUID
                Unique identifier for password reset.

        Returns:
        ----
            tuple[template: str, http_status: int]
                Rendered template and HTTP status code.
        """
        await self._check_token(token)
        template = await render_template(
            "reset_password.html", form=ResetPasswordForm()
        )
        return template, 200

    async def post(self, token: UUID) -> Response:
        """
        Request Password Reset

        Parameters:
        ----
            token: UUID
                Unique identifier for password reset.

        Returns:
        ----
            Response
                HTTP response.
        """
        return await self._post(token)

    async def _check_token(self, token: UUID) -> None:
        """
        Get and handle response.

        Parameters:
        ----
            token: UUID
                Unique identifier for password reset.

        Returns:
        ----
            Response
                HTTP response.
        """
        try:
            await self._service.check_valid_reset_token(token)

        except InvalidResetToken:
            abort(code=404)

    async def _post(self, token: UUID) -> Response:
        """
        Post and handle response.

        Parameters:
        ----
            reset_password_dto: PasscodeDTO
                Data transfer object for resetting password.

        Returns:
        ----
            Response
                HTTP response.
        """

        try:
            response = await self._reset_password_from_data_and_redirect(token)
            return response

        except IncorrectInput as exc:
            response = await self._document_and_redirect_when_input_is_wrong(token, exc)
            return response

        except InvalidResetToken:
            abort(code=404)

    async def _reset_password_from_data_and_redirect(self, token: UUID) -> Response:
        """
        Resets the user's password using the provided token and redirects to a success page.

        Args:
            token (UUID): The token used to verify the user's identity.

        Returns:
            Response: The response object representing the success page.
        """
        reset_password_dto = await self._extract_data_from_form(token)
        await self._service.reset_user_password(reset_password_dto)
        response = await self._successful_response_handling()
        return response

    async def _extract_data_from_form(self, token: UUID) -> PasscodeDTO:
        """
        Transform form data to data transfer object.

        Parameters:
        ----
            token: UUID
                Unique identifier for password reset.

        Returns:
        ----
            PasscodeDTO
                Data transfer object for resetting password.
        """
        form = await ResetPasswordForm.create_form()
        if await form.validate_on_submit():
            return PasscodeDTO(token=token, password=form.data["password"])
        raise IncorrectInput(errors=form.errors)  # type: ignore

    async def _successful_response_handling(self) -> Response:
        """
        Handle successful response.

        Returns:
        ----
            Response
                HTTP response.
        """
        await flash(
            "Your password has been reset succesfully", category="flash-success"
        )

        return redirect(url_for("root.web.user.account_login_app.controller"))

    async def _document_and_redirect_when_input_is_wrong(
        self, token: UUID, exception: IncorrectInput
    ) -> Response:
        """
        Handle failure response.

        Parameters:
        ----
            exception: IncorrectInput
                Exception for incorrect input.

        Returns:
        ----
            Response
                HTTP response.
        """
        for key, value in exception.errors.items():
            await flash(f"{key}: {value}", category="flash-errors")
        return redirect(url_for("root.web.reset_password_app.controller", token=token))


reset_password_app = Blueprint(
    "reset_password_app", __name__, url_prefix="/edit-password/<uuid:token>"
)

reset_password_controller = PasswordResetController.as_view(
    "controller", ServicePasswordReset(PasscodeUnitOfWork())
)

reset_password_app.add_url_rule("/", view_func=reset_password_controller)
