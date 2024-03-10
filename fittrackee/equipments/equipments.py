from typing import Dict, Tuple, Union

from flask import Blueprint, request
from sqlalchemy import exc

from fittrackee import db
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    DataNotFoundErrorResponse,
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import User

from ..equipments.models import Equipment, EquipmentType

equipments_blueprint = Blueprint('equipments', __name__)


@equipments_blueprint.route('/equipments', methods=['GET'])
@require_auth(scopes=['equipments:read'])
def get_equipments(auth_user: User) -> Dict:
    """
    Get all user equipments.

    **Scope**: ``equipments:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/equipments HTTP/1.1
      Content-Type: application/json

    - with some query parameters (get all equipment of type "Shoes")

    .. sourcecode:: http

      GET /api/equipment?equipment_type_id=1  HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

    {
      "data": {
        "equipment": [
          {
            "creation_date": "Tue, 21 Mar 2023 06:08:06 GMT",
            "description": "The first shoes added to FitTrackee",
            "equipment_type": {
              "id": 1,
              "is_active": true,
              "label": "Shoe"
            },
            "id": 8,
            "is_active": true,
            "label": "My shoes",
            "total_distance": 0.0,
            "total_duration": "0:00:00",
            "user_id": 1,
            "workouts_count": 0
        },
        {
            "creation_date": "Tue, 21 Mar 2023 06:08:29 GMT",
            "description": "The second shoes added to FitTrackee",
            "equipment_type": {
              "id": 1,
              "is_active": true,
              "label": "Shoe"
            },
            "id": 9,
            "is_active": true,
            "label": "My shoes 2",
            "total_distance": 0.0,
            "total_duration": "0:00:00",
            "user_id": ,
            "workouts_count": 0
            }
          ]
        }
      },
      "status": "success"
    }

    :query integer equipment_type_id: equipment type id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``

    """
    params = request.args.copy()
    type_id = params.get('equipment_type_id', None)

    equipments = (
        Equipment.query.filter(
            Equipment.user_id == auth_user.id,
            Equipment.equipment_type_id == type_id if type_id else True,
        )
        .order_by(Equipment.id)
        .all()
    )

    return {
        'status': 'success',
        'data': {
            'equipments': [equipment.serialize() for equipment in equipments]
        },
    }


@equipments_blueprint.route('/equipments/<int:equipment_id>', methods=['GET'])
@require_auth(scopes=['equipments:read'])
def get_equipment_by_id(
    auth_user: User, equipment_id: int
) -> Union[Dict, HttpResponse]:
    """
    Get an equipment item

    **Scope**: ``equipments:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/equipment/1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - success

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "equipment": [
            {
              "description": "Another piece of equipment",
              "id": 3,
              "is_active": true,
              "label": "Other user Equipment",
              "total_distance": 0.0,
              "user_id": 2,
              "workouts_count": 0
            }
          ]
        }
      },
      "status": "success"
      }

    - equipment not found

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

      {
          "status": "not found",
          "data": {
              "equipment": []
          }
      }

    :param integer equipment_id: equipment id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``equipment not found``

    """
    filter_args = {'id': equipment_id, 'user_id': auth_user.id}
    equipment = Equipment.query.filter_by(**filter_args).first()
    if equipment:
        return {
            'status': 'success',
            'data': {'equipments': [equipment.serialize()]},
        }
    return DataNotFoundErrorResponse('equipments')


