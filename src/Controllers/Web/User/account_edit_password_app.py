from quart import Blueprint, flash, redirect, render_template, url_for
from quart.views import MethodView
from quart_auth import login_required
from quart_wtf import QuartForm  # type: ignore
from werkzeug import Response
from wtforms import PasswordField, SubmitField  # type: ignore
from wtforms.validators import EqualTo, InputRequired, Length  # type: ignore

from src.Context.Service.Exceptions import IncorrectInput
from src.Context.Service.UnitOfWork.User import UserUnitOfWork
from src.Context.Service.User import ResetPasswordDTO, ServiceUpdateAccountPassword


class EditPasswordForm(QuartForm):
    """
    A form for changing the user's account password.

    Attributes:
    -----------
    old_password : PasswordField
        The user's current password.
    new_password : PasswordField
        The user's new password.
    new_password_2 : PasswordField
        The user's new password confirmation.
    submit : SubmitField
        A button to submit the form.
    """

    current_password = PasswordField(
        "old_password",
        validators=[
            InputRequired("Please enter your current password"),
            Length(min=8, max=30),
        ],
        render_kw={"placeholder": "old password"},
    )

    new_password = PasswordField(
        "new_password",
        validators=[
            InputRequired("Please enter a password"),
            Length(min=8, max=30),
        ],
        render_kw={"placeholder": "new password"},
    )

    new_password_2 = PasswordField(
        "new_password_2",
        validators=[
            InputRequired("Please enter a password"),
            Length(min=8, max=30),
            EqualTo("new_password", message="Password is not the same"),
        ],
        render_kw={"placeholder": "confirm password"},
    )

    submit = SubmitField("Submit")


class EditPasswordController(MethodView):
    """
    Controller for updating the user's password.

    Attributes:
        decorators (list): List of decorators applied to the controller methods.

    Args:
        service (ServiceUpdateAccountPassword): The service responsible for updating the account password.

    Methods:
        get: Handle GET request for updating the password.
        post: Handle POST request for updating the password.
        _validate_and_transform_to_dto: Validates the form data and transforms it into a ResetPasswordDTO object.
        _transform_form_to_dto: Transforms the form data into a ResetPasswordDTO object.
    """

    decorators = [login_required]

    def __init__(self, service: ServiceUpdateAccountPassword) -> None:
        self._service = service

    async def get(self) -> tuple[str, int]:
        """
        Handle GET request for updating the password.

        Returns:
            tuple[str, int]: The template and HTTP status code.
        """
        form = EditPasswordForm()
        template = await render_template("update_password.html", form=form)
        return template, 200

    async def post(self) -> Response:
        """
        Handle POST request for updating the password.

        Returns:
            Response: The HTTP response.
        """
        try:
            data = await self._validate_and_transform_to_dto()
            response = await self._update_password_and_redirect(data)
            return response
        except IncorrectInput as exc:
            response = await self._generate_response_given_form_failure(exc)
            return response

    async def _validate_and_transform_to_dto(self) -> ResetPasswordDTO:
        """
        Validates the form data and transforms it into a ResetPasswordDTO object.

        Returns:
            ResetPasswordDTO:
                The ResetPasswordDTO object if the form data is valid.
        """
        form = await EditPasswordForm.create_form()
        if await form.validate_on_submit():
            return self._transform_form_to_dto(form)  # type: ignore
        raise IncorrectInput(errors=form.errors)  # type: ignore

    def _transform_form_to_dto(self, form: EditPasswordForm) -> ResetPasswordDTO:
        """
        Transforms the form data into a ResetPasswordDTO object.

        Args:
            form (EditPasswordForm): The form containing the password data.

        Returns:
            ResetPasswordDTO: The ResetPasswordDTO object.
        """
        return ResetPasswordDTO(
            old_password=form.current_password.data,  # type: ignore
            new_password=form.new_password.data,  # type: ignore
        )

    async def _update_password_and_redirect(self, data: ResetPasswordDTO) -> Response:
        """
        Update the user's password and redirect to the login page.

        Args:
            data (ResetPasswordDTO):
                The user's password data.

        Returns:
            Response:
                The HTTP response.
        """
        await self._service.update_password(data)
        await flash("Password updated successfully.", category="flash-success")
        return redirect(url_for("root.web.user.account_settings_app.controller"))

    async def _generate_response_given_form_failure(
        self, exc: IncorrectInput
    ) -> Response:
        """
        Handle form failure.

        Returns:
            Response: The HTTP response.
        """
        for key, value in exc.errors.items():
            await flash(f"{key}: {value}", category="flash-errors")

        return redirect(url_for("root.web.user.account_settings_app.controller"))


account_edit_password_app = Blueprint(
    "account_edit_password_app", __name__, url_prefix="/edit-password"
)
account_edit_password_controller = EditPasswordController.as_view(
    "controller", ServiceUpdateAccountPassword(UserUnitOfWork())
)

account_edit_password_app.add_url_rule("/", view_func=account_edit_password_controller)
