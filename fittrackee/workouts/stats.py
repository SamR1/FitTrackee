from datetime import datetime, timedelta
from typing import Dict, List, Union

from flask import Blueprint, request
from sqlalchemy import func

from fittrackee import db
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    UserNotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import User

from .models import Sport, Workout
from .utils.uploads import get_upload_dir_size
from .utils.workouts import get_average_speed, get_datetime_from_request_args

stats_blueprint = Blueprint('stats', __name__)


def get_stats_from_row(row: List) -> Dict:
    return {
        'average_speed': round(float(row[1]), 2),
        'nb_workouts': row[2],
        'total_distance': round(float(row[3]), 2),
        'total_duration': int(row[4].total_seconds()),
        'total_ascent': 0.0 if row[5] is None else round(float(row[5]), 2),
        'total_descent': 0.0 if row[6] is None else round(float(row[6]), 2),
    }


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

        time_format = 'yyyy'
        if filter_type == 'by_sport':
            if sport_id:
                sport = Sport.query.filter_by(id=sport_id).first()
                if not sport:
                    return NotFoundErrorResponse('sport does not exist')
        else:
            if not time or time == 'year':
                time_format = 'yyyy'
            elif time == 'month':
                time_format = 'yyyy-mm'
            elif time.startswith('week'):
                # 'week' => week starts on Sunday
                # 'weekm' => week starts on Monday
                #
                # Note: on PostgreSQL, week starts on Monday
                time_format = 'YYYY-WW'
            else:
                return InvalidPayloadErrorResponse(
                    'Invalid time period.', 'fail'
                )

        # On PostgreSQL, week starts on Monday
        # For 'week' timeframe, the workaround is to add 1 day
        delta = timedelta(days=1 if time and time == "week" else 0)

        query = db.session.query(
            Workout.sport_id,
            func.avg(Workout.ave_speed),
            func.count(Workout.id),
            func.sum(Workout.distance),
            func.sum(Workout.moving),
            func.sum(Workout.ascent),
            func.sum(Workout.descent),
            (
                func.to_char(Workout.workout_date + delta, time_format)
                if filter_type == 'by_time'
                else True
            ),
        ).filter(
            Workout.user_id == user.id,
            Workout.workout_date >= date_from if date_from else True,
            (
                Workout.workout_date < date_to + timedelta(seconds=1)
                if date_to
                else True
            ),
            Workout.sport_id == sport_id if sport_id else True,
        )
        if filter_type == 'by_sport':
            results = query.group_by(Workout.sport_id).all()
        else:
            results = query.group_by(
                func.to_char(Workout.workout_date + delta, time_format),
                Workout.sport_id,
            ).all()

        statistics = {}
        if filter_type == "by_sport":
            for row in results:
                statistics[row[0]] = get_stats_from_row(row)
        else:
            for row in results:
                date_key = row[7]
                if time and time.startswith("week"):
                    date_key = (
                        datetime.strptime(date_key + '-1', "%Y-%W-%w") - delta
                    ).strftime('%Y-%m-%d')
                sport_key = row[0]
                if date_key not in statistics:
                    statistics[date_key] = {sport_key: get_stats_from_row(row)}
                elif sport_key not in statistics[date_key]:
                    statistics[date_key][sport_key] = get_stats_from_row(row)
                else:
                    statistics[date_key][sport_key]['nb_workouts'] += row[2]
                    statistics[date_key][sport_key]['average_speed'] = (
                        get_average_speed(
                            statistics[date_key][sport_key]['nb_workouts'],
                            statistics[date_key][sport_key]['average_speed'],
                            row[1],
                        )
                    )
                    statistics[date_key][sport_key]['total_distance'] += round(
                        float(row[3]), 2
                    )
                    statistics[date_key][sport_key]['total_duration'] += int(
                        row[4].total_seconds()
                    )
                    if row[5]:
                        statistics[date_key][sport_key]['total_ascent'] += (
                            round(float(row[5]), 2)
                        )
                    if row[6]:
                        statistics[date_key][sport_key]['total_ascent'] += (
                            round(float(row[6]), 2)
                        )

        return {
            'status': 'success',
            'data': {'statistics': statistics},
        }
    except Exception as e:
        return handle_error_and_return_response(e)


@stats_blueprint.route('/stats/<user_name>/by_time', methods=['GET'])
@require_auth(scopes=['workouts:read'])
def get_workouts_by_time(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get workouts statistics for a user by time.

    **Scope**: ``workouts:read``

    **Example requests**:

    - without parameters:

    .. sourcecode:: http

      GET /api/stats/admin/by_time HTTP/1.1

    - with parameters:

    .. sourcecode:: http

      GET /api/stats/admin/by_time?from=2018-01-01&to=2018-06-30&time=week
        HTTP/1.1

    **Example responses**:

    - success:

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

    - no workouts:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
            "statistics": {}
        },
        "status": "success"
      }

    :param integer user_name: username

    :query string from: start date (format: ``%Y-%m-%d``)
    :query string to: end date (format: ``%Y-%m-%d``)
    :query string time: time frame:

      - ``week``: week starting Sunday
      - ``weekm``: week starting Monday
      - ``month``: month
      - ``year``: year (default)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``user does not exist``

    """
    return get_workouts(user_name, 'by_time')


@stats_blueprint.route('/stats/<user_name>/by_sport', methods=['GET'])
@require_auth(scopes=['workouts:read'])
def get_workouts_by_sport(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get workouts statistics for a user by sport.

    **Scope**: ``workouts:read``

    **Example requests**:

    - without parameters (get stats for all sports with workouts):

    .. sourcecode:: http

      GET /api/stats/admin/by_sport HTTP/1.1

    - with sport id:

    .. sourcecode:: http

      GET /api/stats/admin/by_sport?sport_id=1 HTTP/1.1

    **Example responses**:

    - success:

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

    - no workouts:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
            "statistics": {}
        },
        "status": "success"
      }

    :param integer user_name: username

    :query integer sport_id: sport id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404:
        - ``user does not exist``
        - ``sport does not exist``

    """
    return get_workouts(user_name, 'by_sport')


@stats_blueprint.route('/stats/all', methods=['GET'])
@require_auth(scopes=['workouts:read'], as_admin=True)
def get_application_stats(auth_user: User) -> Dict:
    """
    Get all application statistics.

    **Scope**: ``workouts:read``

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

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
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
