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
from fittrackee.users.models import User

from ..equipments.models import EquipmentType

equipment_types_blueprint = Blueprint('equipment_types', __name__)


@equipment_types_blueprint.route('/equipment-types', methods=['GET'])
@require_auth(scopes=['equipments:read'])
def get_equipment_types(auth_user: User) -> Dict:
    """
    Get all types of equipment

    **Scope**: ``equipments:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/equipment-types HTTP/1.1
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
              "label": "Bike Trainer"
            },
            {
              "id": 4,
              "is_active": true,
              "label": "Kayak_Boat"
            },
            {
              "id": 5,
              "is_active": true,
              "label": "Skis"
            },
            {
              "id": 5,
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
              "has_equipments": true,
              "id": 1,
              "is_active": true,
              "label": "Shoe"
            },
            {
              "has_equipments": true,
              "id": 2,
              "is_active": true,
              "label": "Bike"
            },
            {
              "has_equipments": false,
              "id": 3,
              "is_active": true,
              "label": "Bike Trainer"
            },
            {
              "has_equipments": false,
              "id": 4,
              "is_active": true,
              "label": "Kayak_Boat"
            },
            {
              "has_equipments": false,
              "id": 5,
              "is_active": true,
              "label": "Skis"
            },
            {
              "has_equipments": false,
              "id": 6,
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
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``

    """
    equipment_types = (
        EquipmentType.query.filter(
            EquipmentType.is_active == True  # noqa
            if not auth_user.admin
            else True
        )
        .order_by(EquipmentType.id)
        .all()
    )
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


@equipment_types_blueprint.route(
    '/equipment-types/<int:equipment_type_id>', methods=['GET']
)
@require_auth(scopes=['equipments:read'])
def get_equipment_type(
    auth_user: User, equipment_type_id: int
) -> Union[Dict, HttpResponse]:
    """
    Get a type of equipment

    **Scope**: ``equipments:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/equipment-types/2 HTTP/1.1
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
              "has_equipments": true,
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
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``equipment_type not found``

    """
    equipment_type = EquipmentType.query.filter_by(
        id=equipment_type_id
    ).first()
    if equipment_type:
        if equipment_type.is_active is False and not auth_user.admin:
            return DataNotFoundErrorResponse('equipment_types')
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


@equipment_types_blueprint.route(
    '/equipment-types/<int:equipment_type_id>', methods=['PATCH']
)
@require_auth(scopes=['equipments:write'], as_admin=True)
def update_equipment_type(
    auth_user: User, equipment_type_id: int
) -> Union[Dict, HttpResponse]:
    """
    Update a type of equipment to (de)activate it.

    Authenticated user must be an admin.

    **Scope**: ``equipments:write``

    **Example request**:

    .. sourcecode:: http

      PATCH /api/equipment-types/2 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - success :

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "equipment_types": [
            {
              "has_equipments": true,
              "id": 2,
              "is_active": true,
              "label": "Bike"
            }
          ]
        },
        "status": "success"
      }

    :param integer equipment_type_id: equipment type id

    :<json boolean is_active: equipment type active status

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 400: ``invalid payload``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``equipment_type not found``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    data = request.get_json()
    if not data or data.get('is_active') is None:
        return InvalidPayloadErrorResponse()

    try:
        equipment_type = EquipmentType.query.filter_by(
            id=equipment_type_id
        ).first()
        if not equipment_type:
            return DataNotFoundErrorResponse('equipment_types')
        equipment_type.is_active = data.get('is_active')
        db.session.commit()
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
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)
