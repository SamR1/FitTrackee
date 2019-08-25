import json
import os
import shutil
from datetime import datetime, timedelta

from fittrackee_api import appLog, db
from flask import Blueprint, current_app, jsonify, request, send_file
from sqlalchemy import exc

from ..users.utils import (
    User, authenticate, can_view_activity, verify_extension
)
from .models import Activity
from .utils import (
    ActivityException, create_activity, edit_activity, get_absolute_file_path,
    get_datetime_with_tz, process_files
)
from .utils_format import convert_in_duration
from .utils_gpx import get_chart_data

activities_blueprint = Blueprint('activities', __name__)


@activities_blueprint.route('/activities', methods=['GET'])
@authenticate
def get_activities(auth_user_id):
    """
    Get activities for the authenticated user.

    **Example requests**:

    - without parameters

    .. sourcecode:: http

      GET /api/activities/ HTTP/1.1

    - with some query parameters

    .. sourcecode:: http

      GET /api/activities?from=2019-07-02&to=2019-07-31&sport_id=1  HTTP/1.1

    **Example responses**:

    - returning at least one activity

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "activities": [
              {
                "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                "ascent": null,
                "ave_speed": 10.0,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": null,
                "distance": 10.0,
                "duration": "0:17:04",
                "id": 1,
                "map": null,
                "max_alt": null,
                "max_speed": 10.0,
                "min_alt": null,
                "modification_date": null,
                "moving": "0:17:04",
                "next_activity": 3,
                "notes": null,
                "pauses": null,
                "previous_activity": null,
                "records": [
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": "0:17:04"
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "title": null,
                "user_id": 1,
                "weather_end": null,
                "weather_start": null,
                "with_gpx": false
              }
            ]
          },
          "status": "success"
        }

    - returning no activities

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
            "data": {
                "activities": []
            },
            "status": "success"
        }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)

    :query integer page: page if using pagination (default: 1)
    :query integer per_page: number of activities per page (default: 5)
    :query integer sport_id: sport id
    :query string from: start date (format: ``%Y-%m-%d``)
    :query string to: end date (format: ``%Y-%m-%d``)
    :query float distance_from: minimal distance
    :query float distance_to: maximal distance
    :query string duration_from: minimal duration (format: ``%H:%M``)
    :query string duration_to: maximal distance (format: ``%H:%M``)
    :query float ave_speed_from: minimal average speed
    :query float ave_speed_to: maximal average speed
    :query float max_speed_from: minimal max. speed
    :query float max_speed_to: maximal max. speed
    :query string order: sorting order (default: ``desc``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 500:

    """
    try:
        user = User.query.filter_by(id=auth_user_id).first()
        params = request.args.copy()
        page = 1 if 'page' not in params.keys() else int(params.get('page'))
        date_from = params.get('from')
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            _, date_from = get_datetime_with_tz(user.timezone, date_from)
        date_to = params.get('to')
        if date_to:
            date_to = datetime.strptime(f'{date_to} 23:59:59',
                                        '%Y-%m-%d %H:%M:%S')
            _, date_to = get_datetime_with_tz(user.timezone, date_to)
        distance_from = params.get('distance_from')
        distance_to = params.get('distance_to')
        duration_from = params.get('duration_from')
        duration_to = params.get('duration_to')
        ave_speed_from = params.get('ave_speed_from')
        ave_speed_to = params.get('ave_speed_to')
        max_speed_from = params.get('max_speed_from')
        max_speed_to = params.get('max_speed_to')
        order = params.get('order')
        sport_id = params.get('sport_id')
        per_page = int(params.get('per_page')) if params.get('per_page') else 5
        activities = Activity.query.filter(
            Activity.user_id == auth_user_id,
            Activity.sport_id == sport_id if sport_id else True,
            Activity.activity_date >= date_from if date_from else True,
            Activity.activity_date < date_to + timedelta(seconds=1)
            if date_to else True,
            Activity.distance >= int(distance_from) if distance_from else True,
            Activity.distance <= int(distance_to) if distance_to else True,
            Activity.moving >= convert_in_duration(duration_from)
            if duration_from else True,
            Activity.moving <= convert_in_duration(duration_to)
            if duration_to else True,
            Activity.ave_speed >= float(ave_speed_from)
            if ave_speed_from else True,
            Activity.ave_speed <= float(ave_speed_to)
            if ave_speed_to else True,
            Activity.max_speed >= float(max_speed_from)
            if max_speed_from else True,
            Activity.max_speed <= float(max_speed_to)
            if max_speed_to else True,
        ).order_by(
            Activity.activity_date.asc()
            if order == 'asc'
            else Activity.activity_date.desc()
        ).paginate(
            page, per_page, False
        ).items
        response_object = {
            'status': 'success',
            'data': {
                'activities': [activity.serialize(params)
                               for activity in activities]
            }
        }
        code = 200
    except Exception as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code


