from flask import Blueprint, jsonify, request
from mpwo_api import appLog, db
from sqlalchemy import exc

from ..users.utils import authenticate
from .models import Activity, Sport

activities_blueprint = Blueprint('activities', __name__)


@activities_blueprint.route('/sports', methods=['GET'])
@authenticate
def get_sports(auth_user_id):
    """Get all sports"""
    sports = Sport.query.order_by(Sport.id).all()
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


@activities_blueprint.route('/sports/<int:sport_id>', methods=['GET'])
@authenticate
def get_sport(auth_user_id, sport_id):
    """Get a sport"""
    sport = Sport.query.filter_by(id=sport_id).first()
    sports_list = []
    if sport:
        sports_list.append({
            'id': sport.id,
            'label': sport.label
        })
        response_object = {
            'status': 'success',
            'data': {
                'sports': sports_list
            }
        }
        code = 200
    else:
        response_object = {
            'status': 'not found',
            'data': {
                'sports': sports_list
            }
        }
        code = 404
    return jsonify(response_object), code


@activities_blueprint.route('/sports', methods=['POST'])
@authenticate
def post_sport(auth_user_id):
    """Post a sport"""
    sport_data = request.get_json()
    if not sport_data or sport_data.get('label') is None:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    sports_list = []
    try:
        new_sport = Sport(label=sport_data.get('label'))
        db.session.add(new_sport)
        db.session.commit()
        sports_list.append({
            'id': new_sport.id,
            'label': new_sport.label
        })
        response_object = {
            'status': 'created',
            'data': {
                'sports': sports_list
            }
        }
        code = 201
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code


@activities_blueprint.route('/sports/<int:sport_id>', methods=['PATCH'])
@authenticate
def update_sport(auth_user_id, sport_id):
    """Update a sport"""
    sport_data = request.get_json()
    if not sport_data or sport_data.get('label') is None:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    sports_list = []
    try:
        sport = Sport.query.filter_by(id=sport_id).first()
        if sport:
            sport.label = sport_data.get('label')
            db.session.commit()
            sports_list.append({
                'id': sport.id,
                'label': sport.label
            })
            response_object = {
                'status': 'success',
                'data': {
                    'sports': sports_list
                }
            }
            code = 200
        else:
            response_object = {
                'status': 'not found',
                'data': {
                    'sports': sports_list
                }
            }
            code = 404
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code


@activities_blueprint.route('/sports/<int:sport_id>', methods=['DELETE'])
@authenticate
def delete_sport(auth_user_id, sport_id):
    """Delete a sport"""
    sports_list = []
    try:
        sport = Sport.query.filter_by(id=sport_id).first()
        if sport:
            db.session.delete(sport)
            db.session.commit()
            response_object = {
                'status': 'no content'
            }
            code = 204
        else:
            response_object = {
                'status': 'not found',
                'data': {
                    'sports': sports_list
                }
            }
            code = 404
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code


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
