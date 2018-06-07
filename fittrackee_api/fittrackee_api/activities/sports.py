from fittrackee_api import appLog, db
from flask import Blueprint, jsonify, request
from sqlalchemy import exc

from ..users.utils import authenticate, authenticate_as_admin
from .models import Sport

sports_blueprint = Blueprint('sports', __name__)


@sports_blueprint.route('/sports', methods=['GET'])
@authenticate
def get_sports(auth_user_id):
    """Get all sports"""
    sports = Sport.query.order_by(Sport.id).all()
    response_object = {
        'status': 'success',
        'data': {
            'sports': [sport.serialize() for sport in sports]
        }
    }
    return jsonify(response_object), 200


@sports_blueprint.route('/sports/<int:sport_id>', methods=['GET'])
@authenticate
def get_sport(auth_user_id, sport_id):
    """Get a sport"""
    sport = Sport.query.filter_by(id=sport_id).first()
    if sport:
        response_object = {
            'status': 'success',
            'data': {
                'sports': [sport.serialize()]
            }
        }
        code = 200
    else:
        response_object = {
            'status': 'not found',
            'data': {
                'sports': []
            }
        }
        code = 404
    return jsonify(response_object), code


@sports_blueprint.route('/sports', methods=['POST'])
@authenticate_as_admin
def post_sport(auth_user_id):
    """Post a sport"""
    sport_data = request.get_json()
    if not sport_data or sport_data.get('label') is None:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    try:
        new_sport = Sport(label=sport_data.get('label'))
        db.session.add(new_sport)
        db.session.commit()
        response_object = {
            'status': 'created',
            'data': {
                'sports': [new_sport.serialize()]
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


@sports_blueprint.route('/sports/<int:sport_id>', methods=['PATCH'])
@authenticate_as_admin
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


@sports_blueprint.route('/sports/<int:sport_id>', methods=['DELETE'])
@authenticate_as_admin
def delete_sport(auth_user_id, sport_id):
    """Delete a sport"""
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
                    'sports': []
                }
            }
            code = 404
    except exc.IntegrityError as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Associated activities exist.'
        }
        code = 500
    except (exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code
