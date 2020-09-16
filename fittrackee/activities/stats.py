from datetime import datetime, timedelta

from fittrackee import appLog, db
from flask import Blueprint, jsonify, request
from sqlalchemy import func

from ..users.models import User
from ..users.utils import authenticate, authenticate_as_admin
from .models import Activity, Sport
from .utils import get_datetime_with_tz, get_upload_dir_size
from .utils_format import convert_timedelta_to_integer

stats_blueprint = Blueprint('stats', __name__)


def get_activities(user_name, filter_type):
    try:
        user = User.query.filter_by(username=user_name).first()
        if not user:
            response_object = {
                'status': 'not found',
                'message': 'User does not exist.',
            }
            return jsonify(response_object), 404

        params = request.args.copy()
        date_from = params.get('from')
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            _, date_from = get_datetime_with_tz(user.timezone, date_from)
        date_to = params.get('to')
        if date_to:
            date_to = datetime.strptime(
                f'{date_to} 23:59:59', '%Y-%m-%d %H:%M:%S'
            )
            _, date_to = get_datetime_with_tz(user.timezone, date_to)
        sport_id = params.get('sport_id')
        time = params.get('time')

        if filter_type == 'by_sport':
            sport_id = params.get('sport_id')
            if sport_id:
                sport = Sport.query.filter_by(id=sport_id).first()
                if not sport:
                    response_object = {
                        'status': 'not found',
                        'message': 'Sport does not exist.',
                    }
                    return jsonify(response_object), 404

        activities = (
            Activity.query.filter(
                Activity.user_id == user.id,
                Activity.activity_date >= date_from if date_from else True,
                Activity.activity_date < date_to + timedelta(seconds=1)
                if date_to
                else True,
                Activity.sport_id == sport_id if sport_id else True,
            )
            .order_by(Activity.activity_date.asc())
            .all()
        )

        activities_list = {}
        for activity in activities:
            if filter_type == 'by_sport':
                sport_id = activity.sport_id
                if sport_id not in activities_list:
                    activities_list[sport_id] = {
                        'nb_activities': 0,
                        'total_distance': 0.0,
                        'total_duration': 0,
                    }
                activities_list[sport_id]['nb_activities'] += 1
                activities_list[sport_id]['total_distance'] += float(
                    activity.distance
                )
                activities_list[sport_id][
                    'total_duration'
                ] += convert_timedelta_to_integer(activity.moving)

            else:
                if time == 'week':
                    activity_date = activity.activity_date - timedelta(
                        days=(
                            activity.activity_date.isoweekday()
                            if activity.activity_date.isoweekday() < 7
                            else 0
                        )
                    )
                    time_period = datetime.strftime(activity_date, "%Y-%m-%d")
                elif time == 'weekm':  # week start Monday
                    activity_date = activity.activity_date - timedelta(
                        days=activity.activity_date.weekday()
                    )
                    time_period = datetime.strftime(activity_date, "%Y-%m-%d")
                elif time == 'month':
                    time_period = datetime.strftime(
                        activity.activity_date, "%Y-%m"
                    )
                elif time == 'year' or not time:
                    time_period = datetime.strftime(
                        activity.activity_date, "%Y"
                    )
                else:
                    response_object = {
                        'status': 'fail',
                        'message': 'Invalid time period.',
                    }
                    return jsonify(response_object), 400
                sport_id = activity.sport_id
                if time_period not in activities_list:
                    activities_list[time_period] = {}
                if sport_id not in activities_list[time_period]:
                    activities_list[time_period][sport_id] = {
                        'nb_activities': 0,
                        'total_distance': 0.0,
                        'total_duration': 0,
                    }
                activities_list[time_period][sport_id]['nb_activities'] += 1
                activities_list[time_period][sport_id][
                    'total_distance'
                ] += float(activity.distance)
                activities_list[time_period][sport_id][
                    'total_duration'
                ] += convert_timedelta_to_integer(activity.moving)

        response_object = {
            'status': 'success',
            'data': {'statistics': activities_list},
        }
        code = 200
    except Exception as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.',
        }
        code = 500
    return jsonify(response_object), code


@stats_blueprint.route('/stats/<user_name>/by_time', methods=['GET'])
@authenticate
def get_activities_by_time(auth_user_id, user_name):
    """
    Get activities statistics for a user by time

    **Example requests**:

    - without parameters

    .. sourcecode:: http

      GET /api/stats/admin/by_time HTTP/1.1

    - with parameters

    .. sourcecode:: http

      GET /api/stats/admin/by_time?from=2018-01-01&to=2018-06-30&time=week HTTP/1.1

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
                "nb_activities": 2,
                "total_distance": 15.282,
                "total_duration": 12341
              }
            },
            "2019": {
              "1": {
                "nb_activities": 3,
                "total_distance": 47,
                "total_duration": 9960
              },
              "2": {
                "nb_activities": 1,
                "total_distance": 5.613,
                "total_duration": 1267
              }
            }
          }
        },
        "status": "success"
      }

    - no activities

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
            "statistics": {}
        },
        "status": "success"
      }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
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
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404:
        - User does not exist.

    """
    return get_activities(user_name, 'by_time')


@stats_blueprint.route('/stats/<user_name>/by_sport', methods=['GET'])
@authenticate
def get_activities_by_sport(auth_user_id, user_name):
    """
    Get activities statistics for a user by sport

    **Example requests**:

    - without parameters (get stats for all sports with activities)

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
              "nb_activities": 3,
              "total_distance": 47,
              "total_duration": 9960
            },
            "2": {
              "nb_activities": 1,
              "total_distance": 5.613,
              "total_duration": 1267
            },
            "3": {
              "nb_activities": 2,
              "total_distance": 15.282,
              "total_duration": 12341
            }
          }
        },
        "status": "success"
      }

    - no activities

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
            "statistics": {}
        },
        "status": "success"
      }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
    :param integer user_name: user name

    :query integer sport_id: sport id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404:
        - User does not exist.
        - Sport does not exist.

    """
    return get_activities(user_name, 'by_sport')


@stats_blueprint.route('/stats/all', methods=['GET'])
@authenticate_as_admin
def get_application_stats(auth_user_id):
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
          "activities": 3,
          "sports": 3,
          "users": 2,
          "uploads_dir_size": 1000
        },
        "status": "success"
      }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 403: You do not have permissions.
    """

    nb_activities = Activity.query.filter().count()
    nb_users = User.query.filter().count()
    nb_sports = (
        db.session.query(func.count(Activity.sport_id))
        .group_by(Activity.sport_id)
        .count()
    )
    response_object = {
        'status': 'success',
        'data': {
            'activities': nb_activities,
            'sports': nb_sports,
            'users': nb_users,
            'uploads_dir_size': get_upload_dir_size(),
        },
    }
    return jsonify(response_object), 200
