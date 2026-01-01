from typing import Dict

from flask import Blueprint
from sqlalchemy.sql import select
from sqlalchemy.sql import text as sql_text

from fittrackee import db
from fittrackee.oauth2.server import require_auth
from fittrackee.users.models import User

from .constants import SPORTS_WITHOUT_ELEVATION_DATA
from .models import Record

records_blueprint = Blueprint("records", __name__)


@records_blueprint.route("/records", methods=["GET"])
@require_auth(scopes=["workouts:read"])
def get_records(auth_user: User) -> Dict:
    """
    Get all records for authenticated user.

    Following types of records are available, depending en sport:
        - average pace (record_type: ``AP``)
        - average speed (record_type: ``AS``)
        - best pace (record_type: ``BP``)
        - farthest distance (record_type: ``FD``)
        - highest ascent (record_type: ``HA``)
        - longest duration (record_type: ``LD``)
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
              "id": 15,
              "record_type": "BP",
              "sport_id": 5,
              "user": "admin",
              "value": "0:05:58",
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
    params = {
        "user_id": auth_user.id,
        "sports_without_elevation_data": tuple(SPORTS_WITHOUT_ELEVATION_DATA),
    }
    sql = """
          SELECT records.*
          FROM records
          JOIN sports ON records.sport_id = sports.id
          LEFT OUTER JOIN users_sports_preferences usp 
                       ON usp.sport_id = records.sport_id AND
                          usp.user_id = records.user_id
          WHERE records.user_id = :user_id AND
            (
              records.record_type IN ('FD', 'LD') OR ( 
                records.record_type = 'HA' AND
                sports.label NOT IN :sports_without_elevation_data
              ) OR (
                records.record_type IN ('AS', 'MS') AND
                (
                  usp.pace_speed_display <> 'PACE' OR ( 
                    usp.pace_speed_display IS NULL AND
                    sports.pace_speed_display <> 'PACE'
                  )
                )
              ) OR (
                records.record_type IN ('AP', 'BP') AND
                (
                  usp.pace_speed_display <> 'SPEED' OR (
                    usp.pace_speed_display IS NULL AND
                    sports.pace_speed_display <> 'SPEED'
                  )
                )
              )
            )
          ORDER BY records.sport_id, records.record_type;"""

    records = db.session.scalars(  # type: ignore
        select(Record).from_statement(sql_text(sql)).params(**params)
    ).all()

    return {
        "status": "success",
        "data": {"records": [record.serialize() for record in records]},
    }
