from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import func

from fittrackee import db
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import HttpResponse, InvalidPayloadErrorResponse
from fittrackee.users.models import TASK_TYPES, User, UserTask
from fittrackee.users.roles import UserRole

queued_tasks_blueprint = Blueprint("queued_users_tasks", __name__)

TASKS_PER_PAGE = 5
USERS_QUEUED_TASKS_FILTERS = [
    UserTask.progress == 0,
    UserTask.errored == False,  # noqa
    UserTask.aborted == False,  # noqa
]


@queued_tasks_blueprint.route("/users/tasks/queued", methods=["GET"])
@require_auth(scopes=["users:read"], role=UserRole.ADMIN)
def get_queued_users_tasks_count(
    auth_user: "User",
) -> Union[Dict, HttpResponse]:
    """
    Get queued tasks.

    **Scope**: ``tasks:read``

    **Minimum role**: Administrator

    **Example request**:

    .. sourcecode:: http

      GET /api/tasks/queued HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "counts": {
          "user_data_export": 0,
          "workouts_archive_upload": 1
        },
        "status": "success"
      }

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
    """
    tasks_counts = (
        db.session.query(UserTask.task_type, func.count(UserTask.task_type))
        .filter(*USERS_QUEUED_TASKS_FILTERS)
        .group_by(UserTask.task_type)
        .all()
    )
    counts: Dict = {"user_data_export": 0, "workouts_archive_upload": 0}
    for count in tasks_counts:
        counts[count[0]] = count[1]

    return {
        "status": "success",
        "counts": counts,
    }


@queued_tasks_blueprint.route(
    "/users/tasks/queued/<string:task_type>", methods=["GET"]
)
@require_auth(scopes=["users:read"], role=UserRole.ADMIN)
def get_queued_users_tasks_list(
    auth_user: "User", task_type: str
) -> Union[Dict, HttpResponse]:
    """
    Get queued tasks for a given type

    **Scope**: ``tasks:read``

    **Minimum role**: Administrator

    **Example request**:

    .. sourcecode:: http

      GET /api/config HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "pagination": {
          "has_next": false,
          "has_prev": false,
          "page": 1,
          "pages": 1,
          "total": 1
        },
        "queued_tasks": [
          {
            "created_at": "Mon, 21 Apr 2025 14:24:53 GMT",
            "file_size": 21750,
            "files_count": 30,
            "id": "5RnDqwLuANmDKRqFhkgJsh",
            "message_id": "3542fd2d-e8f7-438f-b018-0fd49176728a",
            "status": "queued",
            "type": "workouts_archive_upload",
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
        "status": "success"
      }

    :statuscode 200: ``success``
    :statuscode 400: ``invalid task type``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    """
    if task_type not in TASK_TYPES:
        return InvalidPayloadErrorResponse("invalid task type", "invalid")

    params = request.args.copy()
    page = int(params.get("page", 1))

    queued_tasks_pagination = (
        db.session.query(UserTask, User)  # type: ignore
        .join(User, User.id == UserTask.user_id)
        .filter(*USERS_QUEUED_TASKS_FILTERS, UserTask.task_type == task_type)
        .order_by(UserTask.created_at.desc())
        .paginate(page=page, per_page=TASKS_PER_PAGE, error_out=False)
    )

    return {
        "queued_tasks": [
            task.serialize(
                current_user=auth_user, for_admin=True, task_user=task_user
            )
            for task, task_user in queued_tasks_pagination.items
        ],
        "status": "success",
        "pagination": {
            "has_next": queued_tasks_pagination.has_next,
            "has_prev": queued_tasks_pagination.has_prev,
            "page": queued_tasks_pagination.page,
            "pages": queued_tasks_pagination.pages,
            "total": queued_tasks_pagination.total,
        },
    }
