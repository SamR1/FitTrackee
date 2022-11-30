from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import and_, or_

from fittrackee.oauth2.server import require_auth
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.responses import HttpResponse, handle_error_and_return_response
from fittrackee.users.models import User

from .models import Workout
from .utils.visibility import get_workout_user_status

timeline_blueprint = Blueprint('timeline', __name__)

DEFAULT_WORKOUTS_PER_PAGE = 5


@timeline_blueprint.route('/timeline', methods=['GET'])
@require_auth(scopes=['workouts:read'])
def get_user_timeline(auth_user: User) -> Union[Dict, HttpResponse]:
    try:
        params = request.args.copy()
        page = int(params.get('page', 1))
        local_following_users_id = []
        remote_following_users_id = []
        for user in auth_user.following:
            if user.is_remote is True:
                remote_following_users_id.append(user.id)
            else:
                local_following_users_id.append(user.id)
        workouts_pagination = (
            Workout.query.filter(
                or_(
                    Workout.user_id == auth_user.id,
                    and_(
                        Workout.user_id.in_(local_following_users_id),
                        Workout.workout_visibility.in_(
                            [
                                PrivacyLevel.FOLLOWERS,
                                PrivacyLevel.FOLLOWERS_AND_REMOTE,
                            ]
                        ),
                    ),
                    and_(
                        Workout.user_id.in_(remote_following_users_id),
                        Workout.workout_visibility
                        == PrivacyLevel.FOLLOWERS_AND_REMOTE,
                    ),
                    Workout.workout_visibility == PrivacyLevel.PUBLIC,
                )
            )
            .order_by(
                Workout.workout_date.desc(),
            )
            .paginate(
                page=page, per_page=DEFAULT_WORKOUTS_PER_PAGE, error_out=False
            )
        )
        workouts = workouts_pagination.items
        return {
            'status': 'success',
            'data': {
                'workouts': [
                    workout.serialize(
                        get_workout_user_status(workout, auth_user)
                    )
                    for workout in workouts
                ]
            },
            'pagination': {
                'has_next': workouts_pagination.has_next,
                'has_prev': workouts_pagination.has_prev,
                'page': workouts_pagination.page,
                'pages': workouts_pagination.pages,
                'total': workouts_pagination.total,
            },
        }
    except Exception as e:
        return handle_error_and_return_response(e)