@activities_blueprint.route('/activities/<int:activity_id>', methods=['GET'])
@authenticate
def get_activity(auth_user_id, activity_id):
    """
    Get an activity

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/3 HTTP/1.1

    **Example responses**:

    - success

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "activities": [
              {
                "activity_date": "Sun, 07 Jul 2019 07:00:00 GMT",
                "ascent": null,
                "ave_speed": 16,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 18:57:14 GMT",
                "descent": null,
                "distance": 12,
                "duration": "0:45:00",
                "id": 3,
                "map": null,
                "max_alt": null,
                "max_speed": 16,
                "min_alt": null,
                "modification_date": "Sun, 14 Jul 2019 18:57:22 GMT",
                "moving": "0:45:00",
                "next_activity": 4,
                "notes": "activity without gpx",
                "pauses": null,
                "previous_activity": 3,
                "records": [],
                "segments": [],
                "sport_id": 1,
                "title": "biking on sunday morning",
                "user_id": 1,
                "weather_end": null,
                "weather_start": null,
                "with_gpx": false
              }
            ]
          },
          "status": "success"
        }

    - acitivity not found:

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

        {
          "data": {
            "activities": []
          },
          "status": "not found"
        }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
    :param integer activity_id: activity id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 403: You do not have permissions
    :statuscode 404: activity not found

    """
    activity = Activity.query.filter_by(id=activity_id).first()
    activities_list = []

    if activity:
        response_object, code = can_view_activity(
            auth_user_id, activity.user_id)
        if response_object:
            return jsonify(response_object), code

        activities_list.append(activity.serialize())
        status = 'success'
        code = 200
    else:
        status = 'not found'
        code = 404

    response_object = {
        'status': status,
        'data': {
            'activities': activities_list
        }
    }
    return jsonify(response_object), code


def get_activity_data(auth_user_id, activity_id, data_type):
    """Get data from an activity gpx file"""
    activity = Activity.query.filter_by(id=activity_id).first()
    content = ''
    if activity:
        response_object, code = can_view_activity(
            auth_user_id, activity.user_id)
        if response_object:
            return jsonify(response_object), code
        if not activity.gpx or activity.gpx == '':
            response_object = {
                'status': 'fail',
                'message': f'No gpx file for this activity (id: {activity_id})'
            }
            return jsonify(response_object), 400

        try:
            absolute_gpx_filepath = get_absolute_file_path(activity.gpx)
            if data_type == 'chart':
                content = get_chart_data(absolute_gpx_filepath)
            else:  # data_type == 'gpx'
                with open(absolute_gpx_filepath, encoding='utf-8') as f:
                    content = f.read()
        except Exception as e:
            appLog.error(e)
            response_object = {'status': 'error',
                               'message': 'internal error'}
            return jsonify(response_object), 500

        status = 'success'
        message = ''
        code = 200
    else:
        status = 'not found'
        message = f'Activity not found (id: {activity_id})'
        code = 404

    response_object = {'status': status,
                       'message': message,
                       'data': ({'chart_data': content}
                                if data_type == 'chart'
                                else {'gpx': content})}
    return jsonify(response_object), code


@activities_blueprint.route(
    '/activities/<int:activity_id>/gpx', methods=['GET']
)
@authenticate
def get_activity_gpx(auth_user_id, activity_id):
    """
    Get gpx file for an activity displayed on map with Leaflet

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/3/gpx HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "gpx": "gpx file content"
        },
        "message": "",
        "status": "success"
      }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
    :param integer activity_id: activity id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 400: no gpx file for this activity
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404: activity not found
    :statuscode 500:

    """
    return get_activity_data(auth_user_id, activity_id, 'gpx')


