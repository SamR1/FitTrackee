from datetime import datetime, timedelta
from typing import Dict, List, Union

from flask import Blueprint, current_app, request
from sqlalchemy import func

from fittrackee import db
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    ForbiddenErrorResponse,
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


def get_stats_from_row(row: List, stats_type: str) -> Dict:
    row_stats = {
        'total_workouts': row[2],
        f'{stats_type}_distance': round(float(row[3]), 2),
        f'{stats_type}_duration': int(row[4].total_seconds()),
        f'{stats_type}_ascent': (
            None if row[5] is None else round(float(row[5]), 2)
        ),
        f'{stats_type}_descent': (
            None if row[6] is None else round(float(row[6]), 2)
        ),
    }
    if stats_type == "average":
        row_stats['average_speed'] = round(float(row[1]), 2)
    return row_stats


@stats_blueprint.route('/stats/<user_name>/by_time', methods=['GET'])
@require_auth(scopes=['workouts:read'])
def get_workouts_by_time(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get workouts statistics for a user by time.
    For now only authenticated users can access their statistics.

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

    - success for total:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "statistics": {
            "2017": {
              "3": {
                "total_workouts": 2,
                "total_ascent": 203.0,
                "total_ascent": 156.0,
                "total_distance": 15.282,
                "total_duration": 12341
              }
            },
            "2019": {
              "1": {
                "total_workouts": 3,
                "total_ascent": 150.0,
                "total_ascent": 178.0,
                "total_distance": 47,
                "total_duration": 9960
              },
              "2": {
                "total_workouts": 1,
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

    - success for average:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "statistics": {
            "2017": {
              "3": {
                "average_ascent": 101.5,
                "average_ascent": 78.0,
                "average_distance": 15.282,
                "average_duration": 7641,
                "average_speed": 4.48,
                "total_workouts": 2
              }
            },
            "2019": {
              "1": {
                "average_ascent": 50.0,
                "average_descent": 59.33,
                "average_distance": 15.67,
                "average_duration": 3320,
                "average_speed": 16.99,
                "total_workouts": 3
              },
              "2": {
                "average_ascent": 46.0,
                "average_descent": 78.0,
                "average_distance": 5.613,
                "average_duration": 1267,
                "average_speed": 15.95,
                "total_workouts": 1
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
    :query string type: stats type:

      - ``total``: calculating totals
      - ``average``: calculating averages

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid stats type``
        - ``invalid time period``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``user does not exist``

    """
    try:
        user = User.query.filter_by(username=user_name).first()
        if not user:
            return UserNotFoundErrorResponse()
        if user.id != auth_user.id:
            return ForbiddenErrorResponse()

        params = request.args.copy()
        date_from, date_to = get_datetime_from_request_args(params, user)
        time = params.get('time')
        stats_type = params.get('type', 'total')
        if stats_type not in ['total', 'average']:
            return InvalidPayloadErrorResponse('invalid stats type', 'fail')

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
            return InvalidPayloadErrorResponse('invalid time period', 'fail')

        # On PostgreSQL, week starts on Monday
        # For 'week' timeframe, the workaround is to add 1 day
        delta = timedelta(days=1 if time and time == "week" else 0)

        calculation_method = func.avg if stats_type == "average" else func.sum
        results = (
            db.session.query(
                Workout.sport_id,
                func.avg(Workout.ave_speed)
                if stats_type == "average"
                else True,
                func.count(Workout.id),
                calculation_method(Workout.distance),
                calculation_method(Workout.moving),
                calculation_method(Workout.ascent),
                calculation_method(Workout.descent),
                func.to_char(Workout.workout_date + delta, time_format),
            )
            .filter(
                Workout.user_id == user.id,
                Workout.workout_date >= date_from if date_from else True,
                (
                    Workout.workout_date < date_to + timedelta(seconds=1)
                    if date_to
                    else True
                ),
            )
            .group_by(
                func.to_char(Workout.workout_date + delta, time_format),
                Workout.sport_id,
            )
            .all()
        )

        statistics = {}
        for row in results:
            date_key = row[7]
            if time and time.startswith("week"):
                date_key = (
                    datetime.strptime(date_key + '-1', "%Y-%W-%w") - delta
                ).strftime('%Y-%m-%d')
            sport_key = row[0]
            if date_key not in statistics:
                statistics[date_key] = {
                    sport_key: get_stats_from_row(row, stats_type)
                }
            elif sport_key not in statistics[date_key]:
                statistics[date_key][sport_key] = get_stats_from_row(
                    row, stats_type
                )
            else:
                statistics[date_key][sport_key]['total_workouts'] += row[2]
                if stats_type == "average":
                    statistics[date_key][sport_key]['average_speed'] = (
                        get_average_speed(
                            statistics[date_key][sport_key]['total_workouts'],
                            statistics[date_key][sport_key]['average_speed'],
                            row[1],
                        )
                    )
                statistics[date_key][sport_key][f'{stats_type}_distance'] += (
                    round(float(row[3]), 2)
                )
                statistics[date_key][sport_key][f'{stats_type}_duration'] += (
                    int(row[4].total_seconds())
                )
                if row[5]:
                    statistics[date_key][sport_key][
                        f'{stats_type}_ascent'
                    ] += round(float(row[5]), 2)
                if row[6]:
                    statistics[date_key][sport_key][
                        f'{stats_type}_ascent'
                    ] += round(float(row[6]), 2)

        return {
            'status': 'success',
            'data': {'statistics': statistics},
        }
    except Exception as e:
        return handle_error_and_return_response(e)


@stats_blueprint.route('/stats/<user_name>/by_sport', methods=['GET'])
@require_auth(scopes=['workouts:read'])
def get_workouts_by_sport(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get workouts statistics for a user by sport.
    For now only authenticated users can access their statistics.

    **Scope**: ``workouts:read``

    **Example requests**:

    - without parameters (get stats for all sports with workouts):

    .. sourcecode:: http

      GET /api/stats/admin/by_sport HTTP/1.1

    - with sport id:

    .. sourcecode:: http

      GET /api/stats/admin/by_sport?sport_id=1 HTTP/1.1

    **Example responses**:

    - success for all sports:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "statistics": {
            "1": {
              "average_ascent": 50.0,
              "average_descent": 59.33,
              "average_distance": 15.67,
              "average_duration": 3320,
              "average_speed": 16.99,
              "total_workouts": 3,
              "total_ascent": 150.0,
              "total_ascent": 178.0,
              "total_distance": 47,
              "total_duration": 9960
            },
            "2": {
              "average_ascent": 46.0,
              "average_descent": 78.0,
              "average_distance": 5.613,
              "average_duration": 1267,
              "average_speed": 15.95,
              "total_workouts": 1,
              "total_ascent": 46.0,
              "total_ascent": 78.0,
              "total_distance": 5.613,
              "total_duration": 1267
            },
            "3": {
              "average_ascent": 101.5,
              "average_ascent": 78.0,
              "average_distance": 15.282,
              "average_duration": 7641,
              "average_speed": 4.48,
              "total_workouts": 2,
              "total_ascent": 203.0,
              "total_ascent": 156.0,
              "total_distance": 15.282,
              "total_duration": 12341
            }
          }
        },
        "status": "success"
      }

    - success for a given sport:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "statistics": {
            "2": {
              "average_ascent": 46.0,
              "average_descent": 78.0,
              "average_distance": 5.613,
              "average_duration": 1267,
              "average_speed": 15.95,
              "total_workouts": 1,
              "total_ascent": 46.0,
              "total_ascent": 78.0,
              "total_distance": 5.613,
              "total_duration": 1267
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

    :query integer sport_id: sport id (not mandatory).
           If not provided, statistics for all sports are returned.

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid stats type``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404:
        - ``user does not exist``
        - ``sport does not exist``

    """
    try:
        user = User.query.filter_by(username=user_name).first()
        if not user:
            return UserNotFoundErrorResponse()
        if user.id != auth_user.id:
            return ForbiddenErrorResponse()

        params = request.args.copy()
        sport_id = params.get('sport_id')
        if sport_id:
            sport = Sport.query.filter_by(id=sport_id).first()
            if not sport:
                return NotFoundErrorResponse('sport does not exist')

        workouts_query = Workout.query.filter(
            Workout.user_id == user.id,
            Workout.sport_id == sport_id if sport_id else True,
        )
        total_workouts = workouts_query.count()

        workouts_subquery = workouts_query.order_by(
            Workout.workout_date.desc()
        )
        if current_app.config['stats_workouts_limit']:
            workouts_subquery = workouts_subquery.limit(
                current_app.config['stats_workouts_limit']
            )
        workouts_subquery = workouts_subquery.subquery()
        results = (
            db.session.query(
                workouts_subquery.c.sport_id,
                func.avg(workouts_subquery.c.ave_speed),
                func.avg(workouts_subquery.c.ascent),
                func.avg(workouts_subquery.c.descent),
                func.avg(workouts_subquery.c.distance),
                func.avg(workouts_subquery.c.moving),
                func.sum(workouts_subquery.c.ascent),
                func.sum(workouts_subquery.c.descent),
                func.sum(workouts_subquery.c.distance),
                func.sum(workouts_subquery.c.moving),
                func.count(workouts_subquery.c.id),
            )
            .group_by(workouts_subquery.c.sport_id)
            .all()
        )

        statistics = {}
        for row in results:
            statistics[row[0]] = {
                'average_speed': round(float(row[1]), 2),
                'average_ascent': (
                    None if row[2] is None else round(float(row[2]), 2)
                ),
                'average_descent': (
                    None if row[3] is None else round(float(row[3]), 2)
                ),
                'average_distance': round(float(row[4]), 2),
                'average_duration': str(row[5]).split('.')[0],
                'total_ascent': (
                    None if row[6] is None else round(float(row[6]), 2)
                ),
                'total_descent': (
                    None if row[7] is None else round(float(row[7]), 2)
                ),
                'total_distance': round(float(row[8]), 2),
                'total_duration': str(row[9]).split('.')[0],
                'total_workouts': row[10],
            }

        return {
            'status': 'success',
            'data': {
                'statistics': statistics,
                'total_workouts': total_workouts,
            },
        }
    except Exception as e:
        return handle_error_and_return_response(e)


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

    total_workouts = Workout.query.filter().count()
    nb_users = User.query.filter().count()
    nb_sports = (
        db.session.query(func.count(Workout.sport_id))
        .group_by(Workout.sport_id)
        .count()
    )
    return {
        'status': 'success',
        'data': {
            'workouts': total_workouts,
            'sports': nb_sports,
            'users': nb_users,
            'uploads_dir_size': get_upload_dir_size(),
        },
    }
