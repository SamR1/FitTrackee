import json
import os
import shutil
from datetime import timedelta
from typing import Dict, List, Optional, Tuple, Union

import requests
from flask import (
    Blueprint,
    Response,
    current_app,
    request,
    send_from_directory,
)
from sqlalchemy import asc, desc, exc
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, RequestEntityTooLarge
from werkzeug.utils import secure_filename

from fittrackee import appLog, db, limiter
from fittrackee.equipments.exceptions import (
    InvalidEquipmentException,
    InvalidEquipmentsException,
)
from fittrackee.equipments.models import Equipment, WorkoutEquipment
from fittrackee.equipments.utils import (
    SPORT_EQUIPMENT_TYPES,
    handle_equipments,
)
from fittrackee.oauth2.server import require_auth
from fittrackee.reports.models import ReportActionAppeal
from fittrackee.responses import (
    DataInvalidPayloadErrorResponse,
    DataNotFoundErrorResponse,
    EquipmentInvalidPayloadErrorResponse,
    HttpResponse,
    InternalServerErrorResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    PayloadTooLargeErrorResponse,
    get_error_response_if_file_is_invalid,
    handle_error_and_return_response,
)
from fittrackee.users.models import User, UserSportPreference
from fittrackee.utils import decode_short_id
from fittrackee.visibility_levels import can_view

from .decorators import check_workout
from .models import Sport, Workout, WorkoutLike
from .utils.convert import convert_in_duration
from .utils.gpx import (
    WorkoutGPXException,
    extract_segment_from_gpx_file,
    get_chart_data,
)
from .utils.workouts import (
    WorkoutException,
    create_workout,
    edit_workout,
    get_absolute_file_path,
    get_datetime_from_request_args,
    process_files,
)

workouts_blueprint = Blueprint("workouts", __name__)

DEFAULT_WORKOUTS_PER_PAGE = 5
MAX_WORKOUTS_PER_PAGE = 100
MAX_WORKOUTS_TO_SEND = 5
DEFAULT_WORKOUT_LIKES_PER_PAGE = 10


