import pytest
from quart import Quart


@pytest.fixture(scope="session", autouse=True)
def prepare_internal_error_endpoint(app: Quart) -> None:
    """
    Create a new application instance for each test case.
    """
    from werkzeug.exceptions import InternalServerError

    @app.route("/internal_error")
    def _internal_error() -> None:
        raise InternalServerError()