@equipments_blueprint.route('/equipments', methods=['POST'])
@require_auth(scopes=['equipments:write'])
def post_equipment(
    auth_user: User,
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Post a new piece of equipment.

    **Scope**: ``equipments:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/equipment HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

        {
          "data": {
            "equipment": [
              {
                "description": null,
                "id": 12,
                "is_active": true,
                "label": "New equipment from API",
                "total_distance": 0.0,
                "user_id": 1,
                "workouts_count": 0
              }
            ]
          },
          "status": "created"
        }
    :<json string label: a brief (less than 50 characters) label for
        the piece of equipment
    :<json int equipment_type: the ID for an equipment type
    :<json string description: a (perhaps longer) description of the
        equipment (limited to 200 characters, optional)
    :<json bool is_active: whether or not this equipment is currently
        active (default: true)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: equipment created
    :statuscode 400: invalid payload
       - ``The 'label' and 'equipment_type_id' parameters must be provided``
       - ``equipment already exists with the same label``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``equipment not found``
    :statuscode 500: ``Error during equipment save``
    """
    equipment_data = request.get_json()
    if (
        not equipment_data
        or not equipment_data.get('label')
        or equipment_data.get('equipment_type_id') is None
    ):
        return InvalidPayloadErrorResponse(
            "The 'label' and 'equipment_type_id' parameters must be "
            "provided"
        )

    label = equipment_data['label']
    if len(label) > 50:
        return InvalidPayloadErrorResponse("label exceeds 50 characters")
    equipment_type_id = equipment_data['equipment_type_id']

    if (
        Equipment.query.filter_by(user_id=auth_user.id, label=label).first()
        is not None
    ):
        return InvalidPayloadErrorResponse(
            "equipment already exists with the same label"
        )

    if not EquipmentType.query.filter_by(id=equipment_type_id).first():
        return InvalidPayloadErrorResponse("invalid equipment type")

    try:
        new_equipment = Equipment(
            user_id=auth_user.id,
            label=label,
            equipment_type_id=equipment_type_id,
            is_active=True,
            description=equipment_data.get('description'),
        )
        db.session.add(new_equipment)
        db.session.commit()

        return (
            {
                'status': 'created',
                'data': {'equipments': [new_equipment.serialize()]},
            },
            201,
        )

    except (exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(
            error=e,
            message='Error during equipment save',
            status='fail',
            db=db,
        )


@equipments_blueprint.route(
    '/equipments/<int:equipment_id>', methods=['PATCH']
)
@require_auth(scopes=['equipments:write'])
def update_equipment(
    auth_user: User, equipment_id: int
) -> Union[Dict, HttpResponse]:
    """
    Update a piece of equipment. Allows a user to change one of their
    equipment's label, description, type or active status.

    **Scope**: ``equipments:write``

    **Example request**:

    .. sourcecode:: http

      PATCH /api/equipment/1 HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - success

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "equipment": [
              {
                "creation_date": "Tue, 21 Mar 2023 06:28:10 GMT",
                "description": "Change bike to shoes",
                "equipment_type": 1,
                "id": 11,
                "is_active": true,
                "label": "Updated bike",
                "num_workouts": 0,
                "total_distance": 0.0,
                "total_duration": "0:00:00",
                "user_id": 1
              }
            ]
          },
          "status": "success"
        }

    - equipment not found

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

      {
        "data": {
          "equipment": []
        },
        "status": "not found"
      }

    :param integer equipment_id: equipment id

    :<json string label: a brief (less than 50 characters) label for
        the piece of equipment
    :<json int equipment_type_id: the ID for an equipment type
    :<json string description: a (perhaps longer) description of the
        equipment (limited to 200 characters, optional)
    :<json bool is_active: whether or not this equipment is currently
        active (default: true)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: equipment updated
    :statuscode 400: ``invalid payload``
        - ``no request data was supplied``
        - ``no valid parameters supplied``
        - ``equipment already exists with the same label``
        - ``invalid equipment type id``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``equipment not found``
    :statuscode 500: ``Error during equipment update``

    """
    equipment_data = request.get_json()
    if not equipment_data:
        return InvalidPayloadErrorResponse('no request data was supplied')

    if not any(
        e in ['label', 'description', 'equipment_type_id', 'is_active']
        for e in equipment_data
    ):
        return InvalidPayloadErrorResponse('no valid parameters supplied')

    try:
        equipment = Equipment.query.filter_by(
            id=equipment_id, user_id=auth_user.id
        ).first()
        if not equipment:
            return DataNotFoundErrorResponse('equipments')

        # set new values if they were in the request
        if 'is_active' in equipment_data:
            equipment.is_active = equipment_data.get('is_active')
        if 'label' in equipment_data:
            label = equipment_data.get('label')
            if len(label) > 50:
                return InvalidPayloadErrorResponse(
                    "label exceeds 50 characters"
                )
            if (
                Equipment.query.filter(
                    Equipment.user_id == auth_user.id,
                    Equipment.label == label,
                    Equipment.id != equipment.id,
                ).first()
                is not None
            ):
                return InvalidPayloadErrorResponse(
                    "equipment already exists with the same label"
                )
            equipment.label = label
        if 'description' in equipment_data:
            equipment.description = equipment_data.get('description')
        if 'equipment_type_id' in equipment_data:
            equipment_type_id = equipment_data.get('equipment_type_id')
            if not EquipmentType.query.filter_by(id=equipment_type_id).first():
                return InvalidPayloadErrorResponse("invalid equipment type id")
            equipment.equipment_type_id = equipment_type_id
        db.session.commit()

        return {
            'status': 'success',
            'data': {'equipments': [equipment.serialize()]},
        }

    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(
            error=e,
            db=db,
            message='Error during equipment update',
            status='fail',
        )


@equipments_blueprint.route(
    '/equipments/<int:equipment_id>', methods=['DELETE']
)
@require_auth(scopes=['equipments:write'])
def delete_equipment(
    auth_user: User, equipment_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Delete a piece of equipment.

    A user can only delete their own equipment, and
    only if there are no workouts associated with that equipment (unless
    forced). If equipment was associated with any workouts and deletion is
    forced, the association between this equipment and those workouts will
    be removed. If this equipment was a default for any sport, that default
    will be removed (set to NULL).

    **Scope**: ``equipments:write``

    **Example request**:

    .. sourcecode:: http

      DELETE /api/equipment/2 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :param integer equipment_id: equipment id
    :query force: if supplied as argument (no value required), will force
                  deletion of the equipment and remove that equipment
                  from associated workouts

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 204: equipment deleted
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you cannot delete equipment that has workouts associated with it
          without 'force' parameter``
    :statuscode 404: ``equipment not found``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    force_delete = 'force' in request.args

    try:
        equipment = Equipment.query.filter_by(
            id=equipment_id, user_id=auth_user.id
        ).first()
        if not equipment:
            return DataNotFoundErrorResponse('equipments')
        if len(equipment.workouts) > 0 and not force_delete:
            return ForbiddenErrorResponse(
                f"Cannot delete equipment that has associated workouts. "
                f"Equipment id {equipment.id} has {len(equipment.workouts)} "
                f"associated "
                f"workout{'' if len(equipment.workouts) == 1 else 's'}. "
                f"(Provide argument 'force' as a query parameter to "
                f"override this check)"
            )
        # other condition for deleting attachment to workouts
        # is handled by database cascading

        # NULLing of user sport preferences handled by database cascading

        # delete equipment row
        db.session.query(Equipment).filter(
            Equipment.id == equipment.id
        ).delete()
        db.session.commit()
        return {'status': 'no content'}, 204
    except (
        exc.IntegrityError,
        exc.OperationalError,
        ValueError,
        OSError,
    ) as e:  # pragma: no cover
        return handle_error_and_return_response(e, db=db)