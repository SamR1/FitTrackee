from flask import Blueprint, jsonify

from ..users.utils import authenticate
from .models import Record

records_blueprint = Blueprint('records', __name__)


@records_blueprint.route('/records', methods=['GET'])
@authenticate
def get_records(auth_user_id):
    """
    Get all records for authenticated user.

    Following types of records are available:
        - average speed (record_type: 'AS')
        - farest distance (record_type: 'FD')
        - longest duration (record_type: 'LD')
        - maximum speed (record_type: 'MS')

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
              "activity_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "activity_id": 4,
              "id": 9,
              "record_type": "AS",
              "sport_id": 1,
              "user_id": 1,
              "value": 18
            },
            {
              "activity_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "activity_id": 4,
              "id": 10,
              "record_type": "FD",
              "sport_id": 1,
              "user_id": 1,
              "value": 18
            },
            {
              "activity_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "activity_id": 7,
              "id": 11,
              "record_type": "LD",
              "sport_id": 1,
              "user_id": 1,
              "value": "1:01:00"
            },
            {
              "activity_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "activity_id": 4,
              "id": 12,
              "record_type": "MS",
              "sport_id": 1,
              "user_id": 1,
              "value": 18
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

    :param integer auth_user_id: authenticate user id (from JSON Web Token)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.

    """

    records = (
        Record.query.filter_by(user_id=auth_user_id)
        .order_by(Record.sport_id.asc(), Record.record_type.asc())
        .all()
    )
    response_object = {
        'status': 'success',
        'data': {'records': [record.serialize() for record in records]},
    }
    return jsonify(response_object), 200
