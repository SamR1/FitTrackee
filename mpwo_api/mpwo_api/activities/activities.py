from flask import Blueprint, jsonify

from ..users.utils import authenticate
from .models import Activity

activities_blueprint = Blueprint('activities', __name__)


@activities_blueprint.route('/activities', methods=['GET'])
@authenticate
def get_activities(user_id):
    """Get all activities"""
    activities = Activity.query.all()
    activities_list = []
    for activity in activities:
        activity_object = {
            'id': activity.id,
            'user_id': activity.user_id,
            'sport_id': activity.sport_id,
            'creation_date': activity.creation_date
        }
        activities_list.append(activity_object)
    response_object = {
        'status': 'success',
        'data': {
            'activities': activities_list
        }
    }
    return jsonify(response_object), 200
