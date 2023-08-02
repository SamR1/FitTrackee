from typing import Dict, Tuple, Union

from flask import Blueprint, request
from sqlalchemy import func

from fittrackee import db
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.utils import get_comment
from fittrackee.oauth2.server import require_auth
from fittrackee.reports.models import REPORT_OBJECT_TYPES
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.utils.workouts import get_workout

from .models import Report

reports_blueprint = Blueprint('reports', __name__)


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

    if object_type == "comment":
        try:
            target_object = get_comment(object_id, auth_user)
        except CommentForbiddenException:
            return NotFoundErrorResponse(
                f"comment not found (id: {object_id})"
            )

    elif object_type == "workout":
        try:
            target_object = get_workout(object_id, auth_user)
        except WorkoutForbiddenException:
            return NotFoundErrorResponse(
                f"workout not found (id: {object_id})"
            )

    else:  # object_type == "user"
        target_object = User.query.filter(
            func.lower(User.username) == func.lower(object_id),
        ).first()
        if not target_object or not target_object.is_active:
            return NotFoundErrorResponse(
                f"user not found (username: {object_id})"
            )
    try:
        new_report = Report(
            reported_by=auth_user.id,
            note=note,
            object_id=target_object.id,
            object_type=object_type,
        )
        db.session.add(new_report)
        db.session.commit()

        return (
            {
                "status": "created",
                "report": new_report.serialize(auth_user),
            },
            201,
        )
    except Exception as e:
        return handle_error_and_return_response(
            error=e,
            message="Error during report save.",
            status="fail",
            db=db,
        )