@workouts_blueprint.route("/workouts", methods=["GET"])
@require_auth(scopes=["workouts:read"])
def get_workouts(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Get workouts for the authenticated user.

    **Scope**: ``workouts:read``

    **Example requests**:

    - without parameters:

    .. sourcecode:: http

      GET /api/workouts/ HTTP/1.1

    - with some query parameters:

    .. sourcecode:: http

      GET /api/workouts?from=2019-07-02&to=2019-07-31&sport_id=1  HTTP/1.1

    **Example responses**:

    - returning at least one workout:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "workouts": [
              {
                "analysis_visibility": "private",
                "ascent": null,
                "ave_speed": 10.0,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": null,
                "description": null,
                "distance": 10.0,
                "duration": "0:17:04",
                "equipments": [],
                "id": "kjxavSTUrJvoAh2wvCeGEF",
                "liked": false,
                "likes_count": 0,
                "map": null,
                "map_visibility": "private",
                "max_alt": null,
                "max_speed": 10.0,
                "min_alt": null,
                "modification_date": null,
                "moving": "0:17:04",
                "next_workout": 3,
                "notes": null,
                "pauses": null,
                "previous_workout": null,
                "records": [
                  {
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 13,
                    "record_type": "HA",
                    "sport_id": 1,
                    "user": "Sam",
                    "value": 43.97,
                    "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
                    "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
                  },
                  {
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": "0:17:04",
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "suspended": false,
                "suspended_at": null,
                "title": null,
                "user": {
                  "created_at": "Sun, 31 Dec 2017 09:00:00 GMT",
                  "followers": 0,
                  "following": 0,
                  "nb_workouts": 1,
                  "picture": false,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                },
                "weather_end": null,
                "weather_start": null,
                "with_analysis": false,
                "with_gpx": false,
                "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                "workout_visibility": "private"
              }
            ]
          },
          "status": "success"
        }

    - returning no workouts

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
            "data": {
                "workouts": []
            },
            "status": "success"
        }

    :query integer page: page if using pagination (default: 1)
    :query integer per_page: number of workouts per page
                             (default: 5, max: 100)
    :query integer sport_id: sport id
    :query string title: any part (or all) of the workout title;
                         title matching is case-insensitive
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
    :query string order: sorting order: ``asc``, ``desc`` (default: ``desc``)
    :query string order_by: sorting criteria: ``ave_speed``, ``distance``,
                            ``duration``, ``workout_date`` (default:
                            ``workout_date``)
    :query string equipment_id: equipment id (if ``none``, only workouts
                            without equipments will be returned)
    :query string notes: any part (or all) of the workout notes,
                         notes matching is case-insensitive
    :query string description: any part of the workout description;
                         description matching is case-insensitive
    :query string return_equipments: return workouts with equipment
                         (by default, equipment is not returned).
                         **Note**: It's not a filter.
                         **Warning**: Needed for 3rd-party applications
                         updating equipments.


    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    try:
        params = request.args.copy()
        page = int(params.get("page", 1))
        date_from, date_to = get_datetime_from_request_args(params, auth_user)
        distance_from = params.get("distance_from")
        distance_to = params.get("distance_to")
        duration_from = params.get("duration_from")
        duration_to = params.get("duration_to")
        ave_speed_from = params.get("ave_speed_from")
        ave_speed_to = params.get("ave_speed_to")
        max_speed_from = params.get("max_speed_from")
        max_speed_to = params.get("max_speed_to")
        order_by = params.get("order_by", "workout_date")
        workout_column = getattr(
            Workout, "moving" if order_by == "duration" else order_by
        )
        order = params.get("order", "desc")
        sport_id = params.get("sport_id")
        title = params.get("title")
        notes = params.get("notes")
        description = params.get("description")
        if "equipment_id" in params:
            if params["equipment_id"] == "none":
                equipment_id: Union[str, int, None] = "none"
            else:
                equipment_uuid = decode_short_id(params["equipment_id"])
                equipment = Equipment.query.filter_by(
                    uuid=equipment_uuid
                ).first()
                equipment_id = equipment.id if equipment else 0
        else:
            equipment_id = None
        per_page = int(params.get("per_page", DEFAULT_WORKOUTS_PER_PAGE))
        if per_page > MAX_WORKOUTS_PER_PAGE:
            per_page = MAX_WORKOUTS_PER_PAGE

        filters = [
            Workout.user_id == auth_user.id,
            Workout.suspended_at == None,  # noqa
        ]
        if sport_id:
            filters.append(Workout.sport_id == sport_id)
        if title:
            filters.append(Workout.title.ilike(f"%{title}%"))
        if notes:
            filters.append(Workout.notes.ilike(f"%{notes}%"))
        if description:
            filters.append(Workout.description.ilike(f"%{description}%"))
        if date_from:
            filters.append(Workout.workout_date >= date_from)
        if date_to:
            filters.append(
                Workout.workout_date < date_to + timedelta(seconds=1)
            )
        if distance_from:
            filters.append(Workout.distance >= float(distance_from))
        if distance_to:
            filters.append(Workout.distance <= float(distance_to))
        if duration_from:
            filters.append(
                Workout.moving >= convert_in_duration(duration_from)
            )
        if duration_to:
            filters.append(Workout.moving <= convert_in_duration(duration_to))
        if ave_speed_from:
            filters.append(Workout.ave_speed >= float(ave_speed_from))
        if ave_speed_to:
            filters.append(Workout.ave_speed <= float(ave_speed_to))
        if max_speed_from:
            filters.append(Workout.max_speed >= float(max_speed_from))
        if max_speed_to:
            filters.append(Workout.max_speed <= float(max_speed_to))
        if equipment_id == "none":
            filters.append(WorkoutEquipment.c.equipment_id == None)  # noqa
        if equipment_id == "none":
            filters.append(WorkoutEquipment.c.equipment_id == None)  # noqa
        elif equipment_id is not None:
            filters.append(WorkoutEquipment.c.equipment_id == equipment_id)

        workouts_pagination = (
            Workout.query.outerjoin(WorkoutEquipment)
            .filter(*filters)
            .order_by(
                (
                    asc(workout_column)
                    if order == "asc"
                    else desc(workout_column)
                ),
            )
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        workouts = workouts_pagination.items
        with_equipments = (
            params.get("return_equipments", "false").lower() == "true"
        )
        return {
            "status": "success",
            "data": {
                "workouts": [
                    workout.serialize(
                        user=auth_user,
                        params=params,
                        with_equipments=with_equipments,
                    )
                    for workout in workouts
                ]
            },
            "pagination": {
                "has_next": workouts_pagination.has_next,
                "has_prev": workouts_pagination.has_prev,
                "page": workouts_pagination.page,
                "pages": workouts_pagination.pages,
                "total": workouts_pagination.total,
            },
        }
    except Exception as e:
        return handle_error_and_return_response(e)


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>", methods=["GET"]
)
@require_auth(scopes=["workouts:read"], optional_auth_user=True)
@check_workout(only_owner=False)
def get_workout(
    auth_user: Optional[User], workout: Workout, workout_short_id: str
) -> Union[Dict, HttpResponse]:
    """
    Get a workout.

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/kjxavSTUrJvoAh2wvCeGEF HTTP/1.1

    **Example responses**:

    - success:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "workouts": [
              {
                "analysis_visibility": "private",
                "ascent": null,
                "ave_speed": 16,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 18:57:14 GMT",
                "descent": null,
                "description": null,
                "distance": 12,
                "duration": "0:45:00",
                "equipments": [],
                "id": "kjxavSTUrJvoAh2wvCeGEF",
                "liked": false,
                "likes_count": 0,
                "map": null,
                "map_visibility": "private",
                "max_alt": null,
                "max_speed": 16,
                "min_alt": null,
                "modification_date": "Sun, 14 Jul 2019 18:57:22 GMT",
                "moving": "0:45:00",
                "next_workout": 4,
                "notes": "workout without gpx",
                "pauses": null,
                "previous_workout": 3,
                "records": [],
                "segments": [],
                "sport_id": 1,
                "suspended": false,
                "suspended_at": null,
                "title": "biking on sunday morning",
                "user": {
                  "created_at": "Sun, 31 Dec 2017 09:00:00 GMT",
                  "followers": 0,
                  "following": 0,
                  "nb_workouts": 1,
                  "picture": false,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                },
                "weather_end": null,
                "weather_start": null,
                "with_analysis": false,
                "with_gpx": false,
                "workout_date": "Sun, 07 Jul 2019 07:00:00 GMT",
                "workout_visibility": "private"
              }
            ]
          },
          "status": "success"
        }

    - workout not found:

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

        {
          "data": {
            "workouts": []
          },
          "status": "not found"
        }

    :param string workout_short_id: workout short id

    :reqheader Authorization: OAuth 2.0 Bearer Token for workout with
               ``private`` or ``followers_only`` visibility

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``workout not found``

    """
    return {
        "status": "success",
        "data": {"workouts": [workout.serialize(user=auth_user, light=False)]},
    }


