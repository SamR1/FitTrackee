from typing import Dict, Tuple, Union

from flask import Blueprint, request
from sqlalchemy import asc, desc, nullslast

from fittrackee import db
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import WorkoutForbiddenException

from .exceptions import InvalidReporterException, ReportNotFoundException
from .models import REPORT_OBJECT_TYPES, Report
from .service import ReportService

reports_blueprint = Blueprint('reports', __name__)

REPORTS_PER_PAGE = 10
report_service = ReportService()


@reports_blueprint.route("/reports", methods=["POST"])
@require_auth(scopes=["reports:write"])
def create_report(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    data = request.get_json()
    object_id = data.get("object_id")
    object_type = data.get("object_type")
    note = data.get("note")
    if (
        not data
        or not note
        or not object_id
        or object_type not in REPORT_OBJECT_TYPES
    ):
        return InvalidPayloadErrorResponse()

    try:
        new_report = report_service.create_report(
            reporter=auth_user,
            note=note,
            object_id=object_id,
            object_type=object_type,
        )
        return (
            {
                "status": "created",
                "report": new_report.serialize(auth_user),
            },
            201,
        )
    except (
        CommentForbiddenException,
        UserNotFoundException,
        WorkoutForbiddenException,
    ):
        return NotFoundErrorResponse(
            f"{object_type} not found "
            f"({'username' if object_type == 'user' else 'id'}: {object_id})"
        )
    except InvalidReporterException:
        return InvalidPayloadErrorResponse(
            "users can not report their own profile"
            if object_type == "user"
            else f"users can not report their own {object_type}s"
        )
    except Exception as e:
        return handle_error_and_return_response(
            error=e,
            message="Error during report save.",
            status="fail",
            db=db,
        )


@reports_blueprint.route("/reports", methods=["GET"])
@require_auth(scopes=["reports:read"])
def get_reports(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    params = request.args.copy()
    page = int(params.get("page", 1))
    object_type = params.get("object_type")
    resolved = params.get("resolved", "").lower()
    column = params.get("order_by", "created_at")
    if column not in ["created_at", "updated_at"]:
        return InvalidPayloadErrorResponse("invalid 'order_by'")
    report_column = getattr(Report, column)
    order = params.get("order", "desc")
    order_clauses = [
        asc(report_column) if order == "asc" else desc(report_column)
    ]
    if column == "updated_at":
        order_clauses = [nullslast(order_clauses[0])]
    if column != "created_at":
        order_clauses.append(Report.created_at.desc())
    reporter_username = params.get("reporter")
    reporter = (
        User.query.filter(User.username == reporter_username).first()
        if params.get("reporter", "")
        else None
    )

    reports_pagination = (
        Report.query.filter(
            Report.reported_comment_id != None  # noqa
            if object_type == "comment"
            else True,
            Report.reported_user_id != None  # noqa
            if object_type == "user"
            else True,
            Report.reported_workout_id != None  # noqa
            if object_type == "workout"
            else True,
            Report.resolved == True  # noqa
            if resolved == "true"
            else Report.resolved == False  # noqa
            if resolved == "false"
            else True,
            Report.reported_by == auth_user.id
            if auth_user.admin is False
            else Report.reported_by == reporter.id
            if reporter
            else True,
        )
        .order_by(*order_clauses)
        .paginate(page=page, per_page=REPORTS_PER_PAGE, error_out=False)
    )
    reports = reports_pagination.items
    return {
        "status": "success",
        "reports": [report.serialize(auth_user) for report in reports],
        "pagination": {
            'has_next': reports_pagination.has_next,
            'has_prev': reports_pagination.has_prev,
            'page': reports_pagination.page,
            'pages': reports_pagination.pages,
            'total': reports_pagination.total,
        },
    }, 200


@reports_blueprint.route("/reports/<int:report_id>", methods=["GET"])
@require_auth(scopes=["reports:read"])
def get_report(
    auth_user: User, report_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    report = Report.query.filter_by(id=report_id).first()
    if not report or (
        not auth_user.admin and report.reported_by != auth_user.id
    ):
        return NotFoundErrorResponse(f"report not found (id: {report_id})")

    return {
        "status": "success",
        "report": report.serialize(auth_user),
    }, 200


@reports_blueprint.route("/reports/<int:report_id>", methods=["PATCH"])
@require_auth(scopes=["reports:write"], as_admin=True)
def update_report(
    auth_user: User, report_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    data = request.get_json()
    comment = data.get("comment")
    if not data or not comment:
        return InvalidPayloadErrorResponse()

    try:
        report = report_service.update_report(
            report_id=report_id,
            admin_user=auth_user,
            report_comment=comment,
            resolved=data.get("resolved") is True,
        )
    except ReportNotFoundException:
        return NotFoundErrorResponse(f"report not found (id: {report_id})")

    return {
        "status": "success",
        "report": report.serialize(auth_user),
    }, 200
