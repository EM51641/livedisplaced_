from quart import Blueprint, jsonify

from src.Controllers.API.bilateral_ts_data_api import bilateral_app
from src.Controllers.API.country_ts_data_api import country_ts_api_app
from src.Controllers.API.global_data_api import global_api_app

app_api = Blueprint("api", __name__, url_prefix="/api/v1")
app_api.register_blueprint(bilateral_app)
app_api.register_blueprint(country_ts_api_app)
app_api.register_blueprint(global_api_app)


@app_api.route("/health-check")
async def health_check():
    return jsonify({"status": "ok"}), 200
