from datetime import datetime, timedelta
from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import func

from fittrackee import db
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    UserNotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.decorators import authenticate, authenticate_as_admin
from fittrackee.users.models import User

from .models import Sport, Workout
from .utils.convert import convert_timedelta_to_integer
from .utils.uploads import get_upload_dir_size
from .utils.workouts import get_average_speed, get_datetime_from_request_args

stats_blueprint = Blueprint('stats', __name__)


def get_workouts(
    user_name: str, filter_type: str
) -> Union[Dict, HttpResponse]:
    """
    Return user workouts by sport or by time
    """
    try:
        user = User.query.filter_by(username=user_name).first()
        if not user:
            return UserNotFoundErrorResponse()

        params = request.args.copy()
        date_from, date_to = get_datetime_from_request_args(params, user)
        sport_id = params.get('sport_id')
        time = params.get('time')

        if filter_type == 'by_sport':
            if sport_id:
                sport = Sport.query.filter_by(id=sport_id).first()
                if not sport:
                    return NotFoundErrorResponse('sport does not exist')

        workouts = (
            Workout.query.filter(
                Workout.user_id == user.id,
                Workout.workout_date >= date_from if date_from else True,
                Workout.workout_date < date_to + timedelta(seconds=1)
                if date_to
                else True,
                Workout.sport_id == sport_id if sport_id else True,
            )
            .order_by(Workout.workout_date.asc())
            .all()
        )

        workouts_list_by_sport = {}
        workouts_list_by_time = {}  # type: ignore
        for workout in workouts:
            if filter_type == 'by_sport':
                sport_id = workout.sport_id
                if sport_id not in workouts_list_by_sport:
                    workouts_list_by_sport[sport_id] = {
                        'average_speed': 0.0,
                        'nb_workouts': 0,
                        'total_distance': 0.0,
                        'total_duration': 0,
                        'total_ascent': 0.0,
                        'total_descent': 0.0,
                    }
                workouts_list_by_sport[sport_id]['nb_workouts'] += 1
                workouts_list_by_sport[sport_id][
                    'average_speed'
                ] = get_average_speed(
                    workouts_list_by_sport[sport_id]['nb_workouts'],  # type: ignore  # noqa
                    workouts_list_by_sport[sport_id]['average_speed'],
                    workout.ave_speed,
                )
                workouts_list_by_sport[sport_id]['total_distance'] += float(
                    workout.distance
                )
                workouts_list_by_sport[sport_id][
                    'total_duration'
                ] += convert_timedelta_to_integer(workout.moving)
                if workout.ascent:
                    workouts_list_by_sport[sport_id]['total_ascent'] += float(
                        workout.ascent
                    )
                if workout.descent:
                    workouts_list_by_sport[sport_id]['total_descent'] += float(
                        workout.descent
                    )

            # filter_type == 'by_time'
            else:
                if time == 'week':
                    workout_date = workout.workout_date - timedelta(
                        days=(
                            workout.workout_date.isoweekday()
                            if workout.workout_date.isoweekday() < 7
                            else 0
                        )
                    )
                    time_period = datetime.strftime(workout_date, "%Y-%m-%d")
                elif time == 'weekm':  # week start Monday
                    workout_date = workout.workout_date - timedelta(
                        days=workout.workout_date.weekday()
                    )
                    time_period = datetime.strftime(workout_date, "%Y-%m-%d")
                elif time == 'month':
                    time_period = datetime.strftime(
                        workout.workout_date, "%Y-%m"
                    )
                elif time == 'year' or not time:
                    time_period = datetime.strftime(workout.workout_date, "%Y")
                else:
                    return InvalidPayloadErrorResponse(
                        'Invalid time period.', 'fail'
                    )
                sport_id = workout.sport_id
                if time_period not in workouts_list_by_time:
                    workouts_list_by_time[time_period] = {}
                if sport_id not in workouts_list_by_time[time_period]:
                    workouts_list_by_time[time_period][sport_id] = {
                        'average_speed': 0.0,
                        'nb_workouts': 0,
                        'total_distance': 0.0,
                        'total_duration': 0,
                        'total_ascent': 0.0,
                        'total_descent': 0.0,
                    }
                workouts_list_by_time[time_period][sport_id][
                    'nb_workouts'
                ] += 1
                workouts_list_by_time[time_period][sport_id][
                    'average_speed'
                ] = get_average_speed(
                    workouts_list_by_time[time_period][sport_id][
                        'nb_workouts'
                    ],
                    workouts_list_by_time[time_period][sport_id][
                        'average_speed'
                    ],
                    workout.ave_speed,
                )
                workouts_list_by_time[time_period][sport_id][
                    'total_distance'
                ] += float(workout.distance)
                workouts_list_by_time[time_period][sport_id][
                    'total_duration'
                ] += convert_timedelta_to_integer(workout.moving)
                if workout.ascent:
                    workouts_list_by_time[time_period][sport_id][
                        'total_ascent'
                    ] += float(workout.ascent)
                if workout.descent:
                    workouts_list_by_time[time_period][sport_id][
                        'total_descent'
                    ] += float(workout.descent)
        return {
            'status': 'success',
            'data': {
                'statistics': workouts_list_by_sport
                if filter_type == 'by_sport'
                else workouts_list_by_time
            },
        }
    except Exception as e:
        return handle_error_and_return_response(e)


