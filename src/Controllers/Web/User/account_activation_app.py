from uuid import UUID

from quart import Blueprint, abort, flash, redirect, url_for
from quart.views import MethodView
from werkzeug.wrappers.response import Response

from src.Context.Service.Exceptions.Passcode import InvalidActivationToken
from src.Context.Service.Passcode import ServiceActivateUser
from src.Context.Service.UnitOfWork.Passcode import PasscodeUnitOfWork


class UserActivationController(MethodView):
    """
    User Activation Controller

    This controller handles the activation of user accounts.
    """

    def __init__(self, service: ServiceActivateUser) -> None:
        """
        Initializes an instance of the AccountActivationPage class.

        Args:
            service (ServiceActivateUser): The service used for user activation.
        """
        self._service = service

    async def get(self, token: UUID) -> Response:
        """
        Activate User Account.

        Parameters
        ----------
        token : UUID
            The activation token for the user account.

        Returns
        -------
        Response
            A redirect response to the login page if the user account is successfully activated.
            Otherwise, a 404 error page is displayed.
        """

        try:
            await self._service.activate_user(token)
            await flash(
                "Account activated successfully. Please login.",
                category="flash-success",
            )
            return redirect(url_for("root.web.user.account_login_app.controller"))
        except InvalidActivationToken:
            abort(404, description="Page Not Found")


account_activation_app = Blueprint(
    "account_activation_app", __name__, url_prefix="/activation/<uuid:token>"
)
user_activation_controller = UserActivationController.as_view(
    "controller", ServiceActivateUser(PasscodeUnitOfWork())
)
account_activation_app.add_url_rule("/", view_func=user_activation_controller)
