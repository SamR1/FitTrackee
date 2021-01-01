import json
import os
import shutil
from datetime import datetime, timedelta

import requests
from fittrackee import appLog, db
from fittrackee.responses import (
    DataInvalidPayloadErrorResponse,
    DataNotFoundErrorResponse,
    InternalServerErrorResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    handle_error_and_return_response,
)
from flask import Blueprint, Response, current_app, request, send_file
from sqlalchemy import exc

from ..users.utils import (
    User,
    authenticate,
    can_view_activity,
    verify_extension_and_size,
)
from .models import Activity
from .utils import (
    ActivityException,
    create_activity,
    edit_activity,
    get_absolute_file_path,
    get_datetime_with_tz,
    process_files,
)
from .utils_format import convert_in_duration
from .utils_gpx import (
    ActivityGPXException,
    extract_segment_from_gpx_file,
    get_chart_data,
)
from .utils_id import decode_short_id

activities_blueprint = Blueprint('activities', __name__)

ACTIVITIES_PER_PAGE = 5


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
                "id": "kjxavSTUrJvoAh2wvCeGEF",
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
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": "0:17:04"
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "title": null,
                "user": "admin",
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
    :query integer per_page: number of activities per page
                             (default: 5, max: 50)
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
            date_to = datetime.strptime(
                f'{date_to} 23:59:59', '%Y-%m-%d %H:%M:%S'
            )
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
        per_page = (
            int(params.get('per_page'))
            if params.get('per_page')
            else ACTIVITIES_PER_PAGE
        )
        if per_page > 50:
            per_page = 50
        activities = (
            Activity.query.filter(
                Activity.user_id == auth_user_id,
                Activity.sport_id == sport_id if sport_id else True,
                Activity.activity_date >= date_from if date_from else True,
                Activity.activity_date < date_to + timedelta(seconds=1)
                if date_to
                else True,
                Activity.distance >= int(distance_from)
                if distance_from
                else True,
                Activity.distance <= int(distance_to) if distance_to else True,
                Activity.moving >= convert_in_duration(duration_from)
                if duration_from
                else True,
                Activity.moving <= convert_in_duration(duration_to)
                if duration_to
                else True,
                Activity.ave_speed >= float(ave_speed_from)
                if ave_speed_from
                else True,
                Activity.ave_speed <= float(ave_speed_to)
                if ave_speed_to
                else True,
                Activity.max_speed >= float(max_speed_from)
                if max_speed_from
                else True,
                Activity.max_speed <= float(max_speed_to)
                if max_speed_to
                else True,
            )
            .order_by(
                Activity.activity_date.asc()
                if order == 'asc'
                else Activity.activity_date.desc()
            )
            .paginate(page, per_page, False)
            .items
        )
        return {
            'status': 'success',
            'data': {
                'activities': [
                    activity.serialize(params) for activity in activities
                ]
            },
        }
    except Exception as e:
        return handle_error_and_return_response(e)


@activities_blueprint.route(
    '/activities/<string:activity_short_id>', methods=['GET']
)
@authenticate
def get_activity(auth_user_id, activity_short_id):
    """
    Get an activity

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/kjxavSTUrJvoAh2wvCeGEF HTTP/1.1

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
                "id": "kjxavSTUrJvoAh2wvCeGEF",
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
                "user": "admin",
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
    :param string activity_short_id: activity short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 403: You do not have permissions.
    :statuscode 404: activity not found

    """
    activity_uuid = decode_short_id(activity_short_id)
    activity = Activity.query.filter_by(uuid=activity_uuid).first()
    if not activity:
        return DataNotFoundErrorResponse('activities')

    error_response = can_view_activity(auth_user_id, activity.user_id)
    if error_response:
        return error_response

    return {
        'status': 'success',
        'data': {'activities': [activity.serialize()]},
    }


