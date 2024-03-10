from datetime import datetime
from typing import Dict, Tuple, Union

from flask import Blueprint, request
from sqlalchemy import asc, desc, nullslast

from fittrackee import db
from fittrackee.administration.models import (
    COMMENT_ACTION_TYPES,
    OBJECTS_ADMIN_ACTION_TYPES,
    USER_ACTION_TYPES,
    WORKOUT_ACTION_TYPES,
    AdminAction,
)
from fittrackee.administration.reports_service import ReportService
from fittrackee.administration.users_service import UserManagerService
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.exceptions import (
    UserAlreadySuspendedException,
    UserNotFoundException,
)
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import WorkoutForbiddenException

from .exceptions import InvalidReporterException, ReportNotFoundException
from .models import REPORT_OBJECT_TYPES, Report

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
        report_service.create_report(
            reporter=auth_user,
            note=note,
            object_id=object_id,
            object_type=object_type,
        )
        return {"status": "created"}, 201
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
    reporter_username = params.get("reporter", "")
    reporter = (
        User.query.filter(User.username == reporter_username).first()
        if reporter_username
        else None
    )

    reports_pagination = (
        Report.query.filter(
            Report.object_type == object_type if object_type else True,
            (
                Report.resolved == True  # noqa
                if resolved == "true"
                else Report.resolved == False  # noqa
                if resolved == "false"
                else True
            ),
            (
                Report.reported_by == auth_user.id
                if auth_user.admin is False
                else Report.reported_by == reporter.id
                if reporter_username
                else True
            ),
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
        "report": report.serialize(auth_user, full=True),
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
            resolved=data.get("resolved"),
        )
    except ReportNotFoundException:
        return NotFoundErrorResponse(f"report not found (id: {report_id})")

    return {
        "status": "success",
        "report": report.serialize(auth_user, full=True),
    }, 200


@reports_blueprint.route(
    "/reports/<int:report_id>/admin_actions", methods=["POST"]
)
@require_auth(scopes=["reports:write"], as_admin=True)
def create_admin_action(
    auth_user: User, report_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    data = request.get_json()
    action_type = data.get("action_type")
    reason = data.get("reason")
    if not data or not action_type:
        return InvalidPayloadErrorResponse()
    if action_type not in OBJECTS_ADMIN_ACTION_TYPES:
        return InvalidPayloadErrorResponse("invalid 'action_type'")

    report = Report.query.filter_by(id=report_id).first()
    if not report or (
        not auth_user.admin and report.reported_by != auth_user.id
    ):
        return NotFoundErrorResponse(f"report not found (id: {report_id})")

    try:
        if action_type in USER_ACTION_TYPES:
            username = data.get("username")
            if not username:
                return InvalidPayloadErrorResponse("'username' is missing")
            reported_user = report.reported_user
            if not reported_user or username != reported_user.username:
                return InvalidPayloadErrorResponse("invalid 'username'")

            user_manager_service = UserManagerService(
                username=username, admin_user_id=auth_user.id
            )
            user, _, _ = user_manager_service.update(
                suspended=action_type == "user_suspension",
                report_id=report_id,
                reason=reason,
            )

        if action_type in COMMENT_ACTION_TYPES + WORKOUT_ACTION_TYPES:
            object_type = action_type.split("_")[0]
            object_type_column = f"{object_type}_id"
            object_id = data.get(object_type_column)
            if not object_id:
                return InvalidPayloadErrorResponse(
                    f"'{object_type_column}' is missing"
                )
            reported_object = getattr(report, f"reported_{object_type}")
            if not reported_object or reported_object.short_id != object_id:
                return InvalidPayloadErrorResponse(
                    f"invalid '{object_type_column}'"
                )

            now = datetime.utcnow()
            if "_suspension" in action_type:
                if reported_object.suspended_at:
                    return InvalidPayloadErrorResponse(
                        f"{object_type} '{object_id}' already suspended"
                    )
                reported_object.suspended_at = now
            else:
                reported_object.suspended_at = None
            admin_action = AdminAction(
                admin_user_id=auth_user.id,
                action_type=action_type,
                created_at=now,
                report_id=report_id,
                reason=reason,
                user_id=reported_object.user_id,
                **{object_type_column: reported_object.id},
            )
            db.session.add(admin_action)
            db.session.commit()

        return {
            "status": "success",
            "report": report.serialize(auth_user, full=True),
        }, 200
    except UserAlreadySuspendedException as e:
        return InvalidPayloadErrorResponse(str(e))
    except Exception as e:
        return handle_error_and_return_response(
            error=e,
            message="Error during report save.",
            status="fail",
            db=db,
        )
