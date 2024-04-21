from datetime import timedelta
from typing import Dict, List, Tuple, Union

from flask import Blueprint, request
from sqlalchemy import exc, func
from sqlalchemy.dialects.postgresql import insert

from fittrackee import db
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    DataNotFoundErrorResponse,
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import (
    User,
    UserSportPreference,
    UserSportPreferenceEquipment,
)
from fittrackee.utils import decode_short_id
from fittrackee.workouts.models import Sport, Workout, WorkoutEquipment

from .exceptions import InvalidEquipmentsException
from .models import Equipment, EquipmentType
from .utils import SPORT_EQUIPMENT_TYPES

equipments_blueprint = Blueprint('equipments', __name__)


def handle_default_sports(
    default_for_sport_ids: List[int],
    auth_user: User,
    equipment_type: EquipmentType,
) -> List[UserSportPreference]:
    user_sport_preferences = []
    for sport_id in default_for_sport_ids:
        sport = Sport.query.filter_by(id=sport_id).first()
        if not sport:
            raise InvalidEquipmentsException(
                f"sport (id {sport_id}) does not exist"
            )

        # check if sport is valid for equipment type
        if sport.label not in SPORT_EQUIPMENT_TYPES.get(
            equipment_type.label, []
        ):
            raise InvalidEquipmentsException(
                f"invalid sport '{sport.label}' for equipment "
                f"type '{equipment_type.label}'"
            )

        user_sport_preference = UserSportPreference.query.filter_by(
            user_id=auth_user.id,
            sport_id=sport_id,
        ).first()
        if not user_sport_preference:
            user_sport_preference = UserSportPreference(
                user_id=auth_user.id,
                sport_id=sport_id,
                stopped_speed_threshold=sport.stopped_speed_threshold,
            )
            db.session.add(user_sport_preference)
            db.session.flush()
        user_sport_preferences.append(user_sport_preference)
    return user_sport_preferences


