from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import and_, asc, desc, exc, or_

from fittrackee import db
from fittrackee.comments.models import Comment
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    HttpResponse,
    NotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.utils import decode_short_id
from fittrackee.visibility_levels import VisibilityLevel

from .models import Notification, User

notifications_blueprint = Blueprint("notifications", __name__)


DEFAULT_NOTIFICATION_PER_PAGE = 5


@notifications_blueprint.route("/notifications", methods=["GET"])
@require_auth(scopes=["notifications:read"])
def get_auth_user_notifications(auth_user: User) -> Dict:
    """
    Get authenticated user notifications.

    **Scope**: ``notifications:read``

    **Example requests**:

    - without parameters:

    .. sourcecode:: http

      GET /api/notifications HTTP/1.1

    - with some query parameters:

    .. sourcecode:: http

      GET /api/notifications?page=2&status=unread  HTTP/1.1

    **Example responses**:

    - returning at least one notification:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "notifications": [
            {
              "created_at": "Wed, 04 Dec 2024 10:06:35 GMT",
              "from": {
                "created_at": "Wed, 04 Dec 2024 09:07:08 GMT",
                "followers": 0,
                "following": 0,
                "follows": "pending",
                "is_followed_by": "false",
                "nb_workouts": 0,
                "picture": true,
                "role": "admin",
                "suspended_at": null,
                "username": "admin"
              },
              "id": "be26f35a-1239-44ff-a012-12fb835fa26c",
              "marked_as_read": false,
              "type": "follow_request"
            }
          ],
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 1,
            "total": 1
          },
          "status": "success"
        }

    - returning no notifications

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "notifications": [],
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 0,
            "total": 0
          },
          "status": "success"
        }

    :query integer page: page if using pagination (default: 1)
    :query string order: sorting order: ``asc``, ``desc`` (default: ``desc``)
    :query string status: notification read status (``read``, ``unread``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    """
    params = request.args.copy()
    page = int(params.get("page", 1))
    order = params.get("order", "desc")
    status = params.get("status")
    marked_as_read = None
    if status == "read":
        marked_as_read = True
    if status == "unread":
        marked_as_read = False
    event_type = params.get("type")

    blocked_users = auth_user.get_blocked_user_ids()
    blocked_by_users = auth_user.get_blocked_by_user_ids()
    following_ids = auth_user.get_following_user_ids()

    filters = [
        Notification.to_user_id == auth_user.id,
        Notification.from_user_id.not_in(blocked_users),
        or_(
            (
                and_(
                    (
                        or_(
                            Notification.event_type != "workout_comment",
                            and_(
                                Notification.event_type == "workout_comment",
                                Notification.from_user_id.not_in(
                                    blocked_by_users
                                ),
                                or_(
                                    Comment.text_visibility
                                    == VisibilityLevel.PUBLIC,
                                    and_(
                                        Comment.text_visibility
                                        == VisibilityLevel.FOLLOWERS,
                                        Notification.from_user_id.in_(
                                            following_ids
                                        ),
                                    ),
                                ),
                            ),
                        )
                    ),
                    User.suspended_at == None,  # noqa
                )
            ),
            (Notification.event_type.in_(["report", "suspension_appeal"])),
        ),
    ]
    if marked_as_read is not None:
        filters.append(Notification.marked_as_read == marked_as_read)
    if event_type:
        filters.append(Notification.event_type == event_type)
    notifications_pagination = (
        Notification.query.join(
            User,
            Notification.from_user_id == User.id,
        )
        .outerjoin(
            Comment,
            Notification.event_object_id == Comment.id,
        )
        .filter(*filters)
        .order_by(
            asc(Notification.created_at)
            if order == "asc"
            else desc(Notification.created_at)
        )
        .paginate(
            page=page, per_page=DEFAULT_NOTIFICATION_PER_PAGE, error_out=False
        )
    )
    notifications = notifications_pagination.items

    return {
        "status": "success",
        "notifications": [
            notification.serialize() for notification in notifications
        ],
        "pagination": {
            "has_next": notifications_pagination.has_next,
            "has_prev": notifications_pagination.has_prev,
            "page": notifications_pagination.page,
            "pages": notifications_pagination.pages,
            "total": notifications_pagination.total,
        },
    }