@activities_blueprint.route(
    '/activities/<int:activity_id>/chart_data', methods=['GET']
)
@authenticate
def get_activity_chart_data(auth_user_id, activity_id):
    """
    Get chart data from an activity gpx file, to display it with Recharts

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/3/chart HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "chart_data": [
            {
              "distance": 0,
              "duration": 0,
              "elevation": 279.4,
              "latitude": 51.5078118,
              "longitude": -0.1232004,
              "speed": 8.63,
              "time": "Fri, 14 Jul 2017 13:44:03 GMT"
            },
            {
              "distance": 7.5,
              "duration": 7380,
              "elevation": 280,
              "latitude": 51.5079733,
              "longitude": -0.1234538,
              "speed": 6.39,
              "time": "Fri, 14 Jul 2017 15:47:03 GMT"
            }
          ]
        },
        "message": "",
        "status": "success"
      }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
    :param integer activity_id: activity id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 400: no gpx file for this activity
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404: activity not found
    :statuscode 500:

    """
    return get_activity_data(auth_user_id, activity_id, 'chart')


@activities_blueprint.route('/activities/map/<map_id>', methods=['GET'])
def get_map(map_id):
    """
    Get map image for activities with gpx

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/map/fa33f4d996844a5c73ecd1ae24456ab8?1563529507772
        HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: image/png

    :param string map_id: activity map id

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404: map does not exist
    :statuscode 500:

    """
    try:
        activity = Activity.query.filter_by(map_id=map_id).first()
        if not activity:
            response_object = {
                'status': 'fail',
                'message': 'Map does not exist'
            }
            return jsonify(response_object), 404
        else:
            absolute_map_filepath = get_absolute_file_path(activity.map)
            return send_file(absolute_map_filepath)
    except Exception as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'internal error.'
        }
        return jsonify(response_object), 500


@activities_blueprint.route('/activities', methods=['POST'])
@authenticate
def post_activity(auth_user_id):
    """
    Post an activity with a gpx file

    **Example request**:

    .. sourcecode:: http

      POST /api/activities/ HTTP/1.1
      Content-Type: multipart/form-data

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

       {
          "data": {
            "activities": [
              {
                "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                "ascent": null,
                "ave_speed": 10.0,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": null,
                "distance": 10.0,
                "duration": "0:17:04",
                "id": 1,
                "map": null,
                "max_alt": null,
                "max_speed": 10.0,
                "min_alt": null,
                "modification_date": null,
                "moving": "0:17:04",
                "next_activity": 3,
                "notes": null,
                "pauses": null,
                "previous_activity": null,
                "records": [
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": "0:17:04"
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "title": null,
                "user_id": 1,
                "weather_end": null,
                "weather_start": null,
                "with_gpx": false
              }
            ]
          },
          "status": "success"
        }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)

    :form file: gpx file (allowed extensions: .gpx, .zip)
    :form data: sport id and notes (example: ``{"sport_id": 1, "notes": ""}``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: activity created
    :statuscode 400:
        - Invalid payload.
        - No file part.
        - No selected file.
        - File extension not allowed.
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 500:

    """
    response_object = verify_extension('activity', request)
    if response_object['status'] != 'success':
        return jsonify(response_object), 400

    activity_data = json.loads(request.form["data"])
    if not activity_data or activity_data.get('sport_id') is None:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    activity_file = request.files['file']
    upload_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'activities',
        str(auth_user_id))
    folders = {
        'extract_dir': os.path.join(upload_dir, 'extract'),
        'tmp_dir': os.path.join(upload_dir, 'tmp'),
    }

    try:
        new_activities = process_files(
            auth_user_id, activity_data, activity_file, folders
        )
        if len(new_activities) > 0:
            response_object = {
                'status': 'created',
                'data': {
                    'activities': [new_activity.serialize()
                                   for new_activity in new_activities]
                }
            }
            code = 201
        else:
            response_object = {
                'status': 'fail',
                'data': {
                    'activities': []
                }
            }
            code = 400
    except ActivityException as e:
        db.session.rollback()
        if e.e:
            appLog.error(e.e)
        response_object = {
            'status': e.status,
            'message': e.message,
        }
        code = 500 if e.status == 'error' else 400

    shutil.rmtree(folders['extract_dir'], ignore_errors=True)
    shutil.rmtree(folders['tmp_dir'], ignore_errors=True)
    return jsonify(response_object), code


