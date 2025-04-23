"""
This module defines the user controller blueprint.

The user controller handles routes related to user management.

Attributes:
    app (Blueprint): The user controller blueprint.

"""

from __future__ import annotations


from quart import Blueprint

from src.Controllers.Web.User.account_activation_app import account_activation_app
from src.Controllers.Web.User.account_deletion_app import account_deletion_app
from src.Controllers.Web.User.account_edit_password_app import account_edit_password_app
from src.Controllers.Web.User.account_login_app import account_login_app
from src.Controllers.Web.User.account_logout_app import account_logout_app
from src.Controllers.Web.User.account_oauth_login_app import account_oauth_login_app
from src.Controllers.Web.User.account_registration_app import account_registration_app
from src.Controllers.Web.User.account_settings_app import account_settings_app

user_account_app = Blueprint("user", __name__, url_prefix="/user")

user_account_app.register_blueprint(account_activation_app)

user_account_app.register_blueprint(account_deletion_app)

user_account_app.register_blueprint(account_edit_password_app)

user_account_app.register_blueprint(account_login_app)

user_account_app.register_blueprint(account_logout_app)

user_account_app.register_blueprint(account_oauth_login_app)

user_account_app.register_blueprint(account_registration_app)

user_account_app.register_blueprint(account_settings_app)

__all__ = ["user_account_app"]
