from flask import Blueprint, jsonify

from ..users.utils import authenticate
from .models import Activity, Sport

activities_blueprint = Blueprint('activities', __name__)


@activities_blueprint.route('/sports', methods=['GET'])
@authenticate
def get_sports(auth_user_id):
    """Get all sports"""
    sports = Sport.query.all()
    sports_list = []
    for sport in sports:
        sport_object = {
            'id': sport.id,
            'label': sport.label
        }
        sports_list.append(sport_object)
    response_object = {
        'status': 'success',
        'data': {
            'sports': sports_list
        }
    }
    return jsonify(response_object), 200


@activities_blueprint.route('/activities', methods=['GET'])
@authenticate
def get_activities(auth_user_id):
    """Get all activities"""
    activities = Activity.query.all()
    activities_list = []
    for activity in activities:
        activity_object = {
            'id': activity.id,
            'user_id': activity.user_id,
            'sport_id': activity.sport_id,
            'creation_date': activity.creation_date,
            'activity_date': activity.activity_date,
            'duration': activity.duration.seconds
        }
        activities_list.append(activity_object)
    response_object = {
        'status': 'success',
        'data': {
            'activities': activities_list
        }
    }
    return jsonify(response_object), 200