def get_workout_data(
    auth_user: Optional[User],
    workout_short_id: str,
    data_type: str,
    segment_id: Optional[int] = None,
) -> Union[Dict, HttpResponse]:
    """Get data from workout gpx file"""
    not_found_response = DataNotFoundErrorResponse(
        data_type=data_type,
        message=f"workout not found (id: {workout_short_id})",
    )
    workout_uuid = decode_short_id(workout_short_id)
    workout = Workout.query.filter_by(uuid=workout_uuid).first()
    if not workout:
        return not_found_response

    if not can_view(
        workout,
        "calculated_analysis_visibility"
        if data_type == "chart_data"
        else "calculated_map_visibility",
        auth_user,
    ):
        return not_found_response

    if not workout.gpx or workout.gpx == "":
        return NotFoundErrorResponse(
            f"no gpx file for this workout (id: {workout_short_id})"
        )

    try:
        absolute_gpx_filepath = get_absolute_file_path(workout.gpx)
        chart_data_content: Optional[List] = []
        if data_type == "chart_data":
            chart_data_content = get_chart_data(
                absolute_gpx_filepath, segment_id
            )
        else:  # data_type == 'gpx'
            with open(absolute_gpx_filepath, encoding="utf-8") as f:
                gpx_content = f.read()
                if segment_id is not None:
                    gpx_segment_content = extract_segment_from_gpx_file(
                        gpx_content, segment_id
                    )
    except WorkoutGPXException as e:
        appLog.error(e.message)
        if e.status == "not found":
            return NotFoundErrorResponse(e.message)
        return InternalServerErrorResponse(e.message)
    except Exception as e:
        return handle_error_and_return_response(e)

    return {
        "status": "success",
        "message": "",
        "data": (
            {
                data_type: (
                    chart_data_content
                    if data_type == "chart_data"
                    else (
                        gpx_content
                        if segment_id is None
                        else gpx_segment_content
                    )
                )
            }
        ),
    }


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/gpx", methods=["GET"]
)
@require_auth(scopes=["workouts:read"], optional_auth_user=True)
def get_workout_gpx(
    auth_user: Optional[User], workout_short_id: str
) -> Union[Dict, HttpResponse]:
    """
    Get gpx file for a workout displayed on map with Leaflet.

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/kjxavSTUrJvoAh2wvCeGEF/gpx HTTP/1.1
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

    :param string workout_short_id: workout short id

    :reqheader Authorization: OAuth 2.0 Bearer Token for workout with
               ``private`` or ``followers_only`` map visibility

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``workout not found``
        - ``no gpx file for this workout``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    return get_workout_data(auth_user, workout_short_id, "gpx")


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/chart_data", methods=["GET"]
)
@require_auth(scopes=["workouts:read"], optional_auth_user=True)
def get_workout_chart_data(
    auth_user: Optional[User], workout_short_id: str
) -> Union[Dict, HttpResponse]:
    """
    Get chart data from a workout gpx file, to display it with Chart.js.

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/kjxavSTUrJvoAh2wvCeGEF/chart HTTP/1.1
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

    :param string workout_short_id: workout short id

    :reqheader Authorization: OAuth 2.0 Bearer Token for workout with
               ``private`` or ``followers_only`` map visibility

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``workout not found``
        - ``no gpx file for this workout``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    return get_workout_data(auth_user, workout_short_id, "chart_data")


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/gpx/segment/<int:segment_id>",
    methods=["GET"],
)
@require_auth(scopes=["workouts:read"], optional_auth_user=True)
def get_segment_gpx(
    auth_user: Optional[User], workout_short_id: str, segment_id: int
) -> Union[Dict, HttpResponse]:
    """
    Get gpx file for a workout segment displayed on map with Leaflet.

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/kjxavSTUrJvoAh2wvCeGEF/gpx/segment/1 HTTP/1.1
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

    :param string workout_short_id: workout short id
    :param integer segment_id: segment id

    :reqheader Authorization: OAuth 2.0 Bearer Token for workout with
               ``private`` or ``followers_only`` map visibility

    :statuscode 200: ``success``
    :statuscode 400: ``no gpx file for this workout``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``workout not found``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    return get_workout_data(auth_user, workout_short_id, "gpx", segment_id)


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/chart_data/segment/<int:segment_id>",
    methods=["GET"],
)
@require_auth(scopes=["workouts:read"], optional_auth_user=True)
def get_segment_chart_data(
    auth_user: Optional[User], workout_short_id: str, segment_id: int
) -> Union[Dict, HttpResponse]:
    """
    Get chart data from a workout gpx file, to display it with Chart.js.

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/kjxavSTUrJvoAh2wvCeGEF/chart/segment/1 HTTP/1.1
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

    :param string workout_short_id: workout short id
    :param integer segment_id: segment id

    :reqheader Authorization: OAuth 2.0 Bearer Token for workout with
               ``private`` or ``followers_only`` map visibility

    :statuscode 200: ``success``
    :statuscode 400: ``no gpx file for this workout``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``workout not found``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    return get_workout_data(
        auth_user, workout_short_id, "chart_data", segment_id
    )


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/gpx/download", methods=["GET"]
)
@require_auth(scopes=["workouts:read"])
def download_workout_gpx(
    auth_user: User, workout_short_id: str
) -> Union[HttpResponse, Response]:
    """
    Download gpx file.

    **Scope**: ``workouts:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/kjxavSTUrJvoAh2wvCeGEF/gpx/download HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/gpx+xml

    :param string workout_short_id: workout short id

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``workout not found``
        - ``no gpx file for workout``
    """
    workout_uuid = decode_short_id(workout_short_id)
    workout = Workout.query.filter_by(
        uuid=workout_uuid, user_id=auth_user.id
    ).first()
    if not workout:
        return DataNotFoundErrorResponse(
            data_type="workout",
            message=f"workout not found (id: {workout_short_id})",
        )

    if workout.gpx is None:
        return DataNotFoundErrorResponse(
            data_type="gpx",
            message=f"no gpx file for workout (id: {workout_short_id})",
        )

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        workout.gpx,
        mimetype="application/gpx+xml",
        as_attachment=True,
    )


