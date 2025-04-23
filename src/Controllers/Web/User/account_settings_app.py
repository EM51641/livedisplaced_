from __future__ import annotations

from quart import Blueprint, render_template
from quart.views import MethodView
from quart_auth import login_required

from src.Controllers.Web.User.account_deletion_app import DeleteAccountForm
from src.Controllers.Web.User.account_edit_password_app import EditPasswordForm


class SettingsController(MethodView):
    """
    User Settings Controller.

    This class handles the user settings functionality.
    """

    decorators = [login_required]

    async def get(self) -> tuple[str, int]:
        """
        Get User Settings.

        Returns:
        ----
            tuple[template: str, http_status: int]
                - template: The rendered template for the settings page.
                - http_status: The HTTP status code indicating the success of the request.
        """
        deletion_form = DeleteAccountForm()
        edit_password_form = EditPasswordForm()
        template = await render_template(
            "settings.html",
            deletion_form=deletion_form,
            edit_password_form=edit_password_form,
        )
        return template, 200


account_settings_app = Blueprint(
    "account_settings_app", __name__, url_prefix="/settings"
)
account_settings_controller = SettingsController.as_view("controller")
account_settings_app.add_url_rule("/", view_func=account_settings_controller)
