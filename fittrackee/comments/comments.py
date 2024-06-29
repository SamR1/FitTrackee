from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Union

from flask import Blueprint, current_app, request
from sqlalchemy import exc

from fittrackee import db
from fittrackee.administration.models import AdminActionAppeal
from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.tasks.inbox import send_to_remote_inbox
from fittrackee.oauth2.server import require_auth
from fittrackee.privacy_levels import PrivacyLevel, can_view
from fittrackee.responses import (
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import User
from fittrackee.utils import clean_input, decode_short_id
from fittrackee.workouts.decorators import check_workout
from fittrackee.workouts.models import Workout

from .decorators import check_workout_comment
from .models import Comment, CommentLike, get_comments

comments_blueprint = Blueprint('comments', __name__)


def get_all_recipients(
    user: User,
    comment: Comment,
    deleted_mentioned_users: Optional[Set] = None,
) -> List[str]:
    recipients = user.get_followers_shared_inboxes_as_list()
    mentions = [
        user.actor.shared_inbox_url for user in comment.remote_mentions.all()
    ]
    if deleted_mentioned_users is None:
        deleted_mentioned_users = set()
    deleted_mentions = [
        user.actor.shared_inbox_url for user in deleted_mentioned_users
    ]
    return list(set(recipients + mentions + deleted_mentions))


def sending_comment_activities_allowed(
    comment: Comment, deleted_mentioned_users: Optional[Set] = None
) -> bool:
    if deleted_mentioned_users is None:
        deleted_mentioned_users = set()
    return current_app.config['FEDERATION_ENABLED'] and (
        comment.has_remote_mentions
        or len(deleted_mentioned_users) > 0
        or comment.text_visibility
        in (
            PrivacyLevel.PUBLIC,
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
    )


@comments_blueprint.route(
    "/workouts/<string:workout_short_id>/comments", methods=["POST"]
)
@require_auth(scopes=["workouts:write"])
@check_workout(only_owner=False, as_data=False)
def add_workout_comment(
    auth_user: User, workout: Workout, workout_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    comment_data = request.get_json()
    if (
        not comment_data
        or not comment_data.get('text')
        or not comment_data.get('text_visibility')
    ):
        return InvalidPayloadErrorResponse()
    try:
        reply_to = comment_data.get('reply_to')
        comment = None
        if reply_to:
            comment = Comment.query.filter(
                Comment.uuid == decode_short_id(reply_to),
                Comment.user_id.not_in(auth_user.get_blocked_by_user_ids()),
            ).first()
            if (
                not comment
                or comment.suspended_at
                or not can_view(comment, "text_visibility", auth_user)
            ):
                return InvalidPayloadErrorResponse("'reply_to' is invalid")

        new_comment = Comment(
            user_id=auth_user.id,
            workout_id=workout.id,
            text=clean_input(comment_data['text']),
            text_visibility=PrivacyLevel(comment_data['text_visibility']),
            reply_to=comment.id if comment else None,
        )
        db.session.add(new_comment)
        db.session.flush()
        new_comment.create_mentions()
        if sending_comment_activities_allowed(new_comment):
            new_comment.ap_id = (
                f'{auth_user.actor.activitypub_id}/'
                f'workouts/{workout.short_id}/'
                f'comments/{new_comment.short_id}'
            )
            new_comment.remote_url = (
                f'https://{auth_user.actor.domain.name}/'
                f'workouts/{workout.short_id}/'
                f'comments/{new_comment.short_id}'
            )
            note_activity = new_comment.get_activity(activity_type='Create')
            recipients = get_all_recipients(auth_user, new_comment)
            if recipients:
                send_to_remote_inbox.send(
                    sender_id=auth_user.actor.id,
                    activity=note_activity,
                    recipients=recipients,
                )
        db.session.commit()

        return (
            {
                'status': 'created',
                'comment': new_comment.serialize(auth_user),
            },
            201,
        )
    except InvalidVisibilityException as e:
        return InvalidPayloadErrorResponse(message=str(e))
    except (exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(
            error=e,
            message='Error during comment save.',
            status='fail',
            db=db,
        )


@comments_blueprint.route(
    "/comments/<string:comment_short_id>", methods=["GET"]
)
@require_auth(scopes=["workouts:read"], optional_auth_user=True)
@check_workout_comment(only_owner=False)
def get_workout_comment(
    auth_user: Optional[User], comment: Comment
) -> Union[Tuple[Dict, int], HttpResponse]:
    return (
        {
            'status': 'success',
            'comment': comment.serialize(auth_user, get_parent_comment=True),
        },
        200,
    )


@comments_blueprint.route(
    "/workouts/<string:workout_short_id>/comments", methods=["GET"]
)
@require_auth(scopes=['workouts:read'], optional_auth_user=True)
@check_workout(only_owner=False, as_data=False)
def get_workout_comments(
    auth_user: Optional[User], workout: Workout, workout_short_id: str
) -> Union[Dict, HttpResponse]:
    try:
        comments = get_comments(
            workout_id=workout.id,
            user=auth_user,
        )
        return {
            'status': 'success',
            'data': {
                'comments': [
                    comment.serialize(auth_user) for comment in comments
                ]
            },
        }
    except Exception as e:
        return handle_error_and_return_response(e)


@comments_blueprint.route(
    "/comments/<string:comment_short_id>", methods=["DELETE"]
)
@require_auth(scopes=["workouts:write"])
@check_workout_comment()
def delete_workout_comment(
    auth_user: User, comment: Comment
) -> Union[Tuple[Dict, int], HttpResponse]:
    try:
        if sending_comment_activities_allowed(comment):
            note_activity = comment.get_activity(activity_type='Delete')
            recipients = get_all_recipients(auth_user, comment)
            if recipients:
                send_to_remote_inbox.send(
                    sender_id=auth_user.actor.id,
                    activity=note_activity,
                    recipients=recipients,
                )

        db.session.delete(comment)
        db.session.commit()
        return {'status': 'no content'}, 204
    except (
        exc.IntegrityError,
        exc.OperationalError,
        ValueError,
        OSError,
    ) as e:
        return handle_error_and_return_response(e, db=db)


@comments_blueprint.route(
    "/comments/<string:comment_short_id>", methods=["PATCH"]
)
@require_auth(scopes=["workouts:write"])
@check_workout_comment()
def update_workout_comment(
    auth_user: User, comment: Comment
) -> Union[Dict, HttpResponse]:
    comment_data = request.get_json()
    if not comment_data or not comment_data.get('text'):
        return InvalidPayloadErrorResponse()

    try:
        comment.text = clean_input(comment_data['text'])
        comment.modification_date = datetime.utcnow()
        deleted_mentioned_users = comment.update_mentions()
        db.session.commit()

        if sending_comment_activities_allowed(
            comment, deleted_mentioned_users
        ):
            recipients = get_all_recipients(
                auth_user, comment, deleted_mentioned_users
            )
            if recipients:
                note_activity = comment.get_activity(activity_type='Update')
                send_to_remote_inbox.send(
                    sender_id=auth_user.actor.id,
                    activity=note_activity,
                    recipients=recipients,
                )

        return {
            'status': 'success',
            'comment': comment.serialize(auth_user),
        }

    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e)


@comments_blueprint.route(
    "/comments/<string:comment_short_id>/like", methods=["POST"]
)
@require_auth(scopes=["workouts:write"])
@check_workout_comment(only_owner=False)
def like_comment(
    auth_user: User, comment: Comment
) -> Union[Tuple[Dict, int], HttpResponse]:
    if comment.suspended_at:
        return ForbiddenErrorResponse()
    try:
        like = CommentLike(user_id=auth_user.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()

        if current_app.config['FEDERATION_ENABLED'] and comment.user.is_remote:
            like_activity = like.get_activity()
            send_to_remote_inbox.send(
                sender_id=auth_user.actor.id,
                activity=like_activity,
                recipients=[comment.user.actor.shared_inbox_url],
            )
    except exc.IntegrityError:
        db.session.rollback()
    return {
        'status': 'success',
        'comment': comment.serialize(auth_user),
    }, 200


@comments_blueprint.route(
    "/comments/<string:comment_short_id>/like/undo",
    methods=["POST"],
)
@require_auth(scopes=["workouts:write"])
@check_workout_comment(only_owner=False)
def undo_comment_like(
    auth_user: User, comment: Comment
) -> Union[Tuple[Dict, int], HttpResponse]:
    like = CommentLike.query.filter_by(
        user_id=auth_user.id, comment_id=comment.id
    ).first()
    if like:
        db.session.delete(like)
        db.session.commit()

        if current_app.config['FEDERATION_ENABLED'] and comment.user.is_remote:
            undo_activity = like.get_activity(is_undo=True)
            send_to_remote_inbox.send(
                sender_id=auth_user.actor.id,
                activity=undo_activity,
                recipients=[comment.user.actor.shared_inbox_url],
            )

    return {
        'status': 'success',
        'comment': comment.serialize(auth_user),
    }, 200


@comments_blueprint.route(
    "/comments/<string:comment_short_id>/suspension/appeal",
    methods=["POST"],
)
@require_auth(scopes=["workouts:write"])
@check_workout_comment(only_owner=True)
def appeal_comment_suspension(
    auth_user: User, comment: Comment
) -> Union[Tuple[Dict, int], HttpResponse]:
    if not comment.suspended_at:
        return InvalidPayloadErrorResponse("workout comment is not suspended")
    suspension_action = comment.suspension_action
    if not suspension_action:
        return InvalidPayloadErrorResponse("workout comment has no suspension")

    text = request.get_json().get("text")
    if not text:
        return InvalidPayloadErrorResponse("no text provided")

    try:
        appeal = AdminActionAppeal(
            action_id=suspension_action.id, user_id=auth_user.id, text=text
        )
        db.session.add(appeal)
        db.session.commit()
        return {"status": "success"}, 201

    except exc.IntegrityError:
        return InvalidPayloadErrorResponse("you can appeal only once")
    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)