@notifications_blueprint.route(
    "/notifications/<string:notification_id>", methods=["PATCH"]
)
@require_auth(scopes=["notifications:write"])
def update_user_notifications(
    auth_user: User, notification_id: str
) -> Union[Dict, HttpResponse]:
    """
    Update authenticated user notification read status.

    **Scope**: ``notifications:write``

    **Example request**:

    .. sourcecode:: http

      PATCH /api/notifications/be26f35a-1239-44ff-a012-12fb835fa26c HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

       {
          "notification": {
            "created_at": "Wed, 04 Dec 2024 10:06:35 GMT",
            "from": {
              "created_at": "Wed, 04 Dec 2024 09:07:08 GMT",
              "followers": 0,
              "following": 0,
              "follows": "pending",
              "is_followed_by": "false",
              "nb_workouts": 0,
              "picture": true,
              "role": "admin",
              "suspended_at": null,
              "username": "admin"
            },
            "id": "be26f35a-1239-44ff-a012-12fb835fa26c",
            "marked_as_read": true,
            "type": "follow_request"
          },
          "status": "success"
        }

    :param string notification_id: notification short id

    :<json boolean read_status: notification read status

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``notification not found``
    :statuscode 500:
        - ``error, please try again or contact the administrator``
    """
    notification = Notification.query.filter_by(
        uuid=decode_short_id(notification_id), to_user_id=auth_user.id
    ).first()
    if not notification:
        return NotFoundErrorResponse(
            message=f"notification not found (id: {notification_id})"
        )

    params = request.get_json()
    read_status = params.get("read_status")

    try:
        if read_status is not None:
            notification.marked_as_read = read_status
            db.session.commit()

        return {"status": "success", "notification": notification.serialize()}

    except (exc.IntegrityError, exc.StatementError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@notifications_blueprint.route("/notifications/unread", methods=["GET"])
@require_auth(scopes=["notifications:read"])
def get_status(auth_user: User) -> Dict:
    """
    Get if unread notifications exist for authenticated user.

    **Scope**: ``notifications:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/notifications/unread HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

       {
          "status": "success",
          "unread": false
        }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    """
    unread_notifications = (
        Notification.query.join(
            User,
            Notification.from_user_id == User.id,
        )
        .outerjoin(
            Comment,
            Notification.event_object_id == Comment.id,
        )
        .filter(
            Notification.to_user_id == auth_user.id,
            Notification.from_user_id.not_in(auth_user.get_blocked_user_ids()),
            (
                or_(
                    (
                        and_(
                            (
                                or_(
                                    Notification.event_type
                                    != "workout_comment",
                                    and_(
                                        Notification.event_type
                                        == "workout_comment",
                                        Notification.from_user_id.not_in(
                                            auth_user.get_blocked_by_user_ids()
                                        ),
                                        or_(
                                            Comment.text_visibility
                                            == VisibilityLevel.PUBLIC,
                                            and_(
                                                Comment.text_visibility
                                                == VisibilityLevel.FOLLOWERS,
                                                Notification.from_user_id.in_(
                                                    auth_user.get_following_user_ids()
                                                ),
                                            ),
                                        ),
                                    ),
                                )
                            ),
                            User.suspended_at == None,  # noqa
                        )
                    ),
                    (
                        Notification.event_type.in_(
                            ["report", "suspension_appeal"]
                        )
                    ),
                )
            ),
            Notification.marked_as_read == False,  # noqa
        )
        .count()
    )
    return {
        "status": "success",
        "unread": unread_notifications > 0,
    }


@notifications_blueprint.route(
    "/notifications/mark-all-as-read", methods=["POST"]
)
@require_auth(scopes=["notifications:write"])
def mark_all_as_read(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Mark all authenticated user notifications as read.

    **Scope**: ``notifications:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/notifications/mark-all-as-read HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

       {
          "status": "success"
        }

    :<json boolean type: notification type (optional)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 500:
        - ``error, please try again or contact the administrator``
    """
    params = request.get_json(silent=True)
    event_type = params.get("type") if params else None
    try:
        filters = [
            Notification.to_user_id == auth_user.id,
            Notification.marked_as_read == False,  # noqa
        ]
        if event_type is not None:
            filters.append(Notification.event_type == event_type)
        Notification.query.filter(*filters).update(
            {Notification.marked_as_read: True}, synchronize_session=False
        )
        db.session.commit()
    except Exception as e:
        return handle_error_and_return_response(e, db=db)
    return {"status": "success"}


@notifications_blueprint.route("/notifications/types", methods=["GET"])
@require_auth(scopes=["notifications:read"])
def get_notification_types(auth_user: User) -> Dict:
    """
    Get types of notifications received by authenticated user.

    **Scope**: ``notifications:read``

    **Example requests**:

    - without parameters:

    .. sourcecode:: http

      GET /api/notifications/types HTTP/1.1

    - with query parameter:

    .. sourcecode:: http

      GET /api/notifications/types?status=unread  HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

       {
          "notification_types": [
            "mention"
          ],
          "status": "success"
       }

    :query string status: notification read status (``read``, ``unread``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    """
    status = request.args.copy().get("status")
    marked_as_read = None
    if status == "read":
        marked_as_read = True
    if status == "unread":
        marked_as_read = False
    filters = [Notification.to_user_id == auth_user.id]
    if marked_as_read is not None:
        filters.append(Notification.marked_as_read == marked_as_read)
    notification_types = (
        db.session.query(Notification.event_type).filter(*filters).distinct()
    )
    return {
        "notification_types": [
            notification_type[0] for notification_type in notification_types
        ],
        "status": "success",
    }