@activities_blueprint.route('/activities/no_gpx', methods=['POST'])
@authenticate
def post_activity_no_gpx(auth_user_id):
    """
    Post an activity without gpx file

    **Example request**:

    .. sourcecode:: http

      POST /api/activities/no_gpx HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

       {
          "data": {
            "activities": [
              {
                "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                "ascent": null,
                "ave_speed": 10.0,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": null,
                "distance": 10.0,
                "duration": "0:17:04",
                "id": 1,
                "map": null,
                "max_alt": null,
                "max_speed": 10.0,
                "min_alt": null,
                "modification_date": null,
                "moving": "0:17:04",
                "next_activity": 3,
                "notes": null,
                "pauses": null,
                "previous_activity": null,
                "records": [
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": "0:17:04"
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "title": null,
                "user_id": 1,
                "weather_end": null,
                "weather_start": null,
                "with_gpx": false
              }
            ]
          },
          "status": "success"
        }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)

    :<json string activity_date: activity date  (format: ``%Y-%m-%d %H:%M``)
    :<json float distance: activity distance in km
    :<json integer duration: activity duration in seconds
    :<json string notes: notes (not mandatory)
    :<json integer sport_id: activity sport id
    :<json string title: activity title

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: activity created
    :statuscode 400: invalid payload
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 500:

    """
    activity_data = request.get_json()
    if not activity_data or activity_data.get('sport_id') is None \
            or activity_data.get('duration') is None \
            or activity_data.get('distance') is None \
            or activity_data.get('activity_date') is None:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    try:
        user = User.query.filter_by(id=auth_user_id).first()
        new_activity = create_activity(user, activity_data)
        db.session.add(new_activity)
        db.session.commit()

        response_object = {
            'status': 'created',
            'data': {
                'activities': [new_activity.serialize()]
            }
        }
        return jsonify(response_object), 201

    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'fail',
            'message': 'Error during activity save.'
        }
        return jsonify(response_object), 500


@activities_blueprint.route('/activities/<int:activity_id>', methods=['PATCH'])
@authenticate
def update_activity(auth_user_id, activity_id):
    """
    Update an activity

    **Example request**:

    .. sourcecode:: http

      PATCH /api/activities/1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

       {
          "data": {
            "activities": [
              {
                "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                "ascent": null,
                "ave_speed": 10.0,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": null,
                "distance": 10.0,
                "duration": "0:17:04",
                "id": 1,
                "map": null,
                "max_alt": null,
                "max_speed": 10.0,
                "min_alt": null,
                "modification_date": null,
                "moving": "0:17:04",
                "next_activity": 3,
                "notes": null,
                "pauses": null,
                "previous_activity": null,
                "records": [
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": "0:17:04"
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": 1,
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user_id": 1,
                    "value": 10.0
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "title": null,
                "user_id": 1,
                "weather_end": null,
                "weather_start": null,
                "with_gpx": false
              }
            ]
          },
          "status": "success"
        }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
    :param integer activity_id: activity id

    :<json string activity_date: activity date  (format: ``%Y-%m-%d %H:%M``)
        (only for activity without gpx)
    :<json float distance: activity distance in km
        (only for activity without gpx)
    :<json integer duration: activity duration in seconds
        (only for activity without gpx)
    :<json string notes: notes
    :<json integer sport_id: activity sport id
    :<json string title: activity title

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: activity updated
    :statuscode 400: invalid payload
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404: activity not found
    :statuscode 500:

    """
    activity_data = request.get_json()
    if not activity_data:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    try:
        activity = Activity.query.filter_by(id=activity_id).first()
        if activity:
            response_object, code = can_view_activity(
                auth_user_id, activity.user_id)
            if response_object:
                return jsonify(response_object), code

            activity = edit_activity(activity, activity_data, auth_user_id)
            db.session.commit()
            response_object = {
                'status': 'success',
                'data': {
                    'activities': [activity.serialize()]
                }
            }
            code = 200
        else:
            response_object = {
                'status': 'not found',
                'data': {
                    'activities': []
                }
            }
            code = 404
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code


@activities_blueprint.route(
    '/activities/<int:activity_id>', methods=['DELETE']
)
@authenticate
def delete_activity(auth_user_id, activity_id):
    """
    Delete an activity

    **Example request**:

    .. sourcecode:: http

      DELETE /api/activities/1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
    :param integer activity_id: activity id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 204: activity deleted
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404: activity not found
    :statuscode 500: Error. Please try again or contact the administrator.

    """

    try:
        activity = Activity.query.filter_by(id=activity_id).first()
        if activity:
            response_object, code = can_view_activity(
                auth_user_id, activity.user_id)
            if response_object:
                return jsonify(response_object), code

            db.session.delete(activity)
            db.session.commit()
            response_object = {
                'status': 'no content'
            }
            code = 204
        else:
            response_object = {
                'status': 'not found',
                'data': {
                    'activities': []
                }
            }
            code = 404
    except (exc.IntegrityError, exc.OperationalError, ValueError, OSError) \
            as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code
