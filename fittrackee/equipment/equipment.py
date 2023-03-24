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

from ..equipment.models import Equipment
from ..users.models import UserSportPreference

equipment_blueprint = Blueprint('equipment', __name__)
equipment_type_blueprint = Blueprint('equipment_type', __name__)


@equipment_blueprint.route('/equipment', methods=['GET'])
@require_auth(scopes=['profile:read'])
def get_equipment(auth_user: User) -> Dict:
    """
    Get all equipment. If non-admin, only the user's equipment
    will be shown. If admin, all equipment is shown unless the
    "just_me" parameter is given.

    **Scope**: ``profile:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/equipment HTTP/1.1
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
				"equipment_type": 1,
				"id": 8,
				"is_active": true,
				"label": "My shoes",
				"num_workouts": 0,
				"total_distance": 0.0,
				"total_duration": "0:00:00",
				"user_id": 1
			},
			{
				"creation_date": "Tue, 21 Mar 2023 06:08:29 GMT",
				"description": "The second shoes added to FitTrackee",
				"equipment_type": 1,
				"id": 9,
				"is_active": true,
				"label": "My shoes 2",
				"num_workouts": 0,
				"total_distance": 0.0,
				"total_duration": "0:00:00",
				"user_id": 1
			}
          ]
      },
      "status": "success"
    }

    :query only_user: if supplied as argument (no value required),
        will return only equipment of authorized user, even if they
        have admin rights
    :query integer equipment_type_id: equipment type id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again

    """
    params = request.args.copy()
    type_id = params.get('equipment_type_id', None)
    only_user = 'only_user' in [k.lower() for k in request.args.keys()]

    if not auth_user.admin or (auth_user.admin and only_user):
        equipment = (
            Equipment.query.filter(
                Equipment.user_id == auth_user.id,
                Equipment.equipment_type_id == type_id if type_id else True
            ).order_by(Equipment.id)
            .all()
        )
    else:
        equipment = Equipment.query.filter(
            Equipment.equipment_type_id == type_id if type_id else True
        ).order_by(Equipment.id).all()

    equipment_data = []
    for e in equipment:
        equipment_data.append(e.serialize())
    return {
        'status': 'success',
        'data': {'equipment': equipment_data},
    }


@equipment_blueprint.route('/equipment/<int:equipment_id>', methods=['GET'])
@require_auth(scopes=['profile:read'])
def get_equipment_by_id(
    auth_user: User, equipment_id: int
) -> Union[Dict, HttpResponse]:
    """
    Get an equipment item

    **Scope**: ``profile:read``

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
                      "num_workouts": 0,
                      "total_distance": 0.0,
                      "user_id": 2
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
          "status": "not found",
          "data": {
              "equipment": []
          }
      }

    :param integer equipment_id: equipment id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 404: equipment not found

    """
    filter_args = {'id': equipment_id}
    if not auth_user.admin:
        # only filter by user_id if user is not admin
        filter_args['user_id'] = auth_user.id

    equipment = Equipment.query.filter_by(**filter_args).first()
    if equipment:
        return {
            'status': 'success',
            'data': {'equipment': [equipment.serialize()]},
        }
    return DataNotFoundErrorResponse('equipment')


