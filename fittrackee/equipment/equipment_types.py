from typing import Dict, Tuple, Union

from flask import Blueprint, request
from sqlalchemy import exc

from fittrackee import db
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    DataNotFoundErrorResponse,
    ForbiddenErrorResponse,
    GenericErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import User

from ..equipment.models import Equipment, EquipmentType
from ..users.models import UserSportPreference

equipment_types_blueprint = Blueprint('equipment_types', __name__)

@equipment_types_blueprint.route('/equipment_types', methods=['GET'])
@require_auth(scopes=['profile:read'])
def get_equipment_types(auth_user: User) -> Dict:
    """
    Get all sports

    **Scope**: ``profile:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/equipment_types HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - for non admin user :

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "equipment_types": [
            {
              "id": 1,
              "is_active": true,
              "label": "Shoe"
            },
            {
              "id": 2,
              "is_active": true,
              "label": "Bike"
            },
            {
              "id": 3,
              "is_active": true,
              "label": "Treadmill"
            },
            {
              "id": 4,
              "is_active": true,
              "label": "Bike Trainer"
            },
            {
              "id": 5,
              "is_active": true,
              "label": "Kayak/Boat"
            },
            {
              "id": 6,
              "is_active": true,
              "label": "Skis"
            },
            {
              "id": 7,
              "is_active": true,
              "label": "Snowshoes"
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
          "equipment_types": [
            {
              "has_equipment": true,
              "id": 1,
              "is_active": true,
              "label": "Shoe"
            },
            {
              "has_equipment": true,
              "id": 2,
              "is_active": true,
              "label": "Bike"
            },
            {
              "has_equipment": false,
              "id": 3,
              "is_active": true,
              "label": "Treadmill"
            },
            {
              "has_equipment": false,
              "id": 4,
              "is_active": true,
              "label": "Bike Trainer"
            },
            {
              "has_equipment": false,
              "id": 5,
              "is_active": true,
              "label": "Kayak/Boat"
            },
            {
              "has_equipment": false,
              "id": 6,
              "is_active": true,
              "label": "Skis"
            },
            {
              "has_equipment": false,
              "id": 7,
              "is_active": true,
              "label": "Snowshoes"
            }
          ]
        },
        "status": "success"
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again

    """
    equipment_types = EquipmentType.query.order_by(EquipmentType.id).all()
    equipment_types_data = []
    for equipment_type in equipment_types:
        equipment_types_data.append(
            equipment_type.serialize(
                is_admin=auth_user.admin,
            )
        )
    return {
        'status': 'success',
        'data': {'equipment_types': equipment_types_data},
    }

@equipment_types_blueprint.route('/equipment_types/<int:equipment_type_id>', methods=['GET'])
@require_auth(scopes=['profile:read'])
def get_equipment_type(
  auth_user: User, 
  equipment_type_id: int
) -> Union[Dict, HttpResponse]:
    """
    Get a sport

    **Scope**: ``profile:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/equipment_types/1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - success for non admin user :

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "equipment_types": [
            {
              "id": 2,
              "is_active": true,
              "label": "Bike"
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
          "equipment_types": [
            {
              "has_equipment": true,
              "id": 2,
              "is_active": true,
              "label": "Bike"
            }
          ]
        },
        "status": "success"
      }

    - equipment type not found

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

      {
        "status": "not found",
        "data": {
          "equipment_types": []
        }
      }

    :param integer equipment_type_id: equipment type id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 404: equipment_type not found

    """
    equipment_type = EquipmentType.query.filter_by(id=equipment_type_id).first()
    if equipment_type:
        return {
            'status': 'success',
            'data': {
                'equipment_types': [
                    equipment_type.serialize(
                        is_admin=auth_user.admin,
                    )
                ]
            },
        }
    return DataNotFoundErrorResponse('equipment_types')