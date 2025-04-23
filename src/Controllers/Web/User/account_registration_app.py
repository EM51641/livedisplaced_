from quart import Blueprint, flash, redirect, render_template, url_for
from quart.views import MethodView
from quart_wtf import QuartForm  # type: ignore
from werkzeug import Response
from wtforms import (  # type: ignore
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (  # type: ignore
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
)

from src.Context.Service.Exceptions import IncorrectInput
from src.Context.Service.Exceptions.User import EmailAlreadyUsed
from src.Context.Service.UnitOfWork.Passcode import PasscodeUnitOfWork
from src.Context.Service.User import ServiceRegistrationUser, UserRegistrationDTO
from src.Middlewares.user_middleware import only_logged_out


class RegistrationForm(QuartForm):
    """
    A form for user registration.

    Attributes:
    -----------
    first_name : StringField
        The user's first name.
    last_name : StringField
        The user's last name.
    email : StringField
        The user's email address.
    password : PasswordField
        The user's password.
    password_2 : PasswordField
        The user's password confirmation.
    agree : BooleanField
        A checkbox indicating whether the user agrees
        to the terms and conditions.
    submit : SubmitField
        A button to submit the form.
    """

    first_name = StringField(
        "first_name",
        validators=[
            InputRequired("Please enter your first name."),
            Length(2, 50, "This field requires a valid first name"),
        ],
        render_kw={"placeholder": "first name"},
    )
    last_name = StringField(
        "last_name",
        validators=[
            InputRequired("Please enter your last name."),
            Length(2, 50, "This field requires a valid last name"),
        ],
        render_kw={"placeholder": "last name"},
    )
    email = StringField(
        "email",
        validators=[
            InputRequired("Please enter your email address."),
            Email("This field requires a valid email address"),
        ],
        render_kw={"placeholder": "email"},
    )

    password = PasswordField(
        "password",
        validators=[
            InputRequired("Please enter a password"),
            Length(min=8, max=30),
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

    agree = BooleanField(
        "agree",
        validators=[
            DataRequired(),
        ],
    )

    submit = SubmitField("Register")


class UserRegistrationController(MethodView):
    """
    User Registration Controller

    This controller handles the registration of users. It provides methods for rendering the registration form,
    validating and processing the form data, and registering the user with the provided data.
    """

    decorators = [only_logged_out]

    def __init__(self, service: ServiceRegistrationUser) -> None:
        self._service = service

    async def get(self) -> tuple[str, int]:
        """
        Register User

        Parameters:
        ----
            None

        Returns:
        ----
            tuple[template: str, http_status: int]

        This method handles the GET request for the registration page. It renders the registration form template
        and returns it along with the HTTP status code 200.
        """

        form = RegistrationForm()
        template = await render_template("register.html", form=form)
        return template, 200

    async def post(self) -> Response:
        """
        Register User

        Parameters:
        ----
            None

        Returns:
        ----
            Union[Response, str]

        This method handles the POST request for user registration. It validates the form data, converts it to a DTO,
        and registers the user with the provided data. If the registration is successful, it redirects the user to the
        login page. If there are validation errors, it redirects the user back to the registration page with the
        appropriate error messages.
        """
        response = await self._register_user()
        return response

    async def _register_user(self) -> Response:
        """
        Registers a user with the provided registration data.

        Args:
            registration_dto (UserRegistrationDTO): The data transfer object containing the user's registration data.

        Returns:
            Response: The redirect response with the appropriate status code.

        This method registers a user with the provided registration data. If the registration is successful, it displays
        a flash message indicating that the activation email has been sent successfully and redirects the user to the
        login page. If the email is already in use, it displays a flash message indicating that the email is already in
        use and redirects the user to the login page. If there are validation errors, it displays flash messages for
        each validation error and redirects the user to the login page.
        """

        try:
            registration_dto = await self._validate_post_form_and_get_dto()
            await self._service.register_user(registration_dto)  # type: ignore
            response = await self._post_success_response_handling()

        except EmailAlreadyUsed:
            response = await self._post_email_already_used_response_handling()

        except IncorrectInput as e:
            response = await self._post_form_failure_response_handling(e)
        return response

    async def _validate_post_form_and_get_dto(self) -> UserRegistrationDTO | None:
        """
        Validate the form and get the dto

        Parameters:
        ----
            None

        Returns:
        ----
            None

        This method validates the POST form data and converts it to a UserRegistrationDTO object. If the form data is
        valid, it returns the DTO object. Otherwise, it returns None.
        """

        form = await RegistrationForm.create_form()
        if await form.validate_on_submit():
            registration_dto = self._form_to_dto(form)  # type: ignore
            return registration_dto
        raise IncorrectInput(form.errors)  # type: ignore

    def _form_to_dto(self, form: RegistrationForm) -> UserRegistrationDTO:
        """
        Convert the form to a dto

        Parameters:
        ----
            None

        Returns:
        ----
            None

        This method converts the RegistrationForm object to a UserRegistrationDTO object by extracting the relevant
        data from the form fields.
        """

        return UserRegistrationDTO(
            first_name=form.first_name.data,  # type: ignore
            last_name=form.last_name.data,  # type: ignore
            email=form.email.data,  # type: ignore
            password=form.password.data,  # type: ignore
        )

    async def _post_success_response_handling(self) -> Response:
        """
        Handles the success response after registering a user.

        Displays a flash message indicating that the activation email has been sent successfully,
        and redirects the user to the login page.

        Returns:
            Response: The redirect response with status code 201.

        This method handles the success response after registering a user. It displays a flash message indicating that
        the activation email has been sent successfully and redirects the user to the login page with the HTTP status
        code 302.
        """

        await flash(
            "An activation email should be sent to your email address. Please check your inbox.",
            category="flash-success",
        )
        return redirect(url_for("root.web.user.account_login_app.controller"))

    async def _post_email_already_used_response_handling(self) -> Response:
        """
        Handles the failure response after registering a user.

        Displays flash messages for each validation error and redirects the user to the login page.
        """
        await flash("This email is already in use.", category="flash-errors")
        return redirect(url_for("root.web.user.account_registration_app.controller"))

    async def _post_form_failure_response_handling(
        self, exception: IncorrectInput
    ) -> Response:
        """
        Handles the failure response after registering a user.

        Displays flash messages for each validation error and redirects the user to the login page.

        Args:
            exception (IncorrectInput): The exception object containing the validation errors.

        Returns:
            Response: The redirect response with status code 404.

        This method handles the failure response after registering a user. It displays flash messages for each
        validation error and redirects the user to the login page with the HTTP status code 404.
        """

        for key, value in exception.errors.items():
            await flash(f"{key}: {value}", category="flash-errors")
        return redirect(url_for("root.web.user.account_registration_app.controller"))


account_registration_app = Blueprint(
    "account_registration_app", __name__, url_prefix="/register"
)

account_registration_controller = UserRegistrationController.as_view(
    "controller", ServiceRegistrationUser(PasscodeUnitOfWork())
)

account_registration_app.add_url_rule("/", view_func=account_registration_controller)
