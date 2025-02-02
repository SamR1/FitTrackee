from typing import TYPE_CHECKING, Dict, List, Tuple, Union

from flask import Blueprint, current_app, request
from sqlalchemy import asc, desc, exc, nullslast

from fittrackee import db
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.exceptions import (
    UserAlreadyReactivatedException,
    UserAlreadySuspendedException,
    UserNotFoundException,
)
from fittrackee.users.models import User
from fittrackee.users.roles import UserRole
from fittrackee.utils import decode_short_id
from fittrackee.workouts.exceptions import WorkoutForbiddenException

from .exceptions import (
    InvalidReportActionException,
    InvalidReporterException,
    InvalidReportException,
    ReportNotFoundException,
    SuspendedObjectException,
    UserWarningExistsException,
)
from .models import (
    OBJECTS_ACTION_TYPES,
    REPORT_OBJECT_TYPES,
    Report,
    ReportActionAppeal,
)
from .reports_email_service import (
    ReportEmailService,
)
from .reports_service import ReportService

if TYPE_CHECKING:
    from sqlalchemy.sql.expression import UnaryExpression

reports_blueprint = Blueprint("reports", __name__)

REPORTS_PER_PAGE = 10
report_service = ReportService()


@reports_blueprint.route("/reports", methods=["POST"])
@require_auth(scopes=["reports:write"])
def create_report(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Create a report.

    **Scope**: ``reports:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/reports HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

    :<json string note: note describing report
    :<json string object_id: id of content reported
    :<json string object_type: type of content reported (``comment``,
           ``workout`` or ``user``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: report created
    :statuscode 400:
        - ``invalid payload``
        - ``users can not report their own comment``
        - ``users can not report their own profile``
        - ``users can not report their own workout``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``comment not found``
        - ``user not found``
        - ``workout not found``
    :statuscode 500: ``Error during comment save.``
    """
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
@require_auth(scopes=["reports:read"], role=UserRole.MODERATOR)
def get_reports(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Get reports.

    **Scope**: ``reports:read``

    **Minimum role**: Moderator

    **Example requests**:

    - without parameters:

    .. sourcecode:: http

      GET /api/reports/ HTTP/1.1

    - with some query parameters:

    .. sourcecode:: http

      GET /api/reports?page=1&order=desc&order_by=created_at  HTTP/1.1

    **Example responses**:

    - returning at least one report:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

        {
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 1,
            "total": 1
          },
          "reports": [
            {
              "created_at": "Sun, 01 Dec 2024 18:17:30 GMT",
              "id": 1,
              "is_reported_user_warned": false,
              "note": "<REPORT NOTE>",
              "object_type": "user",
              "reported_by": {
                "created_at": "Sun, 01 Dec 2024 17:27:56 GMT",
                "email": "moderator@example.com",
                "followers": 0,
                "following": 0,
                "is_active": true,
                "nb_workouts": 0,
                "picture": false,
                "role": "moderator",
                "suspended_at": null,
                "username": "moderator"
              },
              "reported_comment": null,
              "reported_user": {
                "blocked": false,
                "created_at": "Sun, 01 Dec 2024 17:27:49 GMT",
                "email": "sam@example.com",
                "followers": 0,
                "following": 0,
                "follows": "false",
                "is_active": true,
                "is_followed_by": "false",
                "nb_workouts": 1,
                "picture": false,
                "role": "user",
                "suspended_at": null,
                "username": "Sam"
              },
              "reported_workout": null,
              "resolved": false,
              "resolved_at": null,
              "resolved_by": null,
              "updated_at": null
            }
          ],
          "status": "success"
        }

    - returning no reports

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 0,
            "total": 0
          },
          "reports": [],
          "status": "success"
        }

    :query integer object_type: reported content type (``comment``, ``user``
           or ``workout``)
    :query string order: sorting order: ``asc``, ``desc`` (default: ``desc``)
    :query string order_by: sorting criteria: ``created_at`` or ``updated_at``
    :query integer page: page if using pagination (default: 1)
    :query boolean reporter: reporter username
    :query boolean resolved: filter on report status

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid payload``
        - ``invalid 'order_by'``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    """
    params = request.args.copy()
    page = int(params.get("page", 1))
    object_type = params.get("object_type")
    resolved = params.get("resolved", "").lower()
    column = params.get("order_by", "created_at")
    if column not in ["created_at", "updated_at"]:
        return InvalidPayloadErrorResponse("invalid 'order_by'")
    report_column = getattr(Report, column)
    order = params.get("order", "desc")
    order_clauses: List["UnaryExpression"] = [
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

    filters = []
    if object_type:
        filters.append(Report.object_type == object_type)
    if resolved == "true":
        filters.append(Report.resolved == True)  # noqa
    elif resolved == "false":
        filters.append(Report.resolved == False)  # noqa
    if auth_user.role < UserRole.MODERATOR.value:
        filters.append(Report.reported_by == auth_user.id)
    elif reporter and reporter_username:
        filters.append(Report.reported_by == reporter.id)
    reports_pagination = (
        Report.query.filter(*filters)
        .order_by(*order_clauses)
        .paginate(page=page, per_page=REPORTS_PER_PAGE, error_out=False)
    )
    reports = reports_pagination.items
    return {
        "status": "success",
        "reports": [report.serialize(auth_user) for report in reports],
        "pagination": {
            "has_next": reports_pagination.has_next,
            "has_prev": reports_pagination.has_prev,
            "page": reports_pagination.page,
            "pages": reports_pagination.pages,
            "total": reports_pagination.total,
        },
    }, 200


@reports_blueprint.route("/reports/<int:report_id>", methods=["GET"])
@require_auth(scopes=["reports:read"], role=UserRole.MODERATOR)
def get_report(
    auth_user: User, report_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Get report.

    **Scope**: ``reports:read``

    **Minimum role**: Moderator

    **Example request**:

    .. sourcecode:: http

      GET /api/reports/1 HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

        {
          "report": {
            "comments": [],
            "created_at": "Sun, 01 Dec 2024 18:17:30 GMT",
            "id": 1,
            "is_reported_user_warned": false,
            "note": "<REPORT NOTE>",
            "object_type": "user",
            "report_actions": [],
            "reported_by": {
              "created_at": "Sun, 01 Dec 2024 17:27:56 GMT",
              "email": "moderator@example.com",
              "followers": 0,
              "following": 0,
              "is_active": true,
              "nb_workouts": 0,
              "picture": false,
              "role": "moderator",
              "suspended_at": null,
              "username": "moderator"
            },
            "reported_comment": null,
            "reported_user": {
              "blocked": false,
              "created_at": "Sun, 01 Dec 2024 17:27:49 GMT",
              "email": "sam@example.com",
              "followers": 0,
              "following": 0,
              "follows": "false",
              "is_active": true,
              "is_followed_by": "false",
              "nb_workouts": 1,
              "picture": false,
              "role": "user",
              "suspended_at": null,
              "username": "Sam"
            },
            "reported_workout": null,
            "resolved": false,
            "resolved_at": null,
            "resolved_by": null,
            "updated_at": null
          },
          "status": "success"
        }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404:
        - ``report not found``
    """
    report = Report.query.filter_by(id=report_id).first()
    if not report or (
        not auth_user.has_moderator_rights
        and report.reported_by != auth_user.id
    ):
        return NotFoundErrorResponse(f"report not found (id: {report_id})")

    return {
        "status": "success",
        "report": report.serialize(auth_user, full=True),
    }, 200


@reports_blueprint.route("/reports/<int:report_id>", methods=["PATCH"])
@require_auth(scopes=["reports:write"], role=UserRole.MODERATOR)
def update_report(
    auth_user: User, report_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Update report.

    **Scope**: ``reports:write``

    **Minimum role**: Moderator

    **Example request**:

    .. sourcecode:: http

      PATCH /api/reports/1 HTTP/1.1

    **Example response** (report on user profile):

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

        {
          "report": {
            "comments": [
              {
                "comment": "<REPORT COMMENT>",
                "created_at": "Sun, 01 Dec 2024 18:21:38 GMT",
                "id": 1,
                "report_id": 1,
                "user": {
                  "created_at": "Sun, 01 Dec 2024 17:27:56 GMT",
                  "email": "moderator@example.com",
                  "followers": 0,
                  "following": 0,
                  "is_active": true,
                  "nb_workouts": 0,
                  "picture": false,
                  "role": "moderator",
                  "suspended_at": null,
                  "username": "moderator"
                }
              }
            ],
            "created_at": "Sun, 01 Dec 2024 18:17:30 GMT",
            "id": 1,
            "is_reported_user_warned": false,
            "note": "<REPORT NOTE>",
            "object_type": "user",
            "report_actions": [],
            "reported_by": {
              "created_at": "Sun, 01 Dec 2024 17:27:56 GMT",
              "email": "moderator@example.com",
              "followers": 0,
              "following": 0,
              "is_active": true,
              "nb_workouts": 0,
              "picture": false,
              "role": "moderator",
              "suspended_at": null,
              "username": "moderator"
            },
            "reported_comment": null,
            "reported_user": {
              "blocked": false,
              "created_at": "Sun, 01 Dec 2024 17:27:49 GMT",
              "email": "sam@example.com",
              "followers": 0,
              "following": 0,
              "follows": "false",
              "is_active": true,
              "is_followed_by": "false",
              "nb_workouts": 1,
              "picture": false,
              "role": "user",
              "suspended_at": null,
              "username": "Sam"
            },
            "reported_workout": null,
            "resolved": false,
            "resolved_at": null,
            "resolved_by": null,
            "updated_at": "Sun, 01 Dec 2024 18:21:38 GMT"
          },
          "status": "success"
        }

    :param string report_id: report id

    :<json string notes: report comment (mandatory)
    :<json boolean resolved: report status

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid payload``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
    :statuscode 404:
        - ``report not found``
    """
    data = request.get_json()
    comment = data.get("comment")
    if not data or not comment:
        return InvalidPayloadErrorResponse()

    try:
        report = report_service.update_report(
            report_id=report_id,
            moderator=auth_user,
            report_comment=comment,
            resolved=data.get("resolved"),
        )
    except ReportNotFoundException:
        return NotFoundErrorResponse(f"report not found (id: {report_id})")

    return {
        "status": "success",
        "report": report.serialize(auth_user, full=True),
    }, 200


@reports_blueprint.route("/reports/<int:report_id>/actions", methods=["POST"])
@require_auth(scopes=["reports:write"], role=UserRole.MODERATOR)
def create_action(
    auth_user: User, report_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Create report action.

    **Scope**: ``reports:write``

    **Minimum role**: Moderator

    **Example request**:

    .. sourcecode:: http

      POST /api/reports/1/actions HTTP/1.1

    **Example response** (report on user profile):

    .. sourcecode:: http

      HTTP/1.1 201 SUCCESS
      Content-Type: application/json

        {
          "report": {
            "comments": [
              {
                "comment": "<REPORT COMMENT>",
                "created_at": "Sun, 01 Dec 2024 18:21:38 GMT",
                "id": 1,
                "report_id": 1,
                "user": {
                  "created_at": "Sun, 01 Dec 2024 17:27:56 GMT",
                  "email": "moderator@example.com",
                  "followers": 0,
                  "following": 0,
                  "is_active": true,
                  "nb_workouts": 0,
                  "picture": false,
                  "role": "moderator",
                  "suspended_at": null,
                  "username": "moderator"
                }
              }
            ],
            "created_at": "Sun, 01 Dec 2024 18:17:30 GMT",
            "id": 1,
            "is_reported_user_warned": false,
            "note": "<REPORT NOTE>",
            "object_type": "user",
            "report_actions": [
              {
                "action_type": "user_warning",
                "appeal": null,
                "created_at": "Wed, 04 Dec 2024 09:12:25 GMT",
                "id": "Hv9KwVDtBHhyfvML7PHovq",
                "moderator": {
                  "created_at": "Sun, 01 Dec 2024 17:27:56 GMT",
                  "email": "moderator@example.com",
                  "followers": 0,
                  "following": 0,
                  "is_active": true,
                  "nb_workouts": 0,
                  "picture": false,
                  "role": "moderator",
                  "suspended_at": null,
                  "username": "moderator"
                },
                "reason": "<ACTION REASON>",
                "report_id": 1,
                "user": {
                  "blocked": false,
                  "created_at": "Sun, 01 Dec 2024 17:27:49 GMT",
                  "email": "sam@example.com",
                  "followers": 0,
                  "following": 0,
                  "follows": "false",
                  "is_active": true,
                  "is_followed_by": "false",
                  "nb_workouts": 1,
                  "picture": false,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                }
              }
            ],
            "reported_by": {
              "created_at": "Sun, 01 Dec 2024 17:27:56 GMT",
              "email": "moderator@example.com",
              "followers": 0,
              "following": 0,
              "is_active": true,
              "nb_workouts": 0,
              "picture": false,
              "role": "moderator",
              "suspended_at": null,
              "username": "moderator"
            },
            "reported_comment": null,
            "reported_user": {
              "blocked": false,
              "created_at": "Sun, 01 Dec 2024 17:27:49 GMT",
              "email": "sam@example.com",
              "followers": 0,
              "following": 0,
              "follows": "false",
              "is_active": true,
              "is_followed_by": "false",
              "nb_workouts": 1,
              "picture": false,
              "role": "user",
              "suspended_at": null,
              "username": "Sam"
            },
            "reported_workout": null,
            "resolved": false,
            "resolved_at": null,
            "resolved_by": null,
            "updated_at": "Sun, 01 Dec 2024 18:21:38 GMT"
          },
          "status": "success"
        }

    :param string report_id: report id

    :<json string action_type: action type (expected value:
           ``user_suspension``, ``user_unsuspension``, ``user_warning``,
           ``comment_suspension``, ``comment_unsuspension``,
           ``workout_suspension``, ``workout_unsuspension``)
    :<json string comment_id: id of comment affected by action (type:
           ``comment_suspension``, ``comment_suspension``)
    :<json string reason: text explaining the reason for the action
    :<json string username: username of user affected by action (type:
           ``user_suspension``, ``user_unsuspension``, ``user_warning``)
    :<json string workout_id: id of workout affected by action (type:
           ``workout_suspension``, ``workout_unsuspension``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid payload``
        - ``invalid 'action_type'``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
    :statuscode 404:
        - ``report not found``
    :statuscode 500:
        - ``Error during report save.``
    """
    data = request.get_json()
    action_type = data.get("action_type", "")
    reason = data.get("reason")
    if not data or not action_type:
        return InvalidPayloadErrorResponse()
    if (
        action_type == "user_warning_lifting"
        or action_type not in OBJECTS_ACTION_TYPES
    ):
        return InvalidPayloadErrorResponse("invalid 'action_type'")

    report = Report.query.filter_by(id=report_id).first()
    if not report:
        return NotFoundErrorResponse(f"report not found (id: {report_id})")

    try:
        action = report_service.create_report_action(
            report=report,
            moderator=auth_user,
            action_type=action_type,
            reason=reason,
            data=data,
        )
        db.session.flush()

        if current_app.config["CAN_SEND_EMAILS"]:
            report_action_email_service = ReportEmailService()
            report_action_email_service.send_report_action_email(
                report, action_type, reason, action
            )

        db.session.commit()

        return {
            "status": "success",
            "report": report.serialize(auth_user, full=True),
        }, 200
    except (
        InvalidReportActionException,
        UserAlreadyReactivatedException,
        UserAlreadySuspendedException,
        UserWarningExistsException,
    ) as e:
        return InvalidPayloadErrorResponse(str(e))
    except Exception as e:
        return handle_error_and_return_response(
            error=e,
            message="Error during report save.",
            status="fail",
            db=db,
        )


@reports_blueprint.route("/appeals/<string:appeal_id>", methods=["PATCH"])
@require_auth(scopes=["users:write"], role=UserRole.MODERATOR)
def process_appeal(
    auth_user: User, appeal_id: str
) -> Union[Dict, HttpResponse]:
    """
    Process appeal.

    **Scope**: ``users:write``

    **Minimum role**: Moderator

    **Example request**:

    .. sourcecode:: http

      POST /api/appeals/Z2Ze5qZrnMVmnDejPphASk HTTP/1.1

    **Example response** (report on user profile):

    .. sourcecode:: http

      HTTP/1.1 201 SUCCESS
      Content-Type: application/json

        {
          "appeal": {
            "approved": true,
            "created_at": "Wed, 04 Dec 2024 09:29:18 GMT",
            "id": "Z2Ze5qZrnMVmnDejPphASk",
            "moderator": {
              "created_at": "Sun, 01 Dec 2024 17:27:56 GMT",
              "email": "moderator@example.com",
              "followers": 0,
              "following": 0,
              "is_active": true,
              "nb_workouts": 0,
              "picture": false,
              "role": "moderator",
              "suspended_at": null,
              "username": "moderator"
            },
            "reason": "<REASON>",
            "text": "<APPEAL TEXT>",
            "updated_at": "Wed, 04 Dec 2024 09:30:21 GMT",
            "user": {
              "blocked": false,
              "created_at": "Sun, 01 Dec 2024 17:27:49 GMT",
              "email": "sam@example.com",
              "followers": 0,
              "following": 0,
              "follows": "false",
              "is_active": true,
              "is_followed_by": "false",
              "nb_workouts": 1,
              "picture": false,
              "role": "user",
              "suspended_at": null,
              "username": "Sam"
            }
          },
          "status": "success"
        }

    :param string appeal_id: appeal id

    :<json boolean approved: ``true`` if appeal is approved, ``false`` if
           rejected
    :<json string reason: text explaining why the appeal was approved or
           rejected

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid payload``
        - ``comment already reactivated``
        - ``user account has already been reactivated``
        - ``workout already reactivated``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
    :statuscode 404:
        - ``appeal not found``
    :statuscode 500:
        - ``Error during report save.``
    """
    appeal_uuid = decode_short_id(appeal_id)
    appeal = ReportActionAppeal.query.filter_by(uuid=appeal_uuid).first()

    if not appeal:
        return NotFoundErrorResponse(
            message=f"appeal not found (id: {appeal_id})"
        )

    data = request.get_json()
    reason = data.get("reason")
    if not data or "approved" not in data or not reason:
        return InvalidPayloadErrorResponse()

    try:
        new_report_action = report_service.process_appeal(
            appeal, auth_user, data
        )
        db.session.flush()

        if current_app.config["CAN_SEND_EMAILS"]:
            if new_report_action:
                report_action_email_service = ReportEmailService()
                report_action_email_service.send_report_action_email(
                    new_report_action.report,
                    new_report_action.action_type,
                    reason,
                    new_report_action,
                )
            if data["approved"] is False:
                action = appeal.action
                report_action_email_service = ReportEmailService()
                report_action_email_service.send_report_action_email(
                    action.report,
                    "appeal_rejected",
                    None,
                    action,
                )

        db.session.commit()
        return {
            "status": "success",
            "appeal": appeal.serialize(auth_user),
        }

    except InvalidReportActionException as e:
        return InvalidPayloadErrorResponse(str(e))
    except (exc.OperationalError, exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@reports_blueprint.route("/reports/unresolved", methods=["GET"])
@require_auth(scopes=["reports:read"], role=UserRole.MODERATOR)
def get_unresolved_reports_status(
    auth_user: User,
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Get if unresolved reports exist.

    **Scope**: ``reports:read``

    **Minimum role**: Moderator

    **Example request**:

    .. sourcecode:: http

      POST /api/reports/unresolved HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 SUCCESS
      Content-Type: application/json

        {
          "status": "success",
          "unresolved": true
        }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
    """
    unresolved_reports = Report.query.filter(
        Report.resolved == False  # noqa
    ).count()
    return {
        "status": "success",
        "unresolved": unresolved_reports > 0,
    }, 200
