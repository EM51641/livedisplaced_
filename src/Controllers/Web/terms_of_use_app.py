from uuid import UUID

from quart import Blueprint, flash, redirect, render_template, request, url_for
from quart.views import MethodView
from quart_auth import current_user, login_required
from quart_wtf import QuartForm  # type: ignore
from werkzeug import Response
from wtforms import BooleanField, SubmitField  # type: ignore
from wtforms.validators import DataRequired  # type: ignore

from src.Context.Service.Exceptions import IncorrectInput
from src.Context.Service.TermsOfUse import UserComplianceService
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities.TermsOfUse import (
    SignedTermsOfUseEntity,
    TermsOfUseEntity,
)
from src.managers import db

terms_app = Blueprint("terms_app", __name__, url_prefix="/terms")

UNPROTECTED_ENDPOINT_COMPLIANCE = {
    "root.web.terms_app.compliance_controller",
    "root.web.user.account_logout_app.controller",
    "root.web.user.oauth_app.google_auth_redirect_controller",
    "root.web.user.oauth_app.facebook_auth_redirect_controller",
    "root.web.user.oauth_app.facebook_callback_controller",
    "root.web.user.oauth_app.google_callback_controller",
    "root.web.user.account_login_app.controller",
    "root.web.user.account_settings_app.controller",
    "root.web.terms_app.privacy_policy_controller",
    "root.web.terms_app.terms_of_use_controller",
    "root.web.terms_app.compliance_controller",
    "static",
}


@terms_app.before_app_request
async def compliance_middleware(
    unprotected_endpoints: set[str] = UNPROTECTED_ENDPOINT_COMPLIANCE,
) -> Response | None:
    """
    Middleware that enforces compliance with the latest terms of use
    for authenticated users. If the user is authenticated and the
    requested endpoint is not in the set of unprotected endpoints,
    the function checks if the user has accepted the latest terms of use.
    If not, the user is redirected to the compliance page.

    :param user: The authenticated user. Defaults to the current user.
    :param db: The database connection. Defaults to the global `db` instance.
    :param unprotected_endpoints: A set of endpoint names that are exempt from
                                    compliance checks.
    :return: A Quart response object if the user is not compliant,
                None otherwise.
    """
    from src.Middlewares.global_middleware import CustomAuthUser

    auth_user: CustomAuthUser = current_user  # type: ignore
    db_session = DBSession(db.session)
    if auth_user.auth_id and request.endpoint not in unprotected_endpoints:
        user = await auth_user.load_user()
        latest_term = await _get_latest_compliant_term(db_session)
        latest_user_term = await _get_latest_user_compliant_term(user.id, db_session)
        if latest_term.id != latest_user_term.termsofuse_id:  # type: ignore
            return redirect(url_for("root.web.terms_app.compliance_controller"))
    return None  # Add a return statement at the end of the function


async def _get_latest_compliant_term(db: DBSession) -> TermsOfUseEntity:
    """
    Returns the latest compliant terms of use entity from the database.

    Args:
        db (Database): The database instance to query.

    Returns:
        TermsOfUseEntity: The latest compliant terms of use entity.
    """
    query = db.select(TermsOfUseEntity).order_by(TermsOfUseEntity.created).limit(1)
    result = await db.execute(query)
    entity = result.scalar()
    return entity  # type: ignore


async def _get_latest_user_compliant_term(
    user_id: UUID, db: DBSession
) -> SignedTermsOfUseEntity | None:
    """Retrieve the latest signed terms of use entity for a given user.

    Args:
        user_id (UUID): The ID of the user to retrieve the entity for.
        db (Database): The database session to use.

    Returns:
        SignedTermsOfUseEntity: The latest signed terms of use entity for
                the user.
    """
    query = (
        db.select(SignedTermsOfUseEntity)
        .filter(SignedTermsOfUseEntity.user_id == user_id)
        .order_by(SignedTermsOfUseEntity.user_id)
        .limit(1)
    )
    result = await db.execute(query)
    entity = result.scalar()
    return entity


@terms_app.route("/privacy-policy", methods=["GET"])
async def privacy_policy_controller() -> tuple[str, int]:
    """
    Returns the privacy policy page to the user.

    :return: A tuple containing the rendered privacy policy
                page and a 200 status code.
    """
    return await render_template("privacy_policy.html"), 200


@terms_app.route("/terms-of-use", methods=["GET"])
async def terms_of_use_controller() -> tuple[str, int]:
    """
    Controller function for the terms of use page.

    Returns:
        A tuple containing the rendered template and the HTTP status code.
    """
    return await render_template("terms_of_use.html"), 200


class SubmitTermsAcceptance(QuartForm):
    agree = BooleanField(
        "agree",
        validators=[DataRequired()],
    )
    submit = SubmitField("Submit")


class ComplyController(MethodView):
    """
    Controller for the compliance page.
    """

    decorators = [login_required]

    def __init__(self, service: UserComplianceService) -> None:
        """
        Initialize the controller.

        Args:
            service: The service to use for making the user compliant.
            user: The user to make compliant. Defaults to the current user.
        """
        self._service = service

    async def get(self) -> tuple[str, int]:
        """
        Get Compliance Page

        Returns:
            A tuple containing the compliance page template and a 200
                status code.
        """
        form = await SubmitTermsAcceptance.create_form()
        template = await render_template("compliance_form.html", form=form)
        return template, 200

    async def post(self) -> Response:
        """
        Post Compliance Page

        Returns:
            A redirect response to the home page with a 200 status code.
        """
        try:
            response = await self._make_user_compliant()
        except IncorrectInput as exec:
            response = await self._document_and_redirect_when_input_is_wrong(exec)
        return response

    async def _make_user_compliant(self) -> Response:
        """
        Make the user compliant.

        Returns:
            A redirect response to the home page with a 200 status code.
        """
        assert current_user.auth_id

        await self._extract_form_data()
        await self._service.make_user_compliant(UUID(current_user.auth_id))
        return redirect(url_for("root.web.overview_app.controller"))

    async def _document_and_redirect_when_input_is_wrong(
        self, exception: IncorrectInput
    ) -> Response:
        """
        Handle failure response.

        Parameters:
        ----
            exception: IncorrectInput
                Exception for incorrect input.

        Returns:
        ----
            Response
                HTTP response.
        """
        for key, value in exception.errors.items():
            await flash(f"{key}: {value}", category="flash-errors")
        return redirect(url_for("root.web.terms_app.compliance_controller"))

    async def _extract_form_data(self) -> None:
        """
        Transform form data to DTO.

        This method extracts data from a form and transforms it into a RequestPasswordChangeDTO object.

        Parameters:
            None

        Returns:
            RequestPasswordChangeDTO | None
                An instance of RequestPasswordChangeDTO class if the form
                data is valid, otherwise None.
        """
        form = await SubmitTermsAcceptance.create_form()
        if not await form.validate_on_submit():
            raise IncorrectInput(errors=form.errors)  # type: ignore


compliance_controller = ComplyController.as_view("compliance_controller")
terms_app.add_url_rule("/comply", view_func=compliance_controller)
