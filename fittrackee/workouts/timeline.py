from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import and_, or_

from fittrackee.oauth2.server import require_auth
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.responses import HttpResponse, handle_error_and_return_response
from fittrackee.users.models import User

from .models import Workout

timeline_blueprint = Blueprint('timeline', __name__)

DEFAULT_WORKOUTS_PER_PAGE = 5


@timeline_blueprint.route('/timeline', methods=['GET'])
@require_auth(scopes=['workouts:read'])
def get_user_timeline(auth_user: User) -> Union[Dict, HttpResponse]:
    try:
        params = request.args.copy()
        page = int(params.get('page', 1))
        following_ids = auth_user.get_following_user_ids()
        blocked_users = auth_user.get_blocked_user_ids()
        blocked_by_users = auth_user.get_blocked_by_user_ids()
        workouts_pagination = (
            Workout.query.join(
                User,
                Workout.user_id == User.id,
            )
            .filter(
                or_(
                    # get all authenticated user workouts
                    Workout.user_id == auth_user.id,
                    # gel followed users workouts, that are not suspended
                    # and user is not blocked
                    and_(
                        Workout.suspended_at == None,  # noqa
                        and_(
                            Workout.user_id.in_(following_ids),
                            Workout.user_id.not_in(
                                blocked_users + blocked_by_users
                            ),
                            Workout.workout_visibility.in_(
                                [PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC]
                            ),
                        ),
                    ),
                ),
                User.suspended_at == None,  # noqa
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
                    workout.serialize(user=auth_user) for workout in workouts
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
