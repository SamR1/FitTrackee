from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import and_, or_

from fittrackee.oauth2.server import require_auth
from fittrackee.responses import HttpResponse, handle_error_and_return_response
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel

from .models import Workout

timeline_blueprint = Blueprint("timeline", __name__)

DEFAULT_WORKOUTS_PER_PAGE = 5


@timeline_blueprint.route("/timeline", methods=["GET"])
@require_auth(scopes=["workouts:read"])
def get_user_timeline(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Get workouts visible to authenticated user.

    **Scope**: ``workouts:read``

    **Example requests**:

    - without parameters:

    .. sourcecode:: http

      GET /api/timeline HTTP/1.1

    - with some query parameters:

    .. sourcecode:: http

      GET /api/timeline?page=2  HTTP/1.1

    **Example responses**:

    - returning at least one workout:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "workouts": [
              {
                "ascent": null,
                "ave_cadence": null,
                "ave_hr": null,
                "ave_power": null,
                "ave_speed": 10.0,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": null,
                "description": null,
                "distance": 10.0,
                "duration": "0:17:04",
                "equipments": [],
                "id": "kjxavSTUrJvoAh2wvCeGEF",
                "map": null,
                "max_alt": null,
                "max_cadence": null,
                "max_hr": null,
                "max_power": null,
                "max_speed": 10.0,
                "min_alt": null,
                "modification_date": null,
                "moving": "0:17:04",
                "next_workout": 3,
                "notes": null,
                "pauses": null,
                "previous_workout": null,
                "records": [
                  {
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 13,
                    "record_type": "HA",
                    "sport_id": 1,
                    "user": "Sam",
                    "value": 43.97,
                    "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
                    "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
                  },
                  {
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": "0:17:04",
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "title": null,
                "user": "admin",
                "weather_end": null,
                "weather_start": null,
                "with_gpx": false,
                "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT"
              }
            ]
          },
          "status": "success"
        }

    - returning no workouts

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
            "data": {
                "workouts": []
            },
            "status": "success"
        }

    :query integer page: page if using pagination (default: 1)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    try:
        params = request.args.copy()
        page = int(params.get("page", 1))
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
                                [
                                    VisibilityLevel.FOLLOWERS,
                                    VisibilityLevel.PUBLIC,
                                ]
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
            "status": "success",
            "data": {
                "workouts": [
                    workout.serialize(user=auth_user) for workout in workouts
                ]
            },
            "pagination": {
                "has_next": workouts_pagination.has_next,
                "has_prev": workouts_pagination.has_prev,
                "page": workouts_pagination.page,
                "pages": workouts_pagination.pages,
                "total": workouts_pagination.total,
            },
        }
    except Exception as e:
        return handle_error_and_return_response(e)
