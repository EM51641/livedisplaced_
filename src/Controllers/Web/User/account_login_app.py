from quart import Blueprint, flash, redirect, render_template, url_for
from quart.views import MethodView
from quart_wtf import QuartForm  # type: ignore
from werkzeug import Response
from wtforms import PasswordField, StringField, SubmitField  # type: ignore
from wtforms.validators import Email, InputRequired  # type: ignore

from src.Context.Service.Exceptions import IncorrectInput
from src.Context.Service.Exceptions.User import (
    UserAccountNotActivated,
    UserAccountNotFound,
)
from src.Context.Service.UnitOfWork.User import UserUnitOfWork
from src.Context.Service.User import ServiceLogin, UserLoginDTO
from src.Middlewares.user_middleware import only_logged_out


class LoginForm(QuartForm):
    """
    A form for user login.

    Attributes:
    -----------
    email : StringField
        The user's email address.
    password : PasswordField
        The user's password.
    submit : SubmitField
        A button to submit the form.
    """

    email = StringField(
        "email",
        validators=[
            InputRequired("Please enter your email address."),
            Email("This field requires a valid email address"),
        ],
    )
    password = PasswordField(
        "password", validators=[InputRequired("Please enter a password")]
    )
    submit = SubmitField("Submit")


class UserLoginController(MethodView):
    """
    User Login Controller
    """

    decorators = [only_logged_out]

    def __init__(self, service: ServiceLogin) -> None:
        self._service = service

    async def get(self) -> tuple[str, int]:
        """
        Login User get.

        Parameters:
        ----
            None

        Returns:
        ----
            tuple[template: str, http_status: int]
        """
        form = LoginForm()
        template = await render_template("login.html", form=form)
        return template, 200

    async def post(self) -> Response:
        """
        Login User post.

        Parameters:
        ----
            None

        Returns:
        ----
            Response
        """
        try:
            login_dto = await self._validate_post_form_and_get_dto()
            response = await self._login_user(login_dto)
        except IncorrectInput as exc:
            response = await self._redirect_to_login_if_data_not_valid(exc)
        return response

    async def _validate_post_form_and_get_dto(self) -> UserLoginDTO:
        """
        Validate the form and get the dto

        Parameters:
        ----
            None

        Returns:
        ----
            None
        """
        form = await LoginForm.create_form()

        if await form.validate_on_submit():
            registration_dto = self._form_to_dto(form)  # type: ignore
            return registration_dto

        raise IncorrectInput(errors=form.errors)  # type: ignore

    async def _login_user(self, login_dto: UserLoginDTO) -> Response:
        """
        Login the user

        Parameters:
        ----
            None

        Returns:
        ----
            None
        """
        try:
            await self._service.login(login_dto)
            response = redirect(url_for("root.web.overview_app.controller"))
        except UserAccountNotActivated:
            response = await self._response_user_account_not_activate()
        except UserAccountNotFound:
            response = await self._response_user_account_not_found()
        return response

    async def _redirect_to_login_if_data_not_valid(
        self, exc: IncorrectInput
    ) -> Response:
        """
        Redirect to the login page

        Parameters:
        ----
            None

        Returns:
        ----
            None
        """
        for key, value in exc.errors.items():
            await flash(f"{key}: {value}", category="flash-errors")
        return redirect(url_for("root.web.user.account_login_app.controller"))

    def _form_to_dto(self, form: LoginForm) -> UserLoginDTO:
        """
        Convert the form to a dto

        Parameters:
        ----
            None

        Returns:
        ----
            None
        """
        return UserLoginDTO(
            email=form.email.data,  # type: ignore
            password=form.password.data,  # type: ignore
        )

    async def _response_user_account_not_activate(self) -> Response:
        """
        Handle the response when the user account is not activated

        Parameters:
        ----
            None

        Returns:
        ----
            None
        """
        await flash(
            "Your account is not activated yet. Please check your email.",
            category="flash-errors",
        )
        return redirect(url_for("root.web.user.account_login_app.controller"))

    async def _response_user_account_not_found(self) -> Response:
        """
        Handle the response when the user account is not found

        Parameters:
        ----
            None

        Returns:
        ----
            None
        """
        await flash("Incorrect email and/or password", category="flash-errors")
        return redirect(url_for("root.web.user.account_login_app.controller"))


account_login_app = Blueprint("account_login_app", __name__, url_prefix="/login")

account_login_controller = UserLoginController.as_view(
    "controller", ServiceLogin(UserUnitOfWork())
)
account_login_app.add_url_rule("/", view_func=account_login_controller)