def get_activity_data(
    auth_user_id, activity_short_id, data_type, segment_id=None
):
    """Get data from an activity gpx file"""
    activity_uuid = decode_short_id(activity_short_id)
    activity = Activity.query.filter_by(uuid=activity_uuid).first()
    if not activity:
        return DataNotFoundErrorResponse(
            data_type=data_type,
            message=f'Activity not found (id: {activity_short_id})',
        )

    error_response = can_view_activity(auth_user_id, activity.user_id)
    if error_response:
        return error_response
    if not activity.gpx or activity.gpx == '':
        return NotFoundErrorResponse(
            f'No gpx file for this activity (id: {activity_short_id})'
        )

    try:
        absolute_gpx_filepath = get_absolute_file_path(activity.gpx)
        if data_type == 'chart_data':
            content = get_chart_data(absolute_gpx_filepath, segment_id)
        else:  # data_type == 'gpx'
            with open(absolute_gpx_filepath, encoding='utf-8') as f:
                content = f.read()
                if segment_id is not None:
                    content = extract_segment_from_gpx_file(
                        content, segment_id
                    )
    except ActivityGPXException as e:
        appLog.error(e.message)
        if e.status == 'not found':
            return NotFoundErrorResponse(e.message)
        return InternalServerErrorResponse(e.message)
    except Exception as e:
        return handle_error_and_return_response(e)

    return {
        'status': 'success',
        'message': '',
        'data': ({data_type: content}),
    }


@activities_blueprint.route(
    '/activities/<string:activity_short_id>/gpx', methods=['GET']
)
@authenticate
def get_activity_gpx(auth_user_id, activity_short_id):
    """
    Get gpx file for an activity displayed on map with Leaflet

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/kjxavSTUrJvoAh2wvCeGEF/gpx HTTP/1.1
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
    :param string activity_short_id: activity short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404:
        - activity not found
        - no gpx file for this activity
    :statuscode 500:

    """
    return get_activity_data(auth_user_id, activity_short_id, 'gpx')


@activities_blueprint.route(
    '/activities/<string:activity_short_id>/chart_data', methods=['GET']
)
@authenticate
def get_activity_chart_data(auth_user_id, activity_short_id):
    """
    Get chart data from an activity gpx file, to display it with Recharts

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/kjxavSTUrJvoAh2wvCeGEF/chart HTTP/1.1
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
    :param string activity_short_id: activity short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404:
        - activity not found
        - no gpx file for this activity
    :statuscode 500:

    """
    return get_activity_data(auth_user_id, activity_short_id, 'chart_data')


@activities_blueprint.route(
    '/activities/<string:activity_short_id>/gpx/segment/<int:segment_id>',
    methods=['GET'],
)
@authenticate
def get_segment_gpx(auth_user_id, activity_short_id, segment_id):
    """
    Get gpx file for an activity segment displayed on map with Leaflet

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/kjxavSTUrJvoAh2wvCeGEF/gpx/segment/0 HTTP/1.1
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
    :param string activity_short_id: activity short id
    :param integer segment_id: segment id

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
    return get_activity_data(
        auth_user_id, activity_short_id, 'gpx', segment_id
    )


@activities_blueprint.route(
    '/activities/<string:activity_short_id>/chart_data/segment/'
    '<int:segment_id>',
    methods=['GET'],
)
@authenticate
def get_segment_chart_data(auth_user_id, activity_short_id, segment_id):
    """
    Get chart data from an activity gpx file, to display it with Recharts

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/kjxavSTUrJvoAh2wvCeGEF/chart/segment/0 HTTP/1.1
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
    :param string activity_short_id: activity short id
    :param integer segment_id: segment id

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
    return get_activity_data(
        auth_user_id, activity_short_id, 'chart_data', segment_id
    )


