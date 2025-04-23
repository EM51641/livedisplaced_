from quart import Blueprint

from src.Controllers.API import app_api
from src.Controllers.Web import web_app

root_app = Blueprint("root", __name__)
root_app.register_blueprint(app_api)
root_app.register_blueprint(web_app)
