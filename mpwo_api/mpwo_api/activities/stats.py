from datetime import datetime

from flask import Blueprint, jsonify, request
from mpwo_api import appLog

from ..users.models import User
from ..users.utils import authenticate
from .models import Activity, convert_timedelta_to_integer

stats_blueprint = Blueprint('stats', __name__)


@stats_blueprint.route('/stats/<int:user_id>/by_week', methods=['GET'])
@authenticate
def get_activities(auth_user_id, user_id):
    """Get activities statistics for a user"""
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            response_object = {
                'status': 'fail',
                'message': 'User does not exist.'
            }
            return jsonify(response_object), 404

        params = request.args.copy()
        date_from = params.get('from')
        date_to = params.get('to')
        activities_list = {}

        activities = Activity.query.filter(
            Activity.user_id == user_id,
            Activity.activity_date >= datetime.strptime(date_from, '%Y-%m-%d')
            if date_from else True,
            Activity.activity_date <= datetime.strptime(date_to, '%Y-%m-%d')
            if date_to else True,
        ).order_by(
            Activity.activity_date.asc()
        ).all()

        for activity in activities:
            week = f'W{datetime.strftime(activity.activity_date, "%U")}'  # noqa
            sport = activity.sports.label
            if week not in activities_list:
                activities_list[week] = {}
            if sport not in activities_list[week]:
                activities_list[week][sport] = {
                    'nb_activities': 0,
                    'total_distance': 0.,
                    'total_duration': 0,
                }
            activities_list[week][sport]['nb_activities'] += 1
            activities_list[week][sport]['total_distance'] += \
                float(activity.distance)
            activities_list[week][sport]['total_duration'] += \
                convert_timedelta_to_integer(activity.duration)

        response_object = {
            'status': 'success',
            'data': {
                'statistics': activities_list
            }
        }
        code = 200
    except Exception as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code
