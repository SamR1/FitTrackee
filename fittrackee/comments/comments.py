from datetime import datetime
from typing import Dict, Optional, Tuple, Union

from flask import Blueprint, current_app, request
from sqlalchemy import exc

from fittrackee import db
from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.tasks.inbox import send_to_remote_inbox
from fittrackee.federation.utils import sending_activities_allowed
from fittrackee.oauth2.server import require_auth
from fittrackee.privacy_levels import PrivacyLevel, can_view
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import User
from fittrackee.utils import clean_input, decode_short_id
from fittrackee.workouts.models import Workout

from .decorators import check_workout_comment
from .models import WorkoutComment, get_comments

comments_blueprint = Blueprint('comments', __name__)


@comments_blueprint.route(
    "/workouts/<string:workout_short_id>/comments", methods=["POST"]
)
@require_auth(scopes=["workouts:write"])
def add_workout_comment(
    auth_user: User, workout_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    comment_data = request.get_json()
    if (
        not comment_data
        or not comment_data.get('text')
        or not comment_data.get('text_visibility')
    ):
        return InvalidPayloadErrorResponse()
    try:
        workout_uuid = decode_short_id(workout_short_id)
        workout = Workout.query.filter_by(uuid=workout_uuid).first()
        if not workout:
            return NotFoundErrorResponse(
                f"workout not found (id: {workout_short_id})"
            )

        if not can_view(workout, 'workout_visibility', auth_user):
            return NotFoundErrorResponse(
                f"workout not found (id: {workout_short_id})"
            )

        reply_to = comment_data.get('reply_to')
        workout_comment = None
        if reply_to:
            workout_comment = WorkoutComment.query.filter_by(
                uuid=decode_short_id(reply_to)
            ).first()
            if not workout_comment:
                return InvalidPayloadErrorResponse("'reply_to' is invalid")

        new_comment = WorkoutComment(
            user_id=auth_user.id,
            workout_id=workout.id,
            text=clean_input(comment_data['text']),
            text_visibility=PrivacyLevel(comment_data['text_visibility']),
            reply_to=workout_comment.id if workout_comment else None,
        )
        db.session.add(new_comment)
        db.session.flush()
        new_comment.create_mentions()
        if sending_activities_allowed(new_comment.text_visibility):
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
            recipients = auth_user.get_followers_shared_inboxes_as_list()
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
    "/workouts/<string:workout_short_id>/comments/<string:comment_short_id>",
    methods=["GET"],
)
@require_auth(scopes=['workouts:read'], optional_auth_user=True)
@check_workout_comment(check_owner=False)
def get_workout_comment(
    auth_user: Optional[User], workout_comment: WorkoutComment
) -> Union[Tuple[Dict, int], HttpResponse]:
    return (
        {
            'status': 'success',
            'comment': workout_comment.serialize(auth_user),
        },
        200,
    )


@comments_blueprint.route(
    "/workouts/<string:workout_short_id>/comments", methods=["GET"]
)
@require_auth(scopes=['workouts:read'], optional_auth_user=True)
def get_workout_comments(
    auth_user: Optional[User], workout_short_id: str
) -> Union[Dict, HttpResponse]:
    workout_uuid = decode_short_id(workout_short_id)
    workout = Workout.query.filter_by(uuid=workout_uuid).first()
    if not workout:
        return NotFoundErrorResponse(
            f"workout not found (id: {workout_short_id})"
        )

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
    "/workouts/<string:workout_short_id>/comments/<string:comment_short_id>",
    methods=["DELETE"],
)
@require_auth(scopes=['workouts:write'])
@check_workout_comment()
def delete_workout_comment(
    auth_user: User, workout_comment: WorkoutComment
) -> Union[Tuple[Dict, int], HttpResponse]:
    try:
        if sending_activities_allowed(workout_comment.text_visibility):
            note_activity = workout_comment.get_activity(
                activity_type='Delete'
            )
            recipients = auth_user.get_followers_shared_inboxes_as_list()
            if recipients:
                send_to_remote_inbox.send(
                    sender_id=auth_user.actor.id,
                    activity=note_activity,
                    recipients=recipients,
                )

        db.session.delete(workout_comment)
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
    "/workouts/<string:workout_short_id>/comments/<string:comment_short_id>",
    methods=['PATCH'],
)
@require_auth(scopes=['workouts:write'])
@check_workout_comment()
def update_workout_comment(
    auth_user: User, workout_comment: WorkoutComment
) -> Union[Dict, HttpResponse]:
    comment_data = request.get_json()
    if not comment_data or not comment_data.get('text'):
        return InvalidPayloadErrorResponse()

    try:
        workout_comment.text = clean_input(comment_data['text'])
        workout_comment.modification_date = datetime.utcnow()
        workout_comment.update_mentions()
        db.session.commit()

        if current_app.config[
            'federation_enabled'
        ] and workout_comment.text_visibility in (
            PrivacyLevel.PUBLIC,
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
        ):
            recipients = auth_user.get_followers_shared_inboxes_as_list()
            if recipients:
                note_activity = workout_comment.get_activity(
                    activity_type='Update'
                )
                send_to_remote_inbox.send(
                    sender_id=auth_user.actor.id,
                    activity=note_activity,
                    recipients=recipients,
                )

        return {
            'status': 'success',
            'comment': workout_comment.serialize(auth_user),
        }

    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e)
