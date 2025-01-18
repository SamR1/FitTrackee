from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import exc

from fittrackee import db
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    DataNotFoundErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import User, UserSportPreference
from fittrackee.users.roles import UserRole

from .models import Sport

sports_blueprint = Blueprint('sports', __name__)


@sports_blueprint.route('/sports', methods=['GET'])
@require_auth(
    scopes=['workouts:read'],
    optional_auth_user=True,
    allow_suspended_user=True,
)
def get_sports(auth_user: User) -> Dict:
    """
    Get all sports.

    Suspended user can access this endpoint.

    **Scope**: ``workouts:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/sports HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - for non admin user:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": [
            {
              "color": null,
              "id": 1,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Cycling (Sport)",
              "stopped_speed_threshold": 1
            },
            {
              "color": null,
              "id": 2,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Cycling (Transport)",
              "stopped_speed_threshold": 1
            },
            {
              "color": null,
              "id": 3,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Hiking",
              "stopped_speed_threshold": 0.1
            },
            {
              "color": null,
              "id": 4,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Mountain Biking",
              "stopped_speed_threshold": 1
            },
            {
              "color": null,
              "id": 5,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Running",
              "stopped_speed_threshold": 0.1
            },
            {
              "color": null,
              "id": 6,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Walking",
              "stopped_speed_threshold": 0.1
            }
          ]
        },
        "status": "success"
      }

    - for admin user and check_workouts=true:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": [
            {
              "color": null,
              "has_workouts": true,
              "id": 1,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Cycling (Sport)",
              "stopped_speed_threshold": 1
            },
            {
              "color": null,
              "has_workouts": false,
              "id": 2,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Cycling (Transport)",
              "stopped_speed_threshold": 1
            },
            {
              "color": null,
              "has_workouts": false,
              "id": 3,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Hiking",
              "stopped_speed_threshold": 0.1
            },
            {
              "color": null,
              "has_workouts": false,
              "id": 4,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Mountain Biking",
              "stopped_speed_threshold": 1
            },
            {
              "color": null,
              "has_workouts": false,
              "id": 5,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Running",
              "stopped_speed_threshold": 0.1
            },
            {
              "color": null,
              "has_workouts": false,
              "id": 6,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Walking",
              "stopped_speed_threshold": 0.1
            }
          ]
        },
        "status": "success"
      }

    :query boolean check_workouts: check if sport has workouts

    :reqheader Authorization: OAuth 2.0 Bearer Token if user is authenticated

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``

    """
    params = request.args.copy()
    check_workouts = params.get('check_workouts', 'false').lower() == 'true'

    sport_preferences = (
        {
            p.sport_id: p
            for p in UserSportPreference.query.filter_by(
                user_id=auth_user.id
            ).all()
        }
        if auth_user
        else {}
    )
    sports = Sport.query.order_by(Sport.id).all()
    sports_data = []
    for sport in sports:
        sports_data.append(
            sport.serialize(
                check_workouts=(
                    auth_user and auth_user.has_admin_rights and check_workouts
                ),
                sport_preferences=(
                    sport_preferences[sport.id].serialize()
                    if sport.id in sport_preferences
                    else None
                ),
            )
        )
    return {
        'status': 'success',
        'data': {'sports': sports_data},
    }


@sports_blueprint.route('/sports/<int:sport_id>', methods=['GET'])
@require_auth(scopes=['workouts:read'])
def get_sport(auth_user: User, sport_id: int) -> Union[Dict, HttpResponse]:
    """
    Get a sport

    **Scope**: ``workouts:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/sports/1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - success for non admin user:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": [
            {
              "color": null,
              "id": 1,
              "is_active": true,
              "is_active_for_user": true,
              "label": "Cycling (Sport)",
              "stopped_speed_threshold": 1
            }
          ]
        },
        "status": "success"
      }

    - sport not found:

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

      {
        "data": {
          "sports": []
        },
        "status": "not found"
      }

    :param integer sport_id: sport id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``sport not found``

    """
    sport = Sport.query.filter_by(id=sport_id).first()
    if sport:
        sport_preferences = UserSportPreference.query.filter_by(
            user_id=auth_user.id, sport_id=sport.id
        ).first()
        return {
            'status': 'success',
            'data': {
                'sports': [
                    sport.serialize(
                        sport_preferences=(
                            sport_preferences.serialize()
                            if sport_preferences
                            else None
                        ),
                    )
                ]
            },
        }
    return DataNotFoundErrorResponse('sports')


@sports_blueprint.route('/sports/<int:sport_id>', methods=['PATCH'])
@require_auth(scopes=['workouts:write'], role=UserRole.ADMIN)
def update_sport(auth_user: User, sport_id: int) -> Union[Dict, HttpResponse]:
    """
    Update a sport.

    Authenticated user must be an admin.

    **Scope**: ``workouts:write``

    **Minimum role**: Administrator

    **Example request**:

    .. sourcecode:: http

      PATCH /api/sports/1 HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - success:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "sports": [
            {
              "color": null,
              "has_workouts": false,
              "id": 1,
              "is_active": false,
              "is_active_for_user": false,
              "label": "Cycling (Sport)",
              "stopped_speed_threshold": 1
            }
          ]
        },
        "status": "success"
      }

    - sport not found:

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

      {
        "data": {
          "sports": []
        },
        "status": "not found"
      }

    :param integer sport_id: sport id

    :<json string is_active: sport active status

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: sport updated
    :statuscode 400:
        - ``invalid payload``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``sport not found``
    :statuscode 500: ``error, please try again or contact the administrator``

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
        sport_preferences = UserSportPreference.query.filter_by(
            user_id=auth_user.id, sport_id=sport.id
        ).first()
        return {
            'status': 'success',
            'data': {
                'sports': [
                    sport.serialize(
                        sport_preferences=(
                            sport_preferences.serialize()
                            if sport_preferences
                            else None
                        ),
                    )
                ]
            },
        }

    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)