@workouts_blueprint.route("/workouts/map/<map_id>", methods=["GET"])
@limiter.exempt
def get_map(map_id: int) -> Union[HttpResponse, Response]:
    """
    Get map image for workouts with gpx.

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/map/fa33f4d996844a5c73ecd1ae24456ab8?1563529507772
        HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: image/png

    :param string map_id: workout map id

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``map does not exist``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    try:
        workout = Workout.query.filter_by(map_id=map_id).first()
        if not workout:
            return NotFoundErrorResponse("Map does not exist.")
        return send_from_directory(
            current_app.config["UPLOAD_FOLDER"],
            workout.map,
        )
    except NotFound:
        return NotFoundErrorResponse("Map file does not exist.")
    except Exception as e:
        return handle_error_and_return_response(e)


@workouts_blueprint.route(
    "/workouts/map_tile/<s>/<z>/<x>/<y>.png", methods=["GET"]
)
@limiter.exempt
def get_map_tile(s: str, z: str, x: str, y: str) -> Tuple[Response, int]:
    """
    Get map tile from tile server.

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/map_tile/c/13/4109/2930.png HTTP/1.1

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
    url = current_app.config["TILE_SERVER"]["URL"].format(
        s=secure_filename(s),
        z=secure_filename(z),
        x=secure_filename(x),
        y=secure_filename(y),
    )
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:88.0)"}
    response = requests.get(url, headers=headers, timeout=30)
    return (
        Response(
            response.content,
            content_type=response.headers["content-type"],
        ),
        response.status_code,
    )


