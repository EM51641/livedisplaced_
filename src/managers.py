from quart.globals import app_ctx
from quart_auth import QuartAuth
from quart_wtf import CSRFProtect  # type: ignore

from src.Infrastructure.Database import DBManager
from src.Infrastructure.Email.sendgrid import EmailManager
from src.Infrastructure.Loggers.configuration import AsyncLogger
from src.Middlewares.global_middleware import CustomAuthUser

log_db = AsyncLogger()


def _get_current_context() -> int:
    id_ = id(app_ctx._get_current_object())  # type: ignore
    return id_


db = DBManager(_get_current_context)


email_manager = EmailManager()

login_manager = QuartAuth()
login_manager.user_class = CustomAuthUser

csrf_protection = CSRFProtect()