@stats_blueprint.route('/stats/<user_name>/by_time', methods=['GET'])
@authenticate
def get_workouts_by_time(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get workouts statistics for a user by time

    **Example requests**:

    - without parameters

    .. sourcecode:: http

      GET /api/stats/admin/by_time HTTP/1.1

    - with parameters

    .. sourcecode:: http

      GET /api/stats/admin/by_time?from=2018-01-01&to=2018-06-30&time=week
        HTTP/1.1

    **Example responses**:

    - success

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "statistics": {
            "2017": {
              "3": {
                "average_speed": 4.48,
                "nb_workouts": 2,
                "total_ascent": 203.0,
                "total_ascent": 156.0,
                "total_distance": 15.282,
                "total_duration": 12341
              }
            },
            "2019": {
              "1": {
                "average_speed": 16.99,
                "nb_workouts": 3,
                "total_ascent": 150.0,
                "total_ascent": 178.0,
                "total_distance": 47,
                "total_duration": 9960
              },
              "2": {
                "average_speed": 15.95,
                "nb_workouts": 1,
                "total_ascent": 46.0,
                "total_ascent": 78.0,
                "total_distance": 5.613,
                "total_duration": 1267
              }
            }
          }
        },
        "status": "success"
      }

    - no workouts

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
            "statistics": {}
        },
        "status": "success"
      }

    :param integer user_name: user name

    :query string from: start date (format: ``%Y-%m-%d``)
    :query string to: end date (format: ``%Y-%m-%d``)
    :query string time: time frame:

      - ``week``: week starting Sunday
      - ``weekm``: week starting Monday
      - ``month``: month
      - ``year``: year (default)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 404:
        - user does not exist

    """
    return get_workouts(user_name, 'by_time')


@stats_blueprint.route('/stats/<user_name>/by_sport', methods=['GET'])
@authenticate
def get_workouts_by_sport(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get workouts statistics for a user by sport

    **Example requests**:

    - without parameters (get stats for all sports with workouts)

    .. sourcecode:: http

      GET /api/stats/admin/by_sport HTTP/1.1

    - with sport id

    .. sourcecode:: http

      GET /api/stats/admin/by_sport?sport_id=1 HTTP/1.1

    **Example responses**:

    - success

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "statistics": {
            "1": {
              "average_speed": 16.99,
              "nb_workouts": 3,
              "total_ascent": 150.0,
              "total_ascent": 178.0,
              "total_distance": 47,
              "total_duration": 9960
            },
            "2": {
              "average_speed": 15.95,
              "nb_workouts": 1,
              "total_ascent": 46.0,
              "total_ascent": 78.0,
              "total_distance": 5.613,
              "total_duration": 1267
            },
            "3": {
              "average_speed": 4.46,
              "nb_workouts": 2,
              "total_ascent": 203.0,
              "total_ascent": 156.0,
              "total_distance": 15.282,
              "total_duration": 12341
            }
          }
        },
        "status": "success"
      }

    - no workouts

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
            "statistics": {}
        },
        "status": "success"
      }

    :param integer user_name: user name

    :query integer sport_id: sport id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 404:
        - user does not exist
        - sport does not exist

    """
    return get_workouts(user_name, 'by_sport')


@stats_blueprint.route('/stats/all', methods=['GET'])
@authenticate_as_admin
def get_application_stats(auth_user: User) -> Dict:
    """
    Get all application statistics

    **Example requests**:

    .. sourcecode:: http

      GET /api/stats/all HTTP/1.1


    **Example responses**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": 3,
          "uploads_dir_size": 1000,
          "users": 2,
          "workouts": 3,
        },
        "status": "success"
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403: you do not have permissions
    """

    nb_workouts = Workout.query.filter().count()
    nb_users = User.query.filter().count()
    nb_sports = (
        db.session.query(func.count(Workout.sport_id))
        .group_by(Workout.sport_id)
        .count()
    )
    return {
        'status': 'success',
        'data': {
            'workouts': nb_workouts,
            'sports': nb_sports,
            'users': nb_users,
            'uploads_dir_size': get_upload_dir_size(),
        },
    }
