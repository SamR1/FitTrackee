from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import exc

from fittrackee import db
from fittrackee.responses import (
    DataNotFoundErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.decorators import authenticate, authenticate_as_admin
from fittrackee.users.models import User

from .models import Sport

sports_blueprint = Blueprint('sports', __name__)


@sports_blueprint.route('/sports', methods=['GET'])
@authenticate
def get_sports(auth_user_id: int) -> Dict:
    """
    Get all sports

    **Example request**:

    .. sourcecode:: http

      GET /api/sports HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - for non admin user :

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": [
            {
              "id": 1,
              "is_active": true,
              "label": "Cycling (Sport)"
            },
            {
              "id": 2,
              "is_active": true,
              "label": "Cycling (Transport)"
            },
            {
              "id": 3,
              "is_active": true,
              "label": "Hiking"
            },
            {
              "id": 4,
              "is_active": true,
              "label": "Mountain Biking"
            },
            {
              "id": 5,
              "is_active": true,
              "label": "Running"
            },
            {
              "id": 6,
              "is_active": true,
              "label": "Walking"
            }
          ]
        },
        "status": "success"
      }

    - for admin user :

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": [
            {
              "has_workouts": true,
              "id": 1,
              "is_active": true,
              "label": "Cycling (Sport)"
            },
            {
              "has_workouts": false,
              "id": 2,
              "is_active": true,
              "label": "Cycling (Transport)"
            },
            {
              "has_workouts": false,
              "id": 3,
              "is_active": true,
              "label": "Hiking"
            },
            {
              "has_workouts": false,
              "id": 4,
              "is_active": true,
              "label": "Mountain Biking"
            },
            {
              "has_workouts": false,
              "id": 5,
              "is_active": true,
              "label": "Running"
            },
            {
              "has_workouts": false,
              "id": 6,
              "is_active": true,
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
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again

    """
    user = User.query.filter_by(id=int(auth_user_id)).first()
    sports = Sport.query.order_by(Sport.id).all()
    return {
        'status': 'success',
        'data': {'sports': [sport.serialize(user.admin) for sport in sports]},
    }


@sports_blueprint.route('/sports/<int:sport_id>', methods=['GET'])
@authenticate
def get_sport(auth_user_id: int, sport_id: int) -> Union[Dict, HttpResponse]:
    """
    Get a sport

    **Example request**:

    .. sourcecode:: http

      GET /api/sports/1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - success for non admin user :

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": [
            {
              "id": 1,
              "is_active": true,
              "label": "Cycling (Sport)"
            }
          ]
        },
        "status": "success"
      }

    - success for admin user :

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": [
            {
              "has_workouts": false,
              "id": 1,
              "is_active": true,
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
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 404: sport not found

    """
    user = User.query.filter_by(id=int(auth_user_id)).first()
    sport = Sport.query.filter_by(id=sport_id).first()
    if sport:
        return {
            'status': 'success',
            'data': {'sports': [sport.serialize(user.admin)]},
        }
    return DataNotFoundErrorResponse('sports')


@sports_blueprint.route('/sports/<int:sport_id>', methods=['PATCH'])
@authenticate_as_admin
def update_sport(
    auth_user_id: int, sport_id: int
) -> Union[Dict, HttpResponse]:
    """
    Update a sport
    Authenticated user must be an admin

    **Example request**:

    .. sourcecode:: http

      PATCH /api/sports/1 HTTP/1.1
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
              "has_workouts": false,
              "id": 1,
              "is_active": false,
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

    :<json string is_active: sport active status

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: sport updated
    :statuscode 400: invalid payload
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403: you do not have permissions
    :statuscode 404: sport not found
    :statuscode 500:

    """
    sport_data = request.get_json()
    if not sport_data or sport_data.get('is_active') is None:
        return InvalidPayloadErrorResponse()

    try:
        sport = Sport.query.filter_by(id=sport_id).first()
        if not sport:
            return DataNotFoundErrorResponse('sports')

        sport.is_active = sport_data.get('is_active')
        db.session.commit()
        return {
            'status': 'success',
            'data': {'sports': [sport.serialize(True)]},
        }

    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)