@equipments_blueprint.route('/equipments', methods=['GET'])
@require_auth(scopes=['equipments:read'])
def get_equipments(auth_user: User) -> Dict:
    """
    Get all user equipments.
    Only the equipment owner can see his equipment.

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
          "equipments": [
            {
              "creation_date": "Tue, 21 Mar 2023 06:08:06 GMT",
              "default_for_sport_ids": [],
              "description": "The first shoes added to FitTrackee",
              "equipment_type": {
                "id": 1,
                "is_active": true,
                "label": "Shoe"
              },
              "id": "2UkrViYShoAkg8qSUKnUS4",
              "is_active": true,
              "label": "My shoes",
              "total_distance": 0.0,
              "total_duration": "0:00:00",
              "total_moving": "0:00:00",
              "user_id": 1,
              "workouts_count": 0
          },
          {
              "creation_date": "Tue, 21 Mar 2023 06:08:29 GMT",
              "default_for_sport_ids": [],
              "description": "The second shoes added to FitTrackee",
              "equipment_type": {
                "id": 1,
                "is_active": true,
                "label": "Shoe"
              },
              "id": "2UkrViYShoAkg8qSUKnUS4",
              "is_active": true,
              "label": "My shoes 2",
              "total_distance": 0.0,
              "total_duration": "0:00:00",
              "total_moving": "0:00:00",
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


@equipments_blueprint.route(
    '/equipments/<string:equipment_short_id>', methods=['GET']
)
@require_auth(scopes=['equipments:read'])
def get_equipment_by_id(
    auth_user: User, equipment_short_id: str
) -> Union[Dict, HttpResponse]:
    """
    Get an equipment item.
    Only the equipment owner can see his equipment.

    **Scope**: ``equipments:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/equipments/2UkrViYShoAkg8qSUKnUS4 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - success

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "equipments": [
            {
              "creation_date": "Tue, 21 Mar 2023 06:08:06 GMT",
              "default_for_sport_ids": [],
              "description": "Another piece of equipment",
              "equipment_type": {
                "id": 1,
                "is_active": true,
                "label": "Shoe"
              },
              "id": "2UkrViYShoAkg8qSUKnUS4",
              "is_active": true,
              "label": "Other user Equipment",
              "total_distance": 0.0,
              "total_duration": "0:00:00",
              "total_moving": "0:00:00",
              "user_id": 2,
              "workouts_count": 0
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
          "equipments": []
        },
        "status": "not found"
      }

    :param string equipment_short_id: equipment short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``equipment not found``

    """
    filter_args = {
        'uuid': decode_short_id(equipment_short_id),
        'user_id': auth_user.id,
    }
    equipment = Equipment.query.filter_by(**filter_args).first()
    if equipment:
        return {
            'status': 'success',
            'data': {'equipments': [equipment.serialize()]},
        }
    return DataNotFoundErrorResponse('equipments')


@equipments_blueprint.route('/equipments', methods=['POST'])
@require_auth(scopes=['equipments:write'])
def post_equipment(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Post a new piece of equipment.

    **Scope**: ``equipments:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/equipments HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

      {
        "data": {
          "equipments": [
            {
              "creation_date": "Tue, 21 Mar 2023 06:08:29 GMT",
              "default_for_sport_ids": [],
              "description": null,
              "equipment_type": {
                "id": 1,
                "is_active": true,
                "label": "Shoe"
              },
              "id": "2UkrViYShoAkg8qSUKnUS4",
              "is_active": true,
              "label": "New equipment from API",
              "total_distance": 0.0,
              "total_duration": "0:00:00",
              "total_moving": "0:00:00",
              "user_id": 1,
              "workouts_count": 0
            }
          ]
        },
        "status": "created"
      }

    :<json string label: a brief (less than 50 characters) label for
        the piece of equipment
    :<json integer equipment_type: the ID for an equipment type (it must be
        active)
    :<json string description: a (perhaps longer) description of the
        equipment (limited to 200 characters, optional)
    :<json boolean is_active: whether or not this equipment is currently
        active (default: ``true``)
    :<json array of integers default_for_sport_ids: the default sport ids
        to use for this equipment, not mandatory

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: equipment created
    :statuscode 400:
        - ``the 'label' and 'equipment_type_id' parameters must be provided``
        - ``equipment already exists with the same label``
        - ``label exceeds 50 characters``
        - ``invalid equipment type id``
        - ``equipment type is inactive``
        - ``sport (id <sport_id>) does not exist``
        - ``invalid sport '<sport_label>' for equipment
          type '<equipment_type_label>'``
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
            "the 'label' and 'equipment_type_id' parameters must be "
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

    equipment_type = EquipmentType.query.filter_by(
        id=equipment_type_id
    ).first()
    if not equipment_type:
        return InvalidPayloadErrorResponse("invalid equipment type id")
    if not equipment_type.is_active:
        return InvalidPayloadErrorResponse("equipment type is inactive")

    default_for_sport_ids = equipment_data.get("default_for_sport_ids", [])
    try:
        user_sport_preferences = handle_default_sports(
            default_for_sport_ids, auth_user, equipment_type
        )
    except InvalidEquipmentsException as e:
        return InvalidPayloadErrorResponse(str(e))

    try:
        new_equipment = Equipment(
            user_id=auth_user.id,
            label=label,
            equipment_type_id=equipment_type_id,
            is_active=True,
            description=equipment_data.get('description'),
        )
        db.session.add(new_equipment)
        db.session.flush()
        if user_sport_preferences:
            # remove existing equipments for default sports
            # (for now only one default equipment/sport)
            db.session.query(UserSportPreferenceEquipment).filter(
                UserSportPreferenceEquipment.c.user_id == auth_user.id,
                UserSportPreferenceEquipment.c.sport_id.in_(
                    default_for_sport_ids
                ),
            ).delete()

            db.session.execute(
                insert(UserSportPreferenceEquipment).values(
                    [
                        {
                            "equipment_id": new_equipment.id,
                            "sport_id": sport.sport_id,
                            "user_id": auth_user.id,
                        }
                        for sport in user_sport_preferences
                    ]
                )
            )
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
    '/equipments/<string:equipment_short_id>', methods=['PATCH']
)
@require_auth(scopes=['equipments:write'])
def update_equipment(
    auth_user: User, equipment_short_id: str
) -> Union[Dict, HttpResponse]:
    """
    Update a piece of equipment. Allows a user to change one of their
    equipment's label, description, type or active status.

    Changing equipment type will remove all existing workouts associations
    for that piece of equipment and default sports.

    **Scope**: ``equipments:write``

    **Example request**:

    .. sourcecode:: http

      PATCH /api/equipments/QRj7BY6H2iYjSV8sersFgV HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - success

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "equipments": [
              {
                "creation_date": "Tue, 21 Mar 2023 06:28:10 GMT",
                "default_for_sport_ids": [],
                "description": "Change bike to shoes",
                "equipment_type": {
                  "id": 1,
                  "is_active": true,
                  "label": "Shoe"
                },
                "id": "QRj7BY6H2iYjSV8sersFgV",
                "is_active": true,
                "label": "Updated bike",
                "total_distance": 0.0,
                "total_duration": "0:00:00",
                "total_moving": "0:00:00",
                "user_id": 1,
                "workouts_count": 0
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
          "equipments": []
        },
        "status": "not found"
      }

    :param string equipment_short_id: equipment short id

    :<json string label: a brief (less than 50 characters) label for
        the piece of equipment
    :<json int equipment_type_id: the ID for an equipment type (it must be
        active)
    :<json string description: a (perhaps longer) description of the
        equipment (limited to 200 characters, optional)
    :<json boolean is_active: whether or not this equipment is currently
        active (default: ``true``)
    :<json array of integers default_for_sport_ids: the default sport ids
        to use for this equipment

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: equipment updated
    :statuscode 400:
        - ``no request data was supplied``
        - ``no valid parameters supplied``
        - ``equipment already exists with the same label``
        - ``label exceeds 50 characters``
        - ``invalid equipment type id``
        - ``equipment type is inactive``
        - ``sport (id <sport_id>) does not exist``
        - ``invalid sport '<sport_label>' for equipment
          type '<equipment_type_label>'``
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
        e
        in [
            'label',
            'description',
            'equipment_type_id',
            'is_active',
            'default_for_sport_ids',
        ]
        for e in equipment_data
    ):
        return InvalidPayloadErrorResponse('no valid parameters supplied')

    new_default_for_sport_ids = equipment_data.get(
        "default_for_sport_ids", None
    )
    user_sport_preferences = None
    try:
        equipment = Equipment.query.filter_by(
            uuid=decode_short_id(equipment_short_id), user_id=auth_user.id
        ).first()
        if not equipment:
            return DataNotFoundErrorResponse('equipments')

        check_default_sports = True
        equipment_type = equipment.equipment_type

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
            equipment_type = EquipmentType.query.filter_by(
                id=equipment_type_id
            ).first()
            if not equipment_type:
                return InvalidPayloadErrorResponse("invalid equipment type id")
            if equipment_type.id != equipment.equipment_type_id:
                if not equipment_type.is_active:
                    return InvalidPayloadErrorResponse(
                        "equipment type is inactive"
                    )

                # remove workouts association on type change
                db.session.query(WorkoutEquipment).filter(
                    WorkoutEquipment.c.equipment_id == equipment.id
                ).delete()
                equipment.total_distance = 0.0
                equipment.total_duration = timedelta()
                equipment.total_moving = timedelta()
                equipment.total_workouts = 0

                # remove default sports
                db.session.query(UserSportPreferenceEquipment).filter(
                    UserSportPreferenceEquipment.c.user_id == auth_user.id,
                    UserSportPreferenceEquipment.c.equipment_id
                    == equipment.id,
                ).all()

                # with changes on equipments but no changes on default sports,
                # the default sports are removed.
                if new_default_for_sport_ids is None or (
                    new_default_for_sport_ids
                    == [
                        sport_preference.sport_id
                        for sport_preference in equipment.default_for_sports
                    ]
                ):
                    new_default_for_sport_ids = []
                    check_default_sports = False

            equipment.equipment_type_id = equipment_type_id

        if check_default_sports and new_default_for_sport_ids is not None:
            try:
                user_sport_preferences = handle_default_sports(
                    new_default_for_sport_ids,
                    auth_user,
                    equipment_type,
                )
            except InvalidEquipmentsException as e:
                return InvalidPayloadErrorResponse(str(e))

        if new_default_for_sport_ids is not None:
            existing_sports = (
                db.session.query(UserSportPreferenceEquipment)
                .filter(
                    UserSportPreferenceEquipment.c.user_id == auth_user.id,
                    UserSportPreferenceEquipment.c.equipment_id
                    == equipment.id,
                )
                .all()
            )

            sport_ids_to_remove = {s[1] for s in existing_sports} - set(
                new_default_for_sport_ids
            )

            if sport_ids_to_remove:
                db.session.query(UserSportPreferenceEquipment).filter(
                    UserSportPreferenceEquipment.c.user_id == auth_user.id,
                    (
                        UserSportPreferenceEquipment.c.equipment_id
                        == equipment.id
                    ),
                    UserSportPreferenceEquipment.c.sport_id.in_(
                        sport_ids_to_remove
                    ),
                ).delete()

            if user_sport_preferences:
                # remove existing equipments for default sports
                # (for now only one default equipment/sport)
                db.session.query(UserSportPreferenceEquipment).filter(
                    UserSportPreferenceEquipment.c.user_id == auth_user.id,
                    UserSportPreferenceEquipment.c.sport_id.in_(
                        new_default_for_sport_ids
                    ),
                ).delete()

                db.session.execute(
                    insert(UserSportPreferenceEquipment)
                    .values(
                        [
                            {
                                "equipment_id": equipment.id,
                                "sport_id": sport.sport_id,
                                "user_id": auth_user.id,
                            }
                            for sport in user_sport_preferences
                        ]
                    )
                    .on_conflict_do_nothing()
                )
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
    '/equipments/<string:equipment_short_id>/refresh', methods=['POST']
)
@require_auth(scopes=['equipments:write'])
def refresh_equipment(
    auth_user: User, equipment_short_id: str
) -> Union[Dict, HttpResponse]:
    """
    Refresh equipment totals (in case values are incorrect).

    **Scope**: ``equipments:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/equipments/QRj7BY6H2iYjSV8sersFgV/refresh HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "equipments": [
              {
                "creation_date": "Tue, 21 Mar 2023 06:28:10 GMT",
                "default_for_sport_ids": [],
                "description": "My Shoes",
                "equipment_type": {
                  "id": 1,
                  "is_active": true,
                  "label": "Shoe"
                },
                "id": "QRj7BY6H2iYjSV8sersFgV",
                "is_active": true,
                "label": "Updated bike",
                "total_distance": 6.0,
                "total_duration": "1:10:00",
                "total_moving": "1:00:00",
                "user_id": 1,
                "workouts_count": 1
              }
            ]
          },
          "status": "success"
        }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: equipment updated
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``equipment not found``
    :statuscode 500: ``Error during equipment save``
    """
    equipment = Equipment.query.filter_by(
        uuid=decode_short_id(equipment_short_id), user_id=auth_user.id
    ).first()
    if not equipment:
        return DataNotFoundErrorResponse('equipments')

    try:
        totals = dict(
            db.session.query(
                func.sum(Workout.distance).label('total_distance'),
                func.sum(Workout.duration).label('total_duration'),
                func.sum(Workout.moving).label('total_moving'),
                func.count(Workout.id).label('total_workouts'),
            )
            .join(WorkoutEquipment)
            .filter(WorkoutEquipment.c.equipment_id == equipment.id)
            .first()
        )
        equipment.total_distance = (
            0.0
            if totals["total_distance"] is None
            else totals["total_distance"]
        )
        equipment.total_duration = (
            timedelta()
            if totals["total_duration"] is None
            else totals["total_duration"]
        )
        equipment.total_moving = (
            timedelta()
            if totals["total_moving"] is None
            else totals["total_moving"]
        )
        equipment.total_workouts = totals["total_workouts"]

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
    '/equipments/<string:equipment_short_id>', methods=['DELETE']
)
@require_auth(scopes=['equipments:write'])
def delete_equipment(
    auth_user: User, equipment_short_id: str
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

      DELETE /api/equipments/QRj7BY6H2iYjSV8sersFgV HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :param string equipment_short_id: equipment short id

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
    equipment_uuid = decode_short_id(equipment_short_id)

    try:
        equipment = Equipment.query.filter_by(
            uuid=equipment_uuid, user_id=auth_user.id
        ).first()
        if not equipment:
            return DataNotFoundErrorResponse('equipments')
        if equipment.total_workouts > 0 and not force_delete:
            return ForbiddenErrorResponse(
                f"Cannot delete equipment that has associated workouts. "
                f"Equipment id {equipment.short_id} has "
                f"{equipment.total_workouts} associated "
                f"workout{'' if equipment.total_workouts == 1 else 's'}. "
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
