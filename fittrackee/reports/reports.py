from datetime import datetime
from typing import Dict, Tuple, Union

from flask import Blueprint, current_app, request
from sqlalchemy import asc, desc, exc, nullslast

from fittrackee import db
from fittrackee.administration.models import (
    OBJECTS_ADMIN_ACTION_TYPES,
    AdminAction,
    AdminActionAppeal,
)
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.models import Comment
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
from fittrackee.users.users_service import UserManagerService
from fittrackee.utils import decode_short_id
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import Workout

from .exceptions import (
    InvalidAdminActionException,
    InvalidReporterException,
    InvalidReportException,
    ReportNotFoundException,
    SuspendedObjectException,
)
from .models import REPORT_OBJECT_TYPES, Report
from .reports_email_service import (
    ReportEmailService,
)
from .reports_service import ReportService

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
    except (SuspendedObjectException, InvalidReportException) as e:
        return InvalidPayloadErrorResponse(str(e))
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
                else (
                    Report.resolved == False  # noqa
                    if resolved == "false"
                    else True
                )
            ),
            (
                Report.reported_by == auth_user.id
                if auth_user.admin is False
                else (
                    Report.reported_by == reporter.id
                    if reporter_username
                    else True
                )
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
    "/reports/<int:report_id>/admin-actions", methods=["POST"]
)
@require_auth(scopes=["reports:write"], as_admin=True)
def create_admin_action(
    auth_user: User, report_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    data = request.get_json()
    action_type = data.get("action_type", "")
    reason = data.get("reason")
    if not data or not action_type:
        return InvalidPayloadErrorResponse()
    if action_type not in OBJECTS_ADMIN_ACTION_TYPES:
        return InvalidPayloadErrorResponse("invalid 'action_type'")

    report = Report.query.filter_by(id=report_id).first()
    if not report:
        return NotFoundErrorResponse(f"report not found (id: {report_id})")

    try:
        report_service.create_admin_action(
            report=report,
            admin_user=auth_user,
            action_type=action_type,
            reason=reason,
            data=data,
        )
        db.session.flush()

        if current_app.config['CAN_SEND_EMAILS']:
            admin_action_email_service = ReportEmailService()
            admin_action_email_service.send_admin_action_email(
                report, action_type, reason
            )

        db.session.commit()

        return {
            "status": "success",
            "report": report.serialize(auth_user, full=True),
        }, 200
    except (UserAlreadySuspendedException, InvalidAdminActionException) as e:
        return InvalidPayloadErrorResponse(str(e))
    except Exception as e:
        return handle_error_and_return_response(
            error=e,
            message="Error during report save.",
            status="fail",
            db=db,
        )


@reports_blueprint.route(
    '/suspensions/appeals/<string:appeal_id>', methods=["PATCH"]
)
@require_auth(scopes=['users:write'], as_admin=True)
def process_appeal(
    auth_user: User, appeal_id: str
) -> Union[Dict, HttpResponse]:
    appeal_uuid = decode_short_id(appeal_id)
    appeal = AdminActionAppeal.query.filter_by(uuid=appeal_uuid).first()

    if not appeal:
        return NotFoundErrorResponse(
            message=f"appeal not found (id: {appeal_id})"
        )

    data = request.get_json()
    if not data or "approved" not in data or not data.get("reason"):
        return InvalidPayloadErrorResponse()

    try:
        appeal.admin_user_id = auth_user.id
        appeal.approved = data["approved"]
        appeal.reason = data["reason"]
        appeal.updated_at = datetime.utcnow()

        if data["approved"]:
            action = appeal.action
            if action.action_type == "user_suspension":
                user_manager_service = UserManagerService(
                    username=appeal.user.username, admin_user_id=auth_user.id
                )
                user, _, _ = user_manager_service.update(
                    suspended=False, report_id=appeal.action.report_id
                )
            if action.action_type == "comment_suspension":
                admin_action = AdminAction(
                    admin_user_id=auth_user.id,
                    action_type="comment_unsuspension",
                    comment_id=action.comment_id,
                    created_at=datetime.now(),
                    report_id=action.report_id,
                    user_id=action.user_id,
                )
                db.session.add(admin_action)
                comment = Comment.query.filter_by(id=action.comment_id).first()
                comment.suspended_at = None
            if action.action_type == "workout_suspension":
                admin_action = AdminAction(
                    admin_user_id=auth_user.id,
                    action_type="workout_unsuspension",
                    created_at=datetime.now(),
                    report_id=action.report_id,
                    user_id=action.user_id,
                    workout_id=action.workout_id,
                )
                db.session.add(admin_action)
                workout = Workout.query.filter_by(id=action.workout_id).first()
                workout.suspended_at = None
        db.session.commit()
        return {
            "status": "success",
            "appeal": appeal.serialize(auth_user),
        }

    except (exc.OperationalError, exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)
