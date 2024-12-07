from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Union

from flask import Blueprint, current_app, request
from sqlalchemy import exc

from fittrackee import db
from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.tasks.inbox import send_to_remote_inbox
from fittrackee.oauth2.server import require_auth
from fittrackee.reports.models import ReportActionAppeal
from fittrackee.responses import (
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import User
from fittrackee.utils import clean_input
from fittrackee.visibility_levels import VisibilityLevel
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
            VisibilityLevel.PUBLIC,
            VisibilityLevel.FOLLOWERS_AND_REMOTE,
        )
    )


@comments_blueprint.route(
    "/workouts/<string:workout_short_id>/comments", methods=["POST"]
)
@require_auth(scopes=["workouts:write"])
@check_workout(only_owner=False, as_data=False)
def post_workout_comment(
    auth_user: User, workout: Workout, workout_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Post a comment.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/workouts/2oRDfncv6vpRkfp3yrCYHt HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "comment": {
            "created_at": "Sun, 01 Dec 2024 13:45:34 GMT",
            "id": "WJgTwtqFpnPrHYAK5eX9Pw",
            "liked": false,
            "likes_count": 0,
            "mentions": [],
            "modification_date": null,
            "suspended_at": null,
            "text": "Great!",
            "text_html": "Great!",
            "text_visibility": "private",
            "user": {
              "created_at": "Sun, 24 Nov 2024 16:52:14 GMT",
              "followers": 3,
              "following": 2,
              "nb_workouts": 10,
              "picture": true,
              "role": "user",
              "suspended_at": null,
              "username": "Sam"
            },
            "workout_id": "2oRDfncv6vpRkfp3yrCYHt"
          },
          "status": "created"
        }

    :param string workout_short_id: workout short id

    :<json string text: comment content
    :<json string text_visibility: visibility level (``public``,
           ``followers_only``, ``private``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: ``created``
    :statuscode 400:
        - ``invalid payload``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``workout not found``
    :statuscode 500: ``Error during comment save.``
    """
    comment_data = request.get_json()
    if (
        not comment_data
        or not comment_data.get('text')
        or not comment_data.get('text_visibility')
    ):
        return InvalidPayloadErrorResponse()
    try:
        new_comment = Comment(
            user_id=auth_user.id,
            workout_id=workout.id,
            text=clean_input(comment_data['text']),
            text_visibility=VisibilityLevel(comment_data['text_visibility']),
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
    """
    Get comment.

    **Scope**: ``workouts:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/2oRDfncv6vpRkfp3yrCYHt/comment HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "comment": {
            "created_at": "Sun, 01 Dec 2024 13:45:34 GMT",
            "id": "T2zeeUXvuy3PLA8MeeUFyk",
            "liked": false,
            "likes_count": 0,
            "mentions": [],
            "modification_date": null,
            "suspended_at": null,
            "text": "Nice!",
            "text_html": "Nice!",
            "text_visibility": "private",
            "user": {
              "created_at": "Sun, 24 Nov 2024 16:52:14 GMT",
              "followers": 3,
              "following": 2,
              "nb_workouts": 10,
              "picture": true,
              "role": "user",
              "suspended_at": null,
              "username": "Sam"
            },
            "workout_id": null
          },
          "status": "success"
        }

    :param string comment_short_id: comment short id

    :reqheader Authorization: OAuth 2.0 Bearer Token for comment with
        ``private`` and ``followers_only`` visibility

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``workout comment not found``
    """
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
@check_workout(only_owner=False, as_data=False)
def get_workout_comments(
    auth_user: Optional[User], workout: Workout, workout_short_id: str
) -> Union[Dict, HttpResponse]:
    """
    Get workout comments.

    It returns only comments visible to authenticated user and only public
    comments when no authentication provided.

    **Scope**: ``workouts:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/2oRDfncv6vpRkfp3yrCYHt/comments HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "comments": [
              {
                "created_at": "Sun, 01 Dec 2024 13:45:34 GMT",
                "id": "WJgTwtqFpnPrHYAK5eX9Pw",
                "liked": false,
                "likes_count": 0,
                "mentions": [],
                "modification_date": null,
                "suspended_at": null,
                "text": "Great!",
                "text_html": "Great!",
                "text_visibility": "private",
                "user": {
                  "created_at": "Sun, 24 Nov 2024 16:52:14 GMT",
                  "followers": 3,
                  "following": 2,
                  "nb_workouts": 10,
                  "picture": true,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                },
                "workout_id": "2oRDfncv6vpRkfp3yrCYHt"
              }
            ]
          },
          "status": "success"
        }

    :param string workout_short_id: workout short id

    :reqheader Authorization: OAuth 2.0 Bearer Token for workout with
        ``private`` and ``followers_only`` visibility

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``workout not found``
    :statuscode 500: ``Error during comment save.``
    """
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
    """
    Delete workout comment.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      DELETE /api/comments/MzydiCYYfktG3gga2x8AfU HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :param string comment_short_id: comment short id

    :reqheader Authorization: OAuth 2.0 Bearer Token for workout with
        ``private`` and ``followers_only`` visibility

    :statuscode 204: comment deleted
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``comment not found``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
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
    """
    Update comment text.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      PATCH /api/workouts/WJgTwtqFpnPrHYAK5eX9Pw HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "comment": {
            "created_at": "Sun, 01 Dec 2024 13:45:34 GMT",
            "id": "WJgTwtqFpnPrHYAK5eX9Pw",
            "liked": false,
            "likes_count": 0,
            "mentions": [],
            "modification_date": null,
            "suspended_at": null,
            "text": "Great!",
            "text_html": "Great!",
            "text_visibility": "private",
            "user": {
              "created_at": "Sun, 24 Nov 2024 16:52:14 GMT",
              "followers": 3,
              "following": 2,
              "nb_workouts": 10,
              "picture": true,
              "role": "user",
              "suspended_at": null,
              "username": "Sam"
            },
            "workout_id": "2oRDfncv6vpRkfp3yrCYHt"
          },
          "status": "success"
        }

    :param string comment_short_id: comment short id

    :<json string text: comment content

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid payload``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``comment not found``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
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
    """
    Add a "like" to a comment.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/comments/WJgTwtqFpnPrHYAK5eX9Pw/like HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "comment": {
            "created_at": "Sun, 01 Dec 2024 13:45:34 GMT",
            "id": "WJgTwtqFpnPrHYAK5eX9Pw",
            "liked": true,
            "likes_count": 1,
            "mentions": [],
            "modification_date": null,
            "suspended_at": null,
            "text": "Great!",
            "text_html": "Great!",
            "text_visibility": "private",
            "user": {
              "created_at": "Sun, 24 Nov 2024 16:52:14 GMT",
              "followers": 3,
              "following": 2,
              "nb_workouts": 10,
              "picture": true,
              "role": "user",
              "suspended_at": null,
              "username": "Sam"
            },
            "workout_id": "2oRDfncv6vpRkfp3yrCYHt"
          },
          "status": "success"
        }

    :param string comment_short_id: comment short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``comment not found``
    """
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
    """
    Remove a comment "like".

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/comments/2oRDfncv6vpRkfp3yrCYHt/like/undo HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "comment": {
            "created_at": "Sun, 01 Dec 2024 13:45:34 GMT",
            "id": "WJgTwtqFpnPrHYAK5eX9Pw",
            "liked": false,
            "likes_count": 0,
            "mentions": [],
            "modification_date": null,
            "suspended_at": null,
            "text": "Great!",
            "text_html": "Great!",
            "text_visibility": "private",
            "user": {
              "created_at": "Sun, 24 Nov 2024 16:52:14 GMT",
              "followers": 3,
              "following": 2,
              "nb_workouts": 10,
              "picture": true,
              "role": "user",
              "suspended_at": null,
              "username": "Sam"
            },
            "workout_id": "2oRDfncv6vpRkfp3yrCYHt"
          },
          "status": "success"
        }

    :param string comment_short_id: comment short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``comment not found``
    """
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
    """
    Appeal comment suspension.

    Only comment author can appeal the suspension.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/comments/WJgTwtqFpnPrHYAK5eX9Pw/suspension/appeal HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

        {
          "status": "success"
        }

    :param string comment_short_id: comment short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: appeal created
    :statuscode 400:
        - ``no text provided``
        - ``you can appeal only once``
        - ``workout comment is not suspended``
        - ``workout comment has no suspension``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``comment not found``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    if not comment.suspended_at:
        return InvalidPayloadErrorResponse("workout comment is not suspended")
    suspension_action = comment.suspension_action
    if not suspension_action:
        return InvalidPayloadErrorResponse("workout comment has no suspension")

    text = request.get_json().get("text")
    if not text:
        return InvalidPayloadErrorResponse("no text provided")

    try:
        appeal = ReportActionAppeal(
            action_id=suspension_action.id, user_id=auth_user.id, text=text
        )
        db.session.add(appeal)
        db.session.commit()
        return {"status": "success"}, 201

    except exc.IntegrityError:
        return InvalidPayloadErrorResponse("you can appeal only once")
    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)