@workouts_blueprint.route("/workouts", methods=["POST"])
@require_auth(scopes=["workouts:write"])
def post_workout(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Post a workout with a gpx file.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/workouts/ HTTP/1.1
      Content-Type: multipart/form-data

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

        {
          "data": {
            "workouts": [
              {
                "analysis_visibility": "private",
                "ascent": 435.621,
                "ave_speed": 13.14,
                "bounds": [
                  43.93706,
                  4.517587,
                  43.981933,
                  4.560627
                ],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": 427.499,
                "description": null,
                "distance": 23.478,
                "duration": "2:08:35",
                "equipments": [],
                "id": "PsjeeXbJZ2JJNQcTCPxVvF",
                "liked": false,
                "likes_count": 0,
                "map": "ac075ec36dc25dcc20c270d2005f0398",
                "map_visibility": "private",
                "max_alt": 158.41,
                "max_speed": 25.59,
                "min_alt": 55.03,
                "modification_date": null,
                "moving": "1:47:11",
                "next_workout": "Kd5wyhwLtVozw6o3AU5M4J",
                "notes": "",
                "pauses": "0:20:32",
                "previous_workout": "HgzYFXgvWKCEpdq3vYk67q",
                "records": [
                  {
                    "id": 6,
                    "record_type": "AS",
                    "sport_id": 4,
                    "user": "Sam",
                    "value": 13.14,
                    "workout_date": "Tue, 26 Apr 2016 14:42:30 GMT",
                    "workout_id": "PsjeeXbJZ2JJNQcTCPxVvF"
                  },
                  {
                    "id": 7,
                    "record_type": "FD",
                    "sport_id": 4,
                    "user": "Sam",
                    "value": 23.478,
                    "workout_date": "Tue, 26 Apr 2016 14:42:30 GMT",
                    "workout_id": "PsjeeXbJZ2JJNQcTCPxVvF"
                  },
                  {
                    "id": 9,
                    "record_type": "LD",
                    "sport_id": 4,
                    "user": "Sam",
                    "value": "1:47:11",
                    "workout_date": "Tue, 26 Apr 2016 14:42:30 GMT",
                    "workout_id": "PsjeeXbJZ2JJNQcTCPxVvF"
                  },
                  {
                    "id": 10,
                    "record_type": "MS",
                    "sport_id": 4,
                    "user": "Sam",
                    "value": 25.59,
                    "workout_date": "Tue, 26 Apr 2016 14:42:30 GMT",
                    "workout_id": "PsjeeXbJZ2JJNQcTCPxVvF"
                  },
                  {
                    "id": 8,
                    "record_type": "HA",
                    "sport_id": 4,
                    "user": "Sam",
                    "value": 435.621,
                    "workout_date": "Tue, 26 Apr 2016 14:42:30 GMT",
                    "workout_id": "PsjeeXbJZ2JJNQcTCPxVvF"
                  }
                ],
                "segments": [
                  {
                    "ascent": 435.621,
                    "ave_speed": 13.14,
                    "descent": 427.499,
                    "distance": 23.478,
                    "duration": "2:08:35",
                    "max_alt": 158.41,
                    "max_speed": 25.59,
                    "min_alt": 55.03,
                    "moving": "1:47:11",
                    "pauses": "0:20:32",
                    "segment_id": 0,
                    "workout_id": "PsjeeXbJZ2JJNQcTCPxVvF"
                  }
                ],
                "sport_id": 4,
                "suspended": false,
                "suspended_at": null,
                "title": "VTT dans le Gard",
                "user": {
                  "created_at": "Sun, 31 Dec 2017 09:00:00 GMT",
                  "followers": 0,
                  "following": 0,
                  "nb_workouts": 3,
                  "picture": false,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                },
                "weather_end": null,
                "weather_start": null,
                "with_analysis": false,
                "with_gpx": true,
                "workout_date": "Tue, 26 Apr 2016 14:42:30 GMT",
                "workout_visibility": "private"
              }
            ]
          },
          "status": "success"
        }

    :form file: gpx file (allowed extensions: .gpx, .zip)
    :form data: sport id, equipment id, description, title, notes, visibility
       for workout, analysis and map
       for example:
       ``{"sport_id": 1, "notes": "", "title": "", "description": "",
       "analysis_visibility": "private", "map_visibility": "private",
       "workout_visibility": "private", "equipment_ids": []}``.
       Double quotes in notes, description and title must be escaped.

       The maximum length is 500 characters for notes, 10000 characters for
       description and 255 for title. Otherwise, they will be truncated.
       When description and title are provided, they replace the description
       and title from gpx file.

       For `equipment_ids`, the id of the equipment to associate with
       this workout.
       **Note**: for now only one equipment can be associated.
       If not provided and default equipment exists for sport,
       default equipment will be associated.

       Notes, description, title, equipment ids and visibility
       for workout, analysis and map are not mandatory.
       Visibility levels default to user preferences.

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: workout created
    :statuscode 400:
        - ``invalid payload``
        - ``no file part``
        - ``no selected file``
        - ``file extension not allowed``
        - ``equipment_ids must be an array of strings``
        - ``only one equipment can be added``
        - ``equipment with id <equipment_id> does not exist``
        - ``invalid equipment id <equipment_id> for sport``
        - ``equipment with id <equipment_id> is inactive``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 413: ``error during picture update: file size exceeds 1.0MB``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    try:
        error_response = get_error_response_if_file_is_invalid(
            "workout", request
        )
    except RequestEntityTooLarge as e:
        appLog.error(e)
        return PayloadTooLargeErrorResponse(
            file_type="workout",
            file_size=request.content_length,
            max_size=current_app.config["MAX_CONTENT_LENGTH"],
        )
    if error_response:
        return error_response

    try:
        workout_data = json.loads(request.form["data"], strict=False)
    except json.decoder.JSONDecodeError:
        return InvalidPayloadErrorResponse()

    if not workout_data or workout_data.get("sport_id") is None:
        return InvalidPayloadErrorResponse()

    if "equipment_ids" in workout_data:
        try:
            equipments_list = handle_equipments(
                workout_data["equipment_ids"],
                auth_user,
                workout_data["sport_id"],
            )
        except InvalidEquipmentsException as e:
            return InvalidPayloadErrorResponse(str(e))
        except InvalidEquipmentException as e:
            return EquipmentInvalidPayloadErrorResponse(
                equipment_id=e.equipment_id, message=e.message, status=e.status
            )
        workout_data["equipments_list"] = equipments_list

    workout_file = request.files["file"]
    upload_dir = os.path.join(
        current_app.config["UPLOAD_FOLDER"], "workouts", str(auth_user.id)
    )
    folders = {
        "extract_dir": os.path.join(upload_dir, "extract"),
        "tmp_dir": os.path.join(upload_dir, "tmp"),
    }

    try:
        new_workouts = process_files(
            auth_user, workout_data, workout_file, folders
        )
        if len(new_workouts) > 0:
            response_object = {
                "status": "created",
                "data": {
                    "workouts": [
                        new_workout.serialize(user=auth_user, light=False)
                        for new_workout in new_workouts
                    ]
                },
            }
        else:
            return DataInvalidPayloadErrorResponse("workouts", "fail")
    except WorkoutException as e:
        db.session.rollback()
        if e.e:
            appLog.error(e.e)
        if e.status == "error":
            return InternalServerErrorResponse(e.message)
        return InvalidPayloadErrorResponse(e.message, e.status)

    shutil.rmtree(folders["extract_dir"], ignore_errors=True)
    shutil.rmtree(folders["tmp_dir"], ignore_errors=True)
    return response_object, 201


@workouts_blueprint.route("/workouts/no_gpx", methods=["POST"])
@require_auth(scopes=["workouts:write"])
def post_workout_no_gpx(
    auth_user: User,
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Post a workout without gpx file.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/workouts/no_gpx HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

       {
          "data": {
            "workouts": [
              {
                "analysis_visibility": "private",
                "ascent": null,
                "ave_speed": 10.0,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": null,
                "description": null,
                "distance": 10.0,
                "duration": "0:17:04",
                "id": "Kd5wyhwLtVozw6o3AU5M4J",
                "liked": false,
                "likes_count": 0,
                "equipments": [],
                "map": null,
                "map_visibility": "private",
                "max_alt": null,
                "max_speed": 10.0,
                "min_alt": null,
                "modification_date": null,
                "moving": "0:17:04",
                "next_workout": 3,
                "notes": null,
                "pauses": null,
                "previous_workout": null,
                "records": [
                  {
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": "0:17:04",
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "suspended": false,
                "suspended_at": null,
                "title": null,
                "user": {
                  "created_at": "Sun, 31 Dec 2017 09:00:00 GMT",
                  "followers": 0,
                  "following": 0,
                  "nb_workouts": 1,
                  "picture": false,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                },
                "uuid": "kjxavSTUrJvoAh2wvCeGEF"
                "weather_end": null,
                "weather_start": null,
                "with_analysis": false,
                "with_gpx": false,
                "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                "workout_visibility": "private"
              }
            ]
          },
          "status": "success"
        }

    :<json string analysis_visibility: analysis visibility
        (``private``, ``followers_only`` or ``public``). Not mandatory,
        defaults to user preferences.
    :<json float ascent: workout ascent (not mandatory,
           must be provided with descent)
    :<json float descent: workout descent (not mandatory,
           must be provided with ascent)
    :<json string description: workout description (not mandatory,
           max length: 10000 characters, otherwise it will be truncated)
    :<json float distance: workout distance in km
    :<json integer duration: workout duration in seconds
    :<json array of strings equipment_ids:
        the id of the equipment to associate with this workout.
        **Note**: for now only one equipment can be associated.
        If not provided and default equipment exists for sport,
        default equipment will be associated.
    :<json string map_visibility: map visibility
        (``private``, ``followers_only`` or ``public``). Not mandatory,
        defaults to user preferences.
    :<json string notes: notes (not mandatory, max length: 500
        characters, otherwise they will be truncated)
    :<json integer sport_id: workout sport id
    :<json string title: workout title (not mandatory, max length: 255
        characters, otherwise it will be truncated)
    :<json string workout_date: workout date, in user timezone
        (format: ``%Y-%m-%d %H:%M``)
    :<json string workout_visibility: workout visibility (``private``,
        ``followers_only`` or ``public``). Not mandatory,
        defaults to user preferences.

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: workout created
    :statuscode 400:
        - ``invalid payload``
        - ``equipment_ids must be an array of strings``
        - ``only one equipment can be added``
        - ``equipment with id <equipment_id> does not exist``
        - ``invalid equipment id <equipment_id> for sport``
        - ``equipment with id <equipment_id> is inactive``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    workout_data = request.get_json()
    if (
        not workout_data
        or not workout_data.get("sport_id")
        or not workout_data.get("duration")
        or not workout_data.get("distance")
        or not workout_data.get("workout_date")
    ):
        return InvalidPayloadErrorResponse()

    ascent = workout_data.get("ascent")
    descent = workout_data.get("descent")
    try:
        if (
            (ascent is None and descent is not None)
            or (ascent is not None and descent is None)
            or (
                (ascent is not None and descent is not None)
                and (float(ascent) < 0 or float(descent) < 0)
            )
        ):
            return InvalidPayloadErrorResponse()
    except ValueError:
        return InvalidPayloadErrorResponse()

    # get default equipment if not equipment_ids provided and
    # sport preferences exists
    if "equipment_ids" not in workout_data:
        sport_preferences = UserSportPreference.query.filter_by(
            user_id=auth_user.id, sport_id=workout_data["sport_id"]
        ).first()
        if sport_preferences:
            workout_data["equipments_list"] = [
                equipment
                for equipment in sport_preferences.default_equipments.all()
                if equipment.is_active is True
            ]
    else:
        try:
            equipments_list = handle_equipments(
                workout_data.get("equipment_ids"),
                auth_user,
                workout_data["sport_id"],
            )
            workout_data["equipments_list"] = equipments_list
        except InvalidEquipmentsException as e:
            return InvalidPayloadErrorResponse(str(e))
        except InvalidEquipmentException as e:
            return EquipmentInvalidPayloadErrorResponse(
                equipment_id=e.equipment_id, message=e.message, status=e.status
            )

    try:
        new_workout = create_workout(auth_user, workout_data)
        db.session.add(new_workout)
        db.session.commit()

        return (
            {
                "status": "created",
                "data": {
                    "workouts": [
                        new_workout.serialize(user=auth_user, light=False)
                    ]
                },
            },
            201,
        )

    except (exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(
            error=e,
            message="Error during workout save.",
            status="fail",
            db=db,
        )


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>", methods=["PATCH"]
)
@require_auth(scopes=["workouts:write"])
@check_workout()
def update_workout(
    auth_user: User, workout: Workout, workout_short_id: str
) -> Union[Dict, HttpResponse]:
    """
    Update a workout.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      PATCH /api/workouts/2oRDfncv6vpRkfp3yrCYHt HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

       {
          "data": {
            "workouts": [
              {
                "analysis_visibility": "private",
                "ascent": null,
                "ave_speed": 10.0,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": null,
                "description": null,
                "distance": 10.0,
                "duration": "0:17:04",
                "equipments": [],
                "id": "2oRDfncv6vpRkfp3yrCYHt",
                "liked": false,
                "likes_count": 0,
                "map": null,
                "map_visibility": "private",
                "max_alt": null,
                "max_speed": 10.0,
                "min_alt": null,
                "modification_date": null,
                "moving": "0:17:04",
                "next_workout": 3,
                "notes": null,
                "pauses": null,
                "previous_workout": null,
                "records": [
                  {
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": "0:17:04",
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF",
                  },
                  {
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF",
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "suspended": false,
                "suspended_at": null,
                "title": null,
                "user": {
                  "created_at": "Sun, 31 Dec 2017 09:00:00 GMT",
                  "followers": 0,
                  "following": 0,
                  "nb_workouts": 1,
                  "picture": false,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                },
                "uuid": "kjxavSTUrJvoAh2wvCeGEF"
                "weather_end": null,
                "weather_start": null,
                "with_analysis": false,
                "with_gpx": false,
                "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                "workout_visibility": "private"
              }
            ]
          },
          "status": "success"
        }

    :param string workout_short_id: workout short id

    :<json string analysis_visibility: analysis visibility
        (``private``, ``followers_only`` or ``public``)
    :<json float ascent: workout ascent
        (only for workout without gpx, must be provided with descent)
    :<json float descent: workout descent
        (only for workout without gpx, must be provided with ascent)
    :<json string description: workout description (max length: 10000
        characters, otherwise it will be truncated)
    :<json float distance: workout distance in km
        (only for workout without gpx)
    :<json integer duration: workout duration in seconds
        (only for workout without gpx)
    :<json array of strings equipment_ids:
        the id of the equipment to associate with this workout (any existing
        equipment for this workout will be replaced).
        **Note**: for now only one equipment can be associated.
        If an empty array, equipment for this workout will be removed.
    :<json string map_visibility: map visibility
        (``private``, ``followers_only`` or ``public``)
    :<json string notes: notes (max length: 500 characters, otherwise they
        will be truncated)
    :<json integer sport_id: workout sport id
    :<json string title: workout title (max length: 255 characters, otherwise
        it will be truncated)
    :<json string workout_date: workout date in user timezone
        (format: ``%Y-%m-%d %H:%M``)
        (only for workout without gpx)
    :<json string workout_visibility: workout visibility (``private``,
        ``followers_only`` or ``public``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: workout updated
    :statuscode 400:
        - ``invalid payload``
        - ``equipment_ids must be an array of strings``
        - ``only one equipment can be added``
        - ``equipment with id <equipment_id> does not exist``
        - ``invalid equipment id <equipment_id> for sport``
        - ``equipment with id <equipment_id> is inactive``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``workout not found``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    workout_data = request.get_json()
    if not workout_data:
        return InvalidPayloadErrorResponse()

    try:
        if not workout.gpx:
            try:
                # for workout without gpx file, both elevation values must be
                # provided.
                if (
                    (
                        "ascent" in workout_data
                        and "descent" not in workout_data
                    )
                    or (
                        "ascent" not in workout_data
                        and "descent" in workout_data
                    )
                ) or (
                    not (
                        workout_data.get("ascent") is None
                        and workout_data.get("descent") is None
                    )
                    and (
                        float(workout_data.get("ascent")) < 0
                        or float(workout_data.get("descent")) < 0
                    )
                ):
                    return InvalidPayloadErrorResponse()
            except (TypeError, ValueError):
                return InvalidPayloadErrorResponse()

        sport = None
        if "sport_id" in workout_data:
            sport = Sport.query.filter_by(id=workout_data["sport_id"]).first()
            if not sport:
                return InvalidPayloadErrorResponse(
                    f"sport id {workout_data['sport_id']} not found"
                )

        if "equipment_ids" in workout_data:
            sport_id = (
                workout_data["sport_id"]
                if workout_data.get("sport_id")
                else workout.sport_id
            )
            workout_data["equipments_list"] = handle_equipments(
                workout_data.get("equipment_ids"),
                auth_user,
                sport_id,
                workout.equipments,
            )
        elif sport:
            # remove equipment if invalid for new sport
            # Note: for now only one equipment can be added
            for equipment in workout.equipments:
                if sport.label not in SPORT_EQUIPMENT_TYPES.get(
                    equipment.equipment_type.label, []
                ):
                    workout_data["equipments_list"] = []

        workout = edit_workout(workout, workout_data, auth_user)
        db.session.commit()

        return {
            "status": "success",
            "data": {
                "workouts": [workout.serialize(user=auth_user, light=False)]
            },
        }

    except InvalidEquipmentsException as e:
        return InvalidPayloadErrorResponse(str(e))
    except InvalidEquipmentException as e:
        return EquipmentInvalidPayloadErrorResponse(
            equipment_id=e.equipment_id, message=e.message, status=e.status
        )
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e)


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>", methods=["DELETE"]
)
@require_auth(scopes=["workouts:write"])
@check_workout()
def delete_workout(
    auth_user: User, workout: Workout, workout_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Delete a workout.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      DELETE /api/workouts/kjxavSTUrJvoAh2wvCeGEF HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :param string workout_short_id: workout short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 204: workout deleted
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``workout not found``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    try:
        # update equipments totals
        workout.equipments = []
        db.session.flush()

        db.session.delete(workout)
        db.session.commit()
        return {"status": "no content"}, 204
    except (
        exc.IntegrityError,
        exc.OperationalError,
        ValueError,
        OSError,
    ) as e:
        return handle_error_and_return_response(e, db=db)


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/like", methods=["POST"]
)
@require_auth(scopes=["workouts:write"])
@check_workout(only_owner=False)
def like_workout(
    auth_user: User, workout: Workout, workout_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Add a "like" to a workout.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/workouts/HgzYFXgvWKCEpdq3vYk67q/like HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "workouts": [
              {
                "analysis_visibility": "private",
                "ascent": 231.208,
                "ave_speed": 13.12,
                "bounds": [],
                "creation_date": "Wed, 04 Dec 2024 09:18:26 GMT",
                "descent": 234.208,
                "description": null,
                "distance": 23.41,
                "duration": "3:32:27",
                "equipments": [],
                "id": "HgzYFXgvWKCEpdq3vYk67q",
                "liked": true,
                "likes_count": 1,
                "map": null,
                "map_visibility": "private",
                "max_alt": 104.44,
                "max_speed": 25.59,
                "min_alt": 19.0,
                "modification_date": "Wed, 04 Dec 2024 16:45:14 GMT",
                "moving": "1:47:04",
                "next_workout": null,
                "notes": null,
                "pauses": "1:23:51",
                "previous_workout": null,
                "records": [],
                "segments": [],
                "sport_id": 1,
                "suspended": false,
                "title": "Cycling (Sport) - 2016-04-26 16:42:27",
                "user": {
                  "created_at": "Sun, 24 Nov 2024 16:52:14 GMT",
                  "followers": 0,
                  "following": 0,
                  "nb_workouts": 1,
                  "picture": false,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                },
                "weather_end": null,
                "weather_start": null,
                "with_analysis": false,
                "with_gpx": false,
                "workout_date": "Tue, 26 Apr 2016 14:42:27 GMT",
                "workout_visibility": "public"
              }
            ]
          },
          "status": "success"
        }

    :param string workout_short_id: workout short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``comment not found``
    """
    try:
        like = WorkoutLike(user_id=auth_user.id, workout_id=workout.id)
        db.session.add(like)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
    return {
        "status": "success",
        "data": {"workouts": [workout.serialize(user=auth_user, light=False)]},
    }, 200


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/like/undo", methods=["POST"]
)
@require_auth(scopes=["workouts:write"])
@check_workout(only_owner=False)
def undo_workout_like(
    auth_user: User, workout: Workout, workout_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Remove workout "like".

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/workouts/HgzYFXgvWKCEpdq3vYk67q/like/undo HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "workouts": [
              {
                "analysis_visibility": "private",
                "ascent": 231.208,
                "ave_speed": 13.12,
                "bounds": [],
                "creation_date": "Wed, 04 Dec 2024 09:18:26 GMT",
                "descent": 234.208,
                "description": null,
                "distance": 23.41,
                "duration": "3:32:27",
                "equipments": [],
                "id": "HgzYFXgvWKCEpdq3vYk67q",
                "liked": false,
                "likes_count": 0,
                "map": null,
                "map_visibility": "private",
                "max_alt": 104.44,
                "max_speed": 25.59,
                "min_alt": 19.0,
                "modification_date": "Wed, 04 Dec 2024 16:45:14 GMT",
                "moving": "1:47:04",
                "next_workout": null,
                "notes": null,
                "pauses": "1:23:51",
                "previous_workout": null,
                "records": [],
                "segments": [],
                "sport_id": 1,
                "suspended": false,
                "title": "Cycling (Sport) - 2016-04-26 16:42:27",
                "user": {
                  "created_at": "Sun, 24 Nov 2024 16:52:14 GMT",
                  "followers": 0,
                  "following": 0,
                  "nb_workouts": 1,
                  "picture": false,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                },
                "weather_end": null,
                "weather_start": null,
                "with_analysis": false,
                "with_gpx": false,
                "workout_date": "Tue, 26 Apr 2016 14:42:27 GMT",
                "workout_visibility": "public"
              }
            ]
          },
          "status": "success"
        }

    :param string workout_short_id: workout short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``comment not found``
    """
    like = WorkoutLike.query.filter_by(
        user_id=auth_user.id, workout_id=workout.id
    ).first()
    if like:
        db.session.delete(like)
        db.session.commit()

    return {
        "status": "success",
        "data": {"workouts": [workout.serialize(user=auth_user, light=False)]},
    }, 200


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/likes", methods=["GET"]
)
@require_auth(scopes=["workouts:read"], optional_auth_user=True)
@check_workout(only_owner=False)
def get_workout_likes(
    auth_user: Optional[User], workout: Workout, workout_short_id: str
) -> Union[Dict, HttpResponse]:
    """
    Get users who like the workout.

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/kjxavSTUrJvoAh2wvCeGEF/likes HTTP/1.1

    **Example responses**:

    - success:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "likes": [
              {
                "created_at": "Sun, 31 Dec 2017 09:00:00 GMT",
                "followers": 0,
                "following": 0,
                "nb_workouts": 1,
                "picture": false,
                "role": "user",
                "suspended_at": null,
                "username": "Sam"
              }
            ]
          },
          "status": "success"
        }

    - workout not found:

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

        {
          "data": {
            "likes": []
          },
          "status": "not found"
        }

    :param string workout_short_id: workout short id

    :query integer page: page if using pagination (default: 1)

    :reqheader Authorization: OAuth 2.0 Bearer Token for workout with
               ``private`` or ``followers_only`` visibility

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``workout not found``

    """
    params = request.args.copy()
    page = int(params.get("page", 1))
    likes_pagination = (
        User.query.join(WorkoutLike, User.id == WorkoutLike.user_id)
        .filter(WorkoutLike.workout_id == workout.id)
        .order_by(WorkoutLike.created_at.desc())
        .paginate(
            page=page, per_page=DEFAULT_WORKOUT_LIKES_PER_PAGE, error_out=False
        )
    )
    users = likes_pagination.items
    return {
        "status": "success",
        "data": {
            "likes": [user.serialize(current_user=auth_user) for user in users]
        },
        "pagination": {
            "has_next": likes_pagination.has_next,
            "has_prev": likes_pagination.has_prev,
            "page": likes_pagination.page,
            "pages": likes_pagination.pages,
            "total": likes_pagination.total,
        },
    }


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/suspension/appeal",
    methods=["POST"],
)
@require_auth(scopes=["workouts:write"])
@check_workout(only_owner=True)
def appeal_workout_suspension(
    auth_user: User, workout: Workout, workout_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Appeal workout suspension.

    Only workout author can appeal the suspension.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/workouts/2oRDfncv6vpRkfp3yrCYHt/suspension/appeal HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

        {
          "status": "success"
        }

    :param string workout_short_id: workout short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: appeal created
    :statuscode 400:
        - ``no text provided``
        - ``you can appeal only once``
        - ``workout is not suspended``
        - ``workout has no suspension``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403: ``you do not have permissions``
    :statuscode 404: ``workout not found``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    if not workout.suspended_at:
        return InvalidPayloadErrorResponse("workout is not suspended")
    suspension_action = workout.suspension_action
    if not suspension_action:
        return InvalidPayloadErrorResponse("workout has no suspension")

    text = request.get_json().get("text")
    if not text:
        return InvalidPayloadErrorResponse("no text provided")

    try:
        appeal = ReportActionAppeal(
            action_id=suspension_action.id, user_id=auth_user.id, text=text
        )
        db.session.add(appeal)
        db.session.commit()
        return {"status": "success"}, 201

    except exc.IntegrityError:
        return InvalidPayloadErrorResponse("you can appeal only once")
    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)
