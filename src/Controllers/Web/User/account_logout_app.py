from quart import Blueprint, flash, redirect, url_for
from quart.views import MethodView
from quart_auth import login_required, logout_user
from werkzeug import Response

account_logout_app = Blueprint("account_logout_app", __name__, url_prefix="/logout")


class LogoutUser(MethodView):
    """
    Controller class for handling user logout functionality.
    """

    decorators = [login_required]

    async def post(self) -> Response:
        """
        Handles POST requests for user logout.

        Returns:
            Response: The redirect response after logging out the user.
        """
        response = await self._logout()
        return response

    async def _logout(self) -> Response:
        """
        Logs out the user and redirects to the home page.

        Returns:
            Response: The redirect response after logging out the user.
        """
        logout_user()
        await flash("Logged out succesfully", category="flash-success")
        return redirect(url_for("root.web.user.account_login_app.controller"))


logout_controller = LogoutUser.as_view("controller")
account_logout_app.add_url_rule("/", view_func=logout_controller)