@equipment_blueprint.route('/equipment', methods=['POST'])
@require_auth(scopes=['profile:write'])
def post_equipment(
    auth_user: User,
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Post a new piece of equipment.

    **Scope**: ``profile:write``

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
                        "num_workouts": 0,
                        "total_distance": 0.0,
                        "user_id": 1
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
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 500:

    """
    equipment_data = request.get_json()
    if not equipment_data or \
        equipment_data.get('label') is None or \
        equipment_data.get('equipment_type') is None:
        return InvalidPayloadErrorResponse(
            'The "label" and "equipment_type" parameters must be '
            'provided in the body of the request'
        )
    is_active = equipment_data.get('is_active', True)

    try:
        new_equipment = Equipment(
            user_id=auth_user.id,
            label=equipment_data.get('label'),
            equipment_type_id=equipment_data.get('equipment_type'),
            is_active=is_active,
            description=equipment_data.get('description', None)
        )
        db.session.add(new_equipment)
        db.session.commit()

        return (
            {
                'status': 'created',
                'data': {'equipment': [new_equipment.serialize()]},
            },
            201,
        )

    except (exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(
            error=e,
            message='Error during equipment save.',
            status='fail',
            db=db,
        )


@equipment_blueprint.route('/equipment/<int:equipment_id>', methods=['PATCH'])
@require_auth(scopes=['profile:write'])
def update_equipment(
    auth_user: User, equipment_id: int
) -> Union[Dict, HttpResponse]:
    """
    Update a piece of equipment. Allows a user to change one of their
    equipment's label, description, or active status.

    **Scope**: ``profile:write``

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
    :<json int equipment_type: the ID for an equipment type
    :<json string description: a (perhaps longer) description of the
        equipment (limited to 200 characters, optional)
    :<json bool is_active: whether or not this equipment is currently
        active (default: true)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: equipment updated
    :statuscode 400: invalid payload
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403: you do not have permissions
    :statuscode 404: equipment not found
    :statuscode 500:

    """
    equipment_data = request.get_json()
    if not equipment_data:
        return InvalidPayloadErrorResponse('No request data was supplied')

    try:
        equipment = Equipment.query.filter_by(
            id=equipment_id, user_id=auth_user.id
        ).first()
        if not equipment:
            return DataNotFoundErrorResponse('equipment')

        # set new values if they were in the request
        if 'is_active' in equipment_data:
            equipment.is_active = equipment_data.get('is_active')
        if 'label' in equipment_data:
            equipment.label = equipment_data.get('label')
        if 'description' in equipment_data:
            equipment.description = equipment_data.get('description')
        if 'equipment_type' in equipment_data:
            equipment.equipment_type_id = equipment_data.get('equipment_type')
        db.session.commit()

        return {
            'status': 'success',
            'data': {'equipment': [equipment.serialize()]},
        }

    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@equipment_blueprint.route(
    '/equipment/<int:equipment_id>',
    methods=['DELETE'])
@require_auth(scopes=['profile:write'])
# TODO: is it possible to have conditional scope requirment?
def delete_equipment(
    auth_user: User, equipment_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Delete a piece of equipment.

    A user can only delete their own equipment (unless they're an admin), and
    only if there are no workouts associated with that equipment (unless
    forced). If equipment was associated with any workouts and deletion is
    forced, the association between this equipment and those workouts will
    be removed. If this equipment was a default for any sport, that default will 
    be removed (set to NULL).

    **Scope**: ``profile:write`` (and ``workouts:write`` if 
               deleting equipment with workouts)

    **Example request**:

    .. sourcecode:: http

      DELETE /api/equipment/2 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :param integer equipment_id: equipment id
    :query force: if supplied as argument (no value requires), will force
                  deletion of the equipment and remove that equipment
                  from associated workouts (not yet implemented)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 204: equipment deleted
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403:
        - you cannot delete another user's equipment without admin rights
        - you cannot delete equipment that has workouts associated with it (and "force" parameter was not supplied)
    :statuscode 404:
        - equipment does not exist
    :statuscode 500: error, please try again or contact the administrator

    """
    force_delete = 'force' in request.args

    try:
        equipment = Equipment.query.filter_by(id=equipment_id).first()
        if not equipment:
            return DataNotFoundErrorResponse('equipment')
        if equipment.user_id != auth_user.id and not auth_user.admin:
            return ForbiddenErrorResponse(
                "Cannot delete another user's equipment without admin rights"
            )
        if len(equipment.workouts) > 0 and not force_delete:
            return ForbiddenErrorResponse(
                f"Cannot delete equipment that has associated workouts. "
                f"Equipment id {equipment.id} has {len(equipment.workouts)} "
                f"associated "
                f"workout{'' if len(equipment.workouts) == 1 else 's'}. "
                f"(Provide argument 'force' as a query parameter to "
                f"override this check)"
            )
        if len(equipment.workouts) > 0 and force_delete:
            ## this would be how to delete rows from equipment_workout 
            ## with this equipment id:
            # equipment.workouts = []
            # db.session.commit()
 
            return GenericErrorResponse(
                status_code=403,
                message="Deleting equipment with existing workouts is "
                        "not yet implemented"
            )

        # remove as any defaults for user sport preferences
        prefs_to_fix = db.session.query(UserSportPreference).filter(
            UserSportPreference.user_id == equipment.user_id,
            UserSportPreference.default_equipment_id == equipment.id
        ).all()
        for up in prefs_to_fix:
            up.default_equipment_id = None
        db.session.commit()

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
    ) as e:
        return handle_error_and_return_response(e, db=db)
