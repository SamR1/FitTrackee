import json
from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import and_, asc, desc, exc, or_

from fittrackee import db
from fittrackee.comments.models import Comment
from fittrackee.oauth2.server import require_auth
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.responses import (
    HttpResponse,
    NotFoundErrorResponse,
    handle_error_and_return_response,
)

from .models import Notification, User

notifications_blueprint = Blueprint("notifications", __name__)


DEFAULT_NOTIFICATION_PER_PAGE = 5


@notifications_blueprint.route('/notifications', methods=['GET'])
@require_auth(scopes=["notifications:read"])
def get_auth_user_notifications(auth_user: User) -> Dict:
    params = request.args.copy()
    page = int(params.get('page', 1))
    order = params.get('order', 'desc')
    read_status = params.get('read_status')
    event_type = params.get('type')

    blocked_users = auth_user.get_blocked_user_ids()
    blocked_by_users = auth_user.get_blocked_by_user_ids()
    (
        local_following_ids,
        remote_following_ids,
    ) = auth_user.get_following_user_ids()
    notifications_pagination = (
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
            Notification.from_user_id.not_in(blocked_users),
            (
                Notification.marked_as_read == json.loads(read_status)
                if read_status is not None
                else True
            ),
            (
                or_(
                    (
                        and_(
                            (
                                or_(
                                    Notification.event_type.not_in(
                                        ['workout_comment', 'comment_reply']
                                    ),
                                    and_(
                                        Notification.event_type.in_(
                                            [
                                                'workout_comment',
                                                'comment_reply',
                                            ]
                                        ),
                                        Notification.from_user_id.not_in(
                                            blocked_by_users
                                        ),
                                        or_(
                                            Comment.text_visibility
                                            == PrivacyLevel.PUBLIC,
                                            and_(
                                                Comment.text_visibility.in_(
                                                    [
                                                        PrivacyLevel.FOLLOWERS,
                                                        PrivacyLevel.FOLLOWERS_AND_REMOTE,  # noqa
                                                    ]
                                                ),
                                                Notification.from_user_id.in_(
                                                    local_following_ids
                                                ),
                                            ),
                                            and_(
                                                Comment.text_visibility
                                                == PrivacyLevel.FOLLOWERS_AND_REMOTE,  # noqa
                                                Notification.from_user_id.in_(
                                                    remote_following_ids
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
                            ['report', 'suspension_appeal']
                        )
                    ),
                )
            ),
            Notification.event_type == event_type if event_type else True,
        )
        .order_by(
            asc(Notification.created_at)
            if order == 'asc'
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
    "/notifications/<int:notification_id>", methods=["PATCH"]
)
@require_auth(scopes=["notifications:write"])
def update_user_notifications(
    auth_user: User, notification_id: int
) -> Union[Dict, HttpResponse]:
    notification = Notification.query.filter_by(
        id=notification_id, to_user_id=auth_user.id
    ).first()
    if not notification:
        return NotFoundErrorResponse(
            message=f"notification not found (id: {notification_id})"
        )

    params = request.get_json()
    read_status = params.get('read_status')

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
    (
        local_following_ids,
        remote_following_ids,
    ) = auth_user.get_following_user_ids()
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
                                    Notification.event_type.not_in(
                                        ['workout_comment', 'comment_reply']
                                    ),
                                    and_(
                                        Notification.event_type.in_(
                                            [
                                                'workout_comment',
                                                'comment_reply',
                                            ]
                                        ),
                                        Notification.from_user_id.not_in(
                                            auth_user.get_blocked_by_user_ids()
                                        ),
                                        or_(
                                            Comment.text_visibility
                                            == PrivacyLevel.PUBLIC,
                                            and_(
                                                Comment.text_visibility.in_(
                                                    [
                                                        PrivacyLevel.FOLLOWERS,
                                                        PrivacyLevel.FOLLOWERS_AND_REMOTE,  # noqa
                                                    ]
                                                ),
                                                Notification.from_user_id.in_(
                                                    local_following_ids
                                                ),
                                            ),
                                            and_(
                                                Comment.text_visibility
                                                == PrivacyLevel.FOLLOWERS_AND_REMOTE,  # noqa
                                                Notification.from_user_id.in_(
                                                    remote_following_ids
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
                            ['report', 'suspension_appeal']
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
    params = request.get_json(silent=True)
    event_type = params.get('type') if params else None
    try:
        Notification.query.filter(
            Notification.to_user_id == auth_user.id,
            Notification.marked_as_read == False,  # noqa
            (
                (Notification.event_type == event_type)
                if event_type is not None
                else True
            ),
        ).update(
            {Notification.marked_as_read: True}, synchronize_session=False
        )
        db.session.commit()
    except Exception as e:
        return handle_error_and_return_response(e, db=db)
    return {"status": "success"}
