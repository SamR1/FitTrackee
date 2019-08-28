from fittrackee_api import appLog, db
from flask import Blueprint, jsonify, request
from sqlalchemy import exc

from ..users.utils import authenticate, authenticate_as_admin
from .models import Sport

sports_blueprint = Blueprint('sports', __name__)


@sports_blueprint.route('/sports', methods=['GET'])
@authenticate
def get_sports(auth_user_id):
    """
    Get all sports

    **Example request**:

    .. sourcecode:: http

      GET /api/sports HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": [
            {
              "_can_be_deleted": false,
              "id": 1,
              "img": "/img/sports/cycling-sport.png",
              "label": "Cycling (Sport)"
            },
            {
              "_can_be_deleted": false,
              "id": 2,
              "img": "/img/sports/cycling-transport.png",
              "label": "Cycling (Transport)"
            },
            {
              "_can_be_deleted": false,
              "id": 3,
              "img": "/img/sports/hiking.png",
              "label": "Hiking"
            },
            {
              "_can_be_deleted": false,
              "id": 4,
              "img": "/img/sports/mountain-biking.png",
              "label": "Mountain Biking"
            },
            {
              "_can_be_deleted": false,
              "id": 5,
              "img": "/img/sports/running.png",
              "label": "Running"
            },
            {
              "_can_be_deleted": false,
              "id": 6,
              "img": "/img/sports/walking.png",
              "label": "Walking"
            }
          ]
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

    """

    sports = Sport.query.order_by(Sport.id).all()
    response_object = {
        'status': 'success',
        'data': {'sports': [sport.serialize() for sport in sports]},
    }
    return jsonify(response_object), 200


@sports_blueprint.route('/sports/<int:sport_id>', methods=['GET'])
@authenticate
def get_sport(auth_user_id, sport_id):
    """Get a sport

    **Example request**:

    .. sourcecode:: http

      GET /api/sports/1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - success

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": [
            {
              "_can_be_deleted": false,
              "id": 1,
              "img": "/img/sports/cycling-sport.png",
              "label": "Cycling (Sport)"
            }
          ]
        },
        "status": "success"
      }

    - sport not found

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

      {
        "data": {
          "sports": []
        },
        "status": "not found"
      }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
    :param integer sport_id: sport id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404: sport not found

    """

    sport = Sport.query.filter_by(id=sport_id).first()
    if sport:
        response_object = {
            'status': 'success',
            'data': {'sports': [sport.serialize()]},
        }
        code = 200
    else:
        response_object = {'status': 'not found', 'data': {'sports': []}}
        code = 404
    return jsonify(response_object), code


# no administration - no documentation for now


@sports_blueprint.route('/sports', methods=['POST'])
@authenticate_as_admin
def post_sport(auth_user_id):
    """Post a sport"""
    sport_data = request.get_json()
    if not sport_data or sport_data.get('label') is None:
        response_object = {'status': 'error', 'message': 'Invalid payload.'}
        return jsonify(response_object), 400

    try:
        new_sport = Sport(label=sport_data.get('label'))
        db.session.add(new_sport)
        db.session.commit()
        response_object = {
            'status': 'created',
            'data': {'sports': [new_sport.serialize()]},
        }
        code = 201
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.',
        }
        code = 500
    return jsonify(response_object), code


@sports_blueprint.route('/sports/<int:sport_id>', methods=['PATCH'])
@authenticate_as_admin
def update_sport(auth_user_id, sport_id):
    """Update a sport"""
    sport_data = request.get_json()
    if not sport_data or sport_data.get('label') is None:
        response_object = {'status': 'error', 'message': 'Invalid payload.'}
        return jsonify(response_object), 400

    sports_list = []
    try:
        sport = Sport.query.filter_by(id=sport_id).first()
        if sport:
            sport.label = sport_data.get('label')
            db.session.commit()
            sports_list.append({'id': sport.id, 'label': sport.label})
            response_object = {
                'status': 'success',
                'data': {'sports': sports_list},
            }
            code = 200
        else:
            response_object = {
                'status': 'not found',
                'data': {'sports': sports_list},
            }
            code = 404
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.',
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
            response_object = {'status': 'no content'}
            code = 204
        else:
            response_object = {'status': 'not found', 'data': {'sports': []}}
            code = 404
    except exc.IntegrityError as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Associated activities exist.',
        }
        code = 500
    except (exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.',
        }
        code = 500
    return jsonify(response_object), code
