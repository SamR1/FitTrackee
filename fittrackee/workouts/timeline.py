from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import and_, or_

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.responses import HttpResponse, handle_error_and_return_response
from fittrackee.users.decorators import authenticate
from fittrackee.users.models import User

from .models import Workout
from .utils.visibility import get_workout_user_status

timeline_blueprint = Blueprint('timeline', __name__)

DEFAULT_WORKOUTS_PER_PAGE = 5


@timeline_blueprint.route('/timeline', methods=['GET'])
@authenticate
def get_user_timeline(auth_user: User) -> Union[Dict, HttpResponse]:
    try:
        params = request.args.copy()
        page = int(params.get('page', 1))
        workouts_pagination = (
            Workout.query.filter(
                or_(
                    Workout.user_id == auth_user.id,
                    and_(
                        Workout.user_id.in_(
                            [user.id for user in auth_user.following]
                        ),
                        Workout.workout_visibility == PrivacyLevel.FOLLOWERS,
                    ),
                    Workout.workout_visibility == PrivacyLevel.PUBLIC,
                )
            )
            .order_by(
                Workout.workout_date.desc(),
            )
            .paginate(page, DEFAULT_WORKOUTS_PER_PAGE, False)
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
