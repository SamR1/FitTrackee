from datetime import datetime
from typing import Dict, Optional, Tuple, Union

from flask import Blueprint, request
from sqlalchemy import exc

from fittrackee import db
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
from .models import Comment, CommentLike, get_comments

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
        comment = None
        if reply_to:
            comment = Comment.query.filter_by(
                uuid=decode_short_id(reply_to)
            ).first()
            if not comment:
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
        db.session.commit()

        return (
            {
                'status': 'created',
                'comment': new_comment.serialize(auth_user),
            },
            201,
        )
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
    auth_user: Optional[User], comment: Comment
) -> Union[Tuple[Dict, int], HttpResponse]:
    return (
        {
            'status': 'success',
            'comment': comment.serialize(auth_user),
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
    auth_user: User, comment: Comment
) -> Union[Tuple[Dict, int], HttpResponse]:
    try:
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
    "/workouts/<string:workout_short_id>/comments/<string:comment_short_id>",
    methods=['PATCH'],
)
@require_auth(scopes=['workouts:write'])
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
        comment.update_mentions()
        db.session.commit()
        return {
            'status': 'success',
            'comment': comment.serialize(auth_user),
        }

    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e)


@comments_blueprint.route(
    '/workouts/<string:workout_short_id>/comments/<string:comment_short_id>'
    '/like',
    methods=['POST'],
)
@require_auth(scopes=['workouts:write'])
@check_workout_comment(check_owner=False)
def like_comment(
    auth_user: User, comment: Comment
) -> Union[Tuple[Dict, int], HttpResponse]:
    try:
        like = CommentLike(user_id=auth_user.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
    return {
        'status': 'success',
        'comment': comment.serialize(auth_user),
    }, 200


@comments_blueprint.route(
    '/workouts/<string:workout_short_id>/comments/<string:comment_short_id>'
    '/like/undo',
    methods=['POST'],
)
@require_auth(scopes=['workouts:write'])
@check_workout_comment(check_owner=False)
def undo_comment_like(
    auth_user: User, comment: Comment
) -> Union[Tuple[Dict, int], HttpResponse]:
    like = CommentLike.query.filter_by(
        user_id=auth_user.id, comment_id=comment.id
    ).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    return {
        'status': 'success',
        'comment': comment.serialize(auth_user),
    }, 200
