"""
This module contains the controller for deleting the user's account.
"""

from quart import Blueprint, flash, redirect, url_for
from quart.views import MethodView
from quart_auth import login_required, logout_user
from quart_wtf import QuartForm  # type: ignore
from werkzeug import Response
from wtforms import SubmitField  # type: ignore

from src.Context.Service.UnitOfWork.User import UserUnitOfWork
from src.Context.Service.User import ServiceDeleteAccount


class DeleteAccountForm(QuartForm):
    """
    A form for deleting the user's account.

    Attributes:
    -----------
    submit : SubmitField
        A button to submit the form.
    """

    submit = SubmitField("Delete Account")


class DeleteController(MethodView):
    """
    User Settings Controller

    This controller handles the deletion of user accounts.

    Attributes:
    -----------
    decorators : list
        A list of decorators to apply to the controller.

    Methods:
    --------
    post() -> tuple[str, int]:
        Process the POST request to delete the user account.

    get() -> tuple[str, int]:
        Get User Settings.
    """

    decorators = [login_required]

    def __init__(self, service: ServiceDeleteAccount) -> None:
        self._service = service

    async def post(self) -> Response:
        """
        Process the POST request to delete the user account.

        Parameters:
        ----
        None

        Returns:
        ----
        tuple[template: str, http_status: int]
            The rendered template and the HTTP status code.
        """
        form = await DeleteAccountForm.create_form()
        if await form.validate_on_submit():
            await self._service.delete_user_account()
            logout_user()
            await flash("Account deleted successfully.", category="flash-success")
            return redirect(url_for("root.web.user.account_login_app.controller"))
        return redirect(url_for("root.user.settings_app.controller"))


account_deletion_app = Blueprint("account_deletion_app", __name__, url_prefix="/delete")

account_deletion_controller = DeleteController.as_view(
    "controller", ServiceDeleteAccount(UserUnitOfWork())
)
account_deletion_app.add_url_rule("/", view_func=account_deletion_controller)