@activities_blueprint.route('/activities/map/<map_id>', methods=['GET'])
def get_map(map_id):
    """
    Get map image for activities with gpx

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/map/fa33f4d996844a5c73ecd1ae24456ab8?1563529507772
        HTTP/1.1

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
            return NotFoundErrorResponse('Map does not exist.')
        absolute_map_filepath = get_absolute_file_path(activity.map)
        return send_file(absolute_map_filepath)
    except Exception as e:
        return handle_error_and_return_response(e)


@activities_blueprint.route(
    '/activities/map_tile/<s>/<z>/<x>/<y>.png', methods=['GET']
)
def get_map_tile(s, z, x, y):
    """
    Get map tile from tile server.

    **Example request**:

    .. sourcecode:: http

      GET /api/activities/map_tile/c/13/4109/2930.png HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: image/png

    :param string s: subdomain
    :param string z: zoom
    :param string x: index of the tile along the map's x axis
    :param string y: index of the tile along the map's y axis

    Status codes are status codes returned by tile server

    """
    url = current_app.config['TILE_SERVER']['URL'].format(s=s, z=z, x=x, y=y)
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    return (
        Response(
            response.content,
            content_type=response.headers['content-type'],
        ),
        response.status_code,
    )


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
                "id": "kjxavSTUrJvoAh2wvCeGEF",
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
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": "0:17:04"
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "title": null,
                "user": "admin",
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
    :statuscode 413: Error during picture update: file size exceeds 1.0MB.
    :statuscode 500:

    """
    error_response = verify_extension_and_size('activity', request)
    if error_response:
        return error_response

    activity_data = json.loads(request.form['data'])
    if not activity_data or activity_data.get('sport_id') is None:
        return InvalidPayloadErrorResponse()

    activity_file = request.files['file']
    upload_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'], 'activities', str(auth_user_id)
    )
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
                    'activities': [
                        new_activity.serialize()
                        for new_activity in new_activities
                    ]
                },
            }
        else:
            return DataInvalidPayloadErrorResponse('activities', 'fail')
    except ActivityException as e:
        db.session.rollback()
        if e.e:
            appLog.error(e.e)
        if e.status == 'error':
            return InternalServerErrorResponse(e.message)
        return InvalidPayloadErrorResponse(e.message)

    shutil.rmtree(folders['extract_dir'], ignore_errors=True)
    shutil.rmtree(folders['tmp_dir'], ignore_errors=True)
    return response_object, 201


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
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": "0:17:04"
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "title": null,
                "user": "admin",
                "uuid": "kjxavSTUrJvoAh2wvCeGEF"
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
    if (
        not activity_data
        or activity_data.get('sport_id') is None
        or activity_data.get('duration') is None
        or activity_data.get('distance') is None
        or activity_data.get('activity_date') is None
    ):
        return InvalidPayloadErrorResponse()

    try:
        user = User.query.filter_by(id=auth_user_id).first()
        new_activity = create_activity(user, activity_data)
        db.session.add(new_activity)
        db.session.commit()

        return (
            {
                'status': 'created',
                'data': {'activities': [new_activity.serialize()]},
            },
            201,
        )

    except (exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(
            error=e,
            message='Error during activity save.',
            status='fail',
            db=db,
        )


@activities_blueprint.route(
    '/activities/<string:activity_short_id>', methods=['PATCH']
)
@authenticate
def update_activity(auth_user_id, activity_short_id):
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
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": "0:17:04"
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  },
                  {
                    "activity_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "activity_id": "kjxavSTUrJvoAh2wvCeGEF",
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "title": null,
                "user": "admin",
                "uuid": "kjxavSTUrJvoAh2wvCeGEF"
                "weather_end": null,
                "weather_start": null,
                "with_gpx": false
              }
            ]
          },
          "status": "success"
        }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
    :param string activity_short_id: activity short id

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
        return InvalidPayloadErrorResponse()

    try:
        activity_uuid = decode_short_id(activity_short_id)
        activity = Activity.query.filter_by(uuid=activity_uuid).first()
        if not activity:
            return DataNotFoundErrorResponse('activities')

        response_object = can_view_activity(auth_user_id, activity.user_id)
        if response_object:
            return response_object

        activity = edit_activity(activity, activity_data, auth_user_id)
        db.session.commit()
        return {
            'status': 'success',
            'data': {'activities': [activity.serialize()]},
        }

    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e)


@activities_blueprint.route(
    '/activities/<string:activity_short_id>', methods=['DELETE']
)
@authenticate
def delete_activity(auth_user_id, activity_short_id):
    """
    Delete an activity

    **Example request**:

    .. sourcecode:: http

      DELETE /api/activities/kjxavSTUrJvoAh2wvCeGEF HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
    :param string activity_short_id: activity short id

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
        activity_uuid = decode_short_id(activity_short_id)
        activity = Activity.query.filter_by(uuid=activity_uuid).first()
        if not activity:
            return DataNotFoundErrorResponse('activities')
        error_response = can_view_activity(auth_user_id, activity.user_id)
        if error_response:
            return error_response

        db.session.delete(activity)
        db.session.commit()
        return {'status': 'no content'}, 204
    except (
        exc.IntegrityError,
        exc.OperationalError,
        ValueError,
        OSError,
    ) as e:
        return handle_error_and_return_response(e, db=db)
