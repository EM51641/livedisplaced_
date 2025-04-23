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

from quart import Blueprint, flash, redirect, render_template, url_for
from quart.views import MethodView
from quart_wtf import QuartForm  # type: ignore
from werkzeug import Response
from wtforms import EmailField, SubmitField  # type: ignore
from wtforms.validators import Email, InputRequired  # type: ignore

from src.Context.Service.Exceptions import IncorrectInput
from src.Context.Service.Passcode import (
    RequestPasswordChangeDTO,
    ServiceRequestPasswordReset,
)
from src.Context.Service.UnitOfWork.Passcode import PasscodeUnitOfWork
from src.Infrastructure.Email.sendgrid import EmailManager


class ForgetPasswordForm(QuartForm):
    """
    A form for submitting an email address.
    """

    email = EmailField(
        "email",
        validators=[
            InputRequired("Please enter your email address."),
            Email("This field requires a valid email address"),
        ],
        render_kw={"placeholder": "email"},
    )
    submit = SubmitField("Submit")


class ForgetPasswordController(MethodView):
    """
    A controller class for handling forget password requests.

    Methods:
    ----
    __init__(self, service: ServiceRequestPasswordReset) -> None:
        Constructor for ForgetPasswordController class.

    async def get(self) -> tuple[str, int]:
        Get Reset Password Page

    async def post(self) -> Response:
        Request Password Reset

    def _transform_form_to_dto(self) -> "RequestPasswordChangeDTO":
        Transform form data to DTO.

    def _successful_response_handling(self) -> Response:
        Handle successful response.

    def _failure_response_handling(
        self, exception: IncorrectInput
    ) -> Response:
        Handle failure response.
    """

    def __init__(self, service: ServiceRequestPasswordReset) -> None:
        """
        Constructor for ForgetPasswordController class.

        Parameters:
        ----
        service: ServiceRequestPasswordReset
            An instance of ServiceRequestPasswordReset class.
        """
        self._service = service

    async def get(self) -> tuple[str, int]:
        """
        Get Reset Password Page

        Parameters:
        ----
            None

        Returns:
        ----
            tuple[template: str, http_status: int]
                A tuple containing the template and HTTP status code.
        """
        form = await ForgetPasswordForm.create_form()
        template = await render_template("password_lost_request.html", form=form)
        return template, 200

    async def post(self) -> Response:
        """
        Request Password Reset

        This method handles the POST request for password reset. It extracts the form data,
        checks if the email DTO is valid, and then calls the _reset_password method to reset the password.

        Parameters:
        ----
        None

        Returns:
        ----
        Response
            A response object.
        """
        await self._reset_password()
        return redirect(url_for("root.web.forget_password_app.controller"))

    async def _reset_password(self) -> None:
        """
        Resets the password for the given email address.

        Args:
            email_dto (RequestPasswordChangeDTO): The DTO containing the email address.

        Returns:
            Response: The response object indicating the success or failure of the password reset.

        Raises:
            IncorrectInput: If the input is incorrect.
        """
        try:
            await self._extract_form_and_send_email()

        except IncorrectInput as e:
            await self._failure_response_handling(e)

    async def _extract_form_and_send_email(self) -> None:
        """
        Send reset email and redirect.

        This method sends a reset email and redirects to the forget password page.

        Parameters:
        ----
        None

        Returns:
        ----
        Response
            A response object.
        """
        email_dto = await self._extract_form_data()
        await self._service.send_reset_email(email_dto)
        await self._successful_response_handling()

    async def _failure_response_handling(self, exception: IncorrectInput) -> None:
        """
        Handle failure response.

        Parameters:
        ----
        exception: IncorrectInput
            An instance of IncorrectInput class.

        Returns:
        ----
        Response
            A response object.
        """
        for key, value in exception.errors.items():
            await flash(f"{key}: {value}", category="flash-errors")

    async def _extract_form_data(self) -> RequestPasswordChangeDTO:
        """
        Transform form data to DTO.

        This method extracts data from a form and transforms it into a RequestPasswordChangeDTO object.

        Parameters:
        ----
        None

        Returns:
        ----
        RequestPasswordChangeDTO | None
            An instance of RequestPasswordChangeDTO class if the form data is valid, otherwise None.
        """
        form = await ForgetPasswordForm.create_form()
        if await form.validate_on_submit():
            return RequestPasswordChangeDTO(email=form.data["email"])  # type: ignore
        raise IncorrectInput(errors=form.errors)  # type: ignore

    async def _successful_response_handling(self) -> None:
        """
        Handle successful response.

        Parameters:
        ----
        None

        Returns:
        ----
        Response
            A response object.
        """
        await flash(
            "An email to reset your password will be sent to you shortly",
            category="flash-success",
        )


forget_password_app = Blueprint(
    "forget_password_app", __name__, url_prefix="/forget-password"
)


forget_password_controller = ForgetPasswordController.as_view(
    "controller",
    ServiceRequestPasswordReset(PasscodeUnitOfWork(), EmailManager()),
)
forget_password_app.add_url_rule("/", view_func=forget_password_controller)
