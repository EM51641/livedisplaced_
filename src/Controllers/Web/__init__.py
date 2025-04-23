from quart import Blueprint

from src.Controllers.Web.countries_report_app import countries_report_app
from src.Controllers.Web.flux_between_cntries_app import flux_between_cntries_app
from src.Controllers.Web.forget_password_app import forget_password_app
from src.Controllers.Web.overview_app import overview_app
from src.Controllers.Web.reset_password_app import reset_password_app
from src.Controllers.Web.terms_of_use_app import terms_app
from src.Controllers.Web.User import user_account_app


web_app = Blueprint("web", __name__)

web_app.register_blueprint(overview_app)
web_app.register_blueprint(countries_report_app)
web_app.register_blueprint(flux_between_cntries_app)
web_app.register_blueprint(forget_password_app)
web_app.register_blueprint(reset_password_app)
web_app.register_blueprint(terms_app)
web_app.register_blueprint(user_account_app)
