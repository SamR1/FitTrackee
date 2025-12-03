from typing import Dict

from flask import Blueprint
from sqlalchemy import and_, or_

from fittrackee.oauth2.server import require_auth
from fittrackee.users.models import User

from .constants import PACE_SPORTS, SPORTS_WITHOUT_ELEVATION_DATA
from .models import Record, Sport

records_blueprint = Blueprint("records", __name__)


@records_blueprint.route("/records", methods=["GET"])
@require_auth(scopes=["workouts:read"])
def get_records(auth_user: User) -> Dict:
    """
    Get all records for authenticated user.

    Following types of records are available, depending en sport:
        - average pace (record_type: ``AP``)
        - average speed (record_type: ``AS``)
        - farthest distance (record_type: ``FD``)
        - highest ascent (record_type: ``HA``)
        - longest duration (record_type: ``LD``)
        - maximum pace (record_type: ``MP``)
        - maximum speed (record_type: ``MS``)

    **Scope**: ``workouts:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/records HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - returning records

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "records": [
            {
              "id": 14,
              "record_type": "AP",
              "sport_id": 5,
              "user": "admin",
              "value": "0:07:01",
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 9,
              "record_type": "AS",
              "sport_id": 5,
              "user": "admin",
              "value": 8.55,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 10,
              "record_type": "FD",
              "sport_id": 5,
              "user": "admin",
              "value": 2.858,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 13,
              "record_type": "HA",
              "sport_id": 5,
              "user": "Sam",
              "value": 7.029,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 11,
              "record_type": "LD",
              "sport_id": 5,
              "user": "admin",
              "value": "0:20:24",
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 15,
              "record_type": "MP",
              "sport_id": 5,
              "user": "admin",
              "value": "0:05:58",
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 12,
              "record_type": "MS",
              "sport_id": 5,
              "user": "admin",
              "value": 10.06,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            }
          ]
        },
        "status": "success"
      }

    - no records

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "records": []
        },
        "status": "success"
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``

    """
    records = (
        Record.query.join(Sport)
        .filter(
            Record.user_id == auth_user.id,
            or_(
                Record.record_type.in_(["AS", "FD", "LD", "MS"]),
                and_(
                    Record.record_type == "HA",
                    Sport.label.not_in(SPORTS_WITHOUT_ELEVATION_DATA),
                ),
                and_(
                    Record.record_type.in_(["AP", "MP"]),
                    Sport.label.in_(PACE_SPORTS),
                ),
            ),
        )
        .order_by(Record.sport_id.asc(), Record.record_type.asc())
        .all()
    )
    return {
        "status": "success",
        "data": {"records": [record.serialize() for record in records]},
    }
