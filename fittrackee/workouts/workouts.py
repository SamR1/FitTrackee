import json
import re
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import requests
from dramatiq_abort import abort
from flask import (
    Blueprint,
    Response,
    current_app,
    request,
    send_from_directory,
)
from sqlalchemy import asc, case, desc, distinct, exc, func
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, RequestEntityTooLarge
from werkzeug.utils import secure_filename

from fittrackee import abortable, appLog, db, limiter
from fittrackee.equipments.exceptions import (
    InvalidEquipmentException,
    InvalidEquipmentsException,
)
from fittrackee.equipments.models import Equipment, WorkoutEquipment
from fittrackee.files import get_absolute_file_path
from fittrackee.oauth2.server import require_auth
from fittrackee.reports.models import ReportActionAppeal
from fittrackee.responses import (
    DataNotFoundErrorResponse,
    EquipmentInvalidPayloadErrorResponse,
    ExceedingValueErrorResponse,
    HttpResponse,
    InternalServerErrorResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    PayloadTooLargeErrorResponse,
    get_error_response_if_file_is_invalid,
    handle_error_and_return_response,
)
from fittrackee.users.models import User, UserTask
from fittrackee.utils import decode_short_id
from fittrackee.visibility_levels import (
    VisibilityLevel,
    can_view,
    can_view_heart_rate,
)

from .constants import SPORTS_WITHOUT_ELEVATION_DATA, WORKOUT_FILE_MIMETYPES
from .decorators import check_workout
from .exceptions import (
    InvalidDurationException,
    WorkoutExceedingValueException,
    WorkoutException,
    WorkoutFileException,
    WorkoutRefreshException,
)
from .models import Sport, Workout, WorkoutLike
from .services import (
    WorkoutCreationService,
    WorkoutsFromFileCreationService,
    WorkoutUpdateService,
)
from .services.workouts_from_file_refresh_service import (
    WorkoutFromFileRefreshService,
)
from .utils.convert import convert_in_duration
from .utils.gpx import (
    WorkoutGPXException,
    extract_segment_from_gpx_file,
    get_chart_data,
    get_file_extension,
)
from .utils.workouts import get_datetime_from_request_args

if TYPE_CHECKING:
    from sqlalchemy.sql.selectable import Subquery

workouts_blueprint = Blueprint("workouts", __name__)

DEFAULT_WORKOUTS_PER_PAGE = 5
MAX_WORKOUTS_PER_PAGE = 100
MAX_WORKOUTS_TO_SEND = 5
DEFAULT_WORKOUT_LIKES_PER_PAGE = 10
NO_STATISTICS = {
    "average_ascent": None,
    "average_descent": None,
    "average_distance": None,
    "average_duration": None,
    "average_speed": None,
    "count": 0,
    "max_speed": None,
    "total_ascent": None,
    "total_descent": None,
    "total_distance": None,
    "total_duration": None,
    "total_sports": 0,
}
DEFAULT_TASKS_PER_PAGE = 5


def get_rounded_float_value(row_value: Optional[Decimal]) -> Optional[float]:
    if row_value is None:
        return None
    return round(float(row_value), 2)


def get_string_duration_value(row_value: Optional[timedelta]) -> Optional[str]:
    if row_value is None:
        return None
    return str(row_value).split(".")[0]


def get_statistics(
    workouts_subquery: "Subquery", *, get_speeds: bool = True
) -> Dict:
    columns: List = [
        func.sum(
            case(
                (
                    Sport.label.not_in(SPORTS_WITHOUT_ELEVATION_DATA),
                    workouts_subquery.c.ascent,
                ),
                else_=None,
            )
        ),
        func.sum(
            case(
                (
                    Sport.label.not_in(SPORTS_WITHOUT_ELEVATION_DATA),
                    workouts_subquery.c.descent,
                ),
                else_=None,
            )
        ),
        func.sum(workouts_subquery.c.distance),
        func.sum(workouts_subquery.c.moving),
        func.avg(
            case(
                (
                    Sport.label.not_in(SPORTS_WITHOUT_ELEVATION_DATA),
                    workouts_subquery.c.ascent,
                ),
                else_=None,
            )
        ),
        func.avg(
            case(
                (
                    Sport.label.not_in(SPORTS_WITHOUT_ELEVATION_DATA),
                    workouts_subquery.c.descent,
                ),
                else_=None,
            )
        ),
        func.avg(workouts_subquery.c.distance),
        func.avg(workouts_subquery.c.moving),
        func.count(workouts_subquery.c.id),
        func.count(distinct(workouts_subquery.c.sport_id)),
    ]
    if get_speeds:
        columns = [
            *columns,
            func.avg(workouts_subquery.c.ave_speed),
            func.max(workouts_subquery.c.max_speed),
        ]
    stats_query = (
        db.session.query(*columns)
        .join(Sport, Sport.id == workouts_subquery.c.sport_id)
        .first()
    )
    if not stats_query:
        return NO_STATISTICS

    total_sports = stats_query[9]
    return_speeds = total_sports == 1 and get_speeds
    return {
        "average_ascent": get_rounded_float_value(stats_query[4]),
        "average_descent": get_rounded_float_value(stats_query[5]),
        "average_distance": get_rounded_float_value(stats_query[6]),
        "average_duration": get_string_duration_value(stats_query[7]),
        "average_speed": (
            get_rounded_float_value(stats_query[10]) if return_speeds else None
        ),
        "count": stats_query[8],
        "max_speed": (
            get_rounded_float_value(stats_query[11]) if return_speeds else None
        ),
        "total_ascent": get_rounded_float_value(stats_query[0]),
        "total_descent": get_rounded_float_value(stats_query[1]),
        "total_distance": get_rounded_float_value(stats_query[2]),
        "total_duration": get_string_duration_value(stats_query[3]),
        "total_sports": total_sports,
    }


def download_workout_file(
    workout_short_id: str, auth_user_id: int, original_file: bool
) -> Union[HttpResponse, Response]:
    workout_uuid = decode_short_id(workout_short_id)
    workout = Workout.query.filter_by(
        uuid=workout_uuid, user_id=auth_user_id
    ).first()
    if not workout:
        return DataNotFoundErrorResponse(
            data_type="workout",
            message=f"workout not found (id: {workout_short_id})",
        )

    if (original_file and workout.original_file is None) or (
        not original_file and workout.gpx is None
    ):
        return DataNotFoundErrorResponse(
            data_type="original_file" if original_file else "gpx",
            message=(
                f"no {'original' if original_file else 'gpx'} "
                f"file for workout (id: {workout_short_id})"
            ),
        )

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        workout.original_file if original_file else workout.gpx,
        mimetype=WORKOUT_FILE_MIMETYPES[
            get_file_extension(workout.original_file)
            if original_file
            else "gpx"
        ],
        as_attachment=True,
    )


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
                "ave_cadence": null,
                "ave_hr": null,
                "ave_power": null,
                "ave_speed": 18.0,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": null,
                "distance": 18.0,
                "duration": "1:00:00",
                "equipments": [],
                "id": "kjxavSTUrJvoAh2wvCeGEF",
                "liked": false,
                "likes_count": 0,
                "map": null,
                "map_visibility": "private",
                "max_alt": null,
                "max_cadence": null,
                "max_hr": null,
                "max_power": null,
                "max_speed": 18.0,
                "min_alt": null,
                "modification_date": null,
                "moving": "1:00:00",
                "next_workout": null,
                "notes": "",
                "pauses": null,
                "previous_workout": null,
                "records": [],
                "segments": [],
                "sport_id": 1,
                "suspended": false,
                "suspended_at": null,
                "title": "Cycling (Sport) - 2018-01-01 08:00:00",
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
                "workout_date": "Mon, 01 Jan 2018 07:00:00 GMT",
                "workout_visibility": "private"
              }
            ]
          },
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 1,
            "total": 1
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
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 0,
            "total": 0
          },
          "status": "success"
        }

    - with statistics

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "statistics": {
              "all": {
                "ave_speed": null,
                "count": 0,
                "max_speed": null,
                "total_ascent": null,
                "total_descent": null,
                "total_distance": null,
                "total_duration": null
              },
              "current_page": {
                "ave_speed": null,
                "count": 0,
                "max_speed": null,
                "total_ascent": null,
                "total_descent": null,
                "total_distance": null,
                "total_duration": null
              }
            },
            "workouts": []
          },
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 0,
            "total": 0
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
    :query boolean return_equipments: return workouts with equipment
                         (by default, equipment is not returned).
                         **Note**: It's not a filter.
                         **Warning**: Needed for 3rd-party applications
                         updating equipments.
    :query string workout_visibility: workout visibility (``private``,
                         ``followers_only`` or ``public``)
    :query boolean with_statistics: return statistics when ``true``
                        (by default, statistics are not returned)

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
        workout_visibility = params.get("workout_visibility")
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
        if workout_visibility:
            if workout_visibility not in set(
                item.value for item in VisibilityLevel
            ):
                return InvalidPayloadErrorResponse(
                    "invalid value for visibility"
                )
            filters.append(
                Workout.workout_visibility
                == VisibilityLevel(workout_visibility).value
            )

        workouts_query = (
            Workout.query.outerjoin(WorkoutEquipment)
            .filter(*filters)
            .order_by(
                (
                    asc(workout_column)
                    if order == "asc"
                    else desc(workout_column)
                ),
            )
        )

        workouts_pagination = workouts_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        workouts = workouts_pagination.items
        with_equipments = (
            params.get("return_equipments", "false").lower() == "true"
        )

        statistics = {}
        if params.get("with_statistics", "false").lower() == "true":
            if workouts_pagination.total == 0:
                statistics = {
                    "statistics": {
                        "current_page": {**NO_STATISTICS},
                        "all": {**NO_STATISTICS},
                    }
                }
            elif workouts_pagination.total == 1:
                workout = workouts[0]
                return_elevation_data = (
                    workout.sport.label not in SPORTS_WITHOUT_ELEVATION_DATA
                )
                ascent = (
                    None
                    if workout.ascent is None or not return_elevation_data
                    else float(workout.ascent)
                )
                descent = (
                    None
                    if workout.descent is None or not return_elevation_data
                    else float(workout.descent)
                )
                distance = (
                    None
                    if workout.distance is None
                    else float(workout.distance)
                )
                duration = (
                    None if workout.moving is None else str(workout.moving)
                )
                workout_total: Dict = {
                    "average_ascent": ascent,
                    "average_descent": descent,
                    "average_distance": distance,
                    "average_duration": duration,
                    "average_speed": (
                        None
                        if workout.ave_speed is None
                        else float(workout.ave_speed)
                    ),
                    "count": 1,
                    "max_speed": (
                        None
                        if workout.max_speed is None
                        else float(workout.max_speed)
                    ),
                    "total_ascent": ascent,
                    "total_descent": descent,
                    "total_distance": distance,
                    "total_duration": duration,
                    "total_sports": 1,
                }
                statistics = {
                    "statistics": {
                        "current_page": {**workout_total},
                        "all": {**workout_total},
                    }
                }
            else:
                workouts_subquery = (
                    workouts_query.offset((page - 1) * per_page)
                    .limit(per_page)
                    .subquery()
                )
                get_speeds = True
                if workouts_pagination.pages == 1:
                    sport_ids = {workout.sport_id for workout in workouts}
                    # do not get speeds when workouts with different sport
                    # are fetched
                    get_speeds = len(sport_ids) == 1
                current_page_stats = get_statistics(
                    workouts_subquery,
                    get_speeds=get_speeds,
                )
                statistics = {
                    "statistics": {"current_page": current_page_stats}
                }

                if current_page_stats["count"] == workouts_pagination.total:
                    statistics["statistics"]["all"] = {**current_page_stats}
                else:
                    all_workouts_subquery = workouts_query
                    if current_app.config["stats_workouts_limit"]:
                        all_workouts_subquery = all_workouts_subquery.limit(
                            max(
                                current_app.config["stats_workouts_limit"],
                                per_page,
                            )
                        )
                    workouts_subquery = all_workouts_subquery.subquery()
                    statistics["statistics"]["all"] = get_statistics(
                        workouts_subquery,
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
                ],
                **statistics,
            },
            "pagination": {
                "has_next": workouts_pagination.has_next,
                "has_prev": workouts_pagination.has_prev,
                "page": workouts_pagination.page,
                "pages": workouts_pagination.pages,
                "total": workouts_pagination.total,
            },
        }
    except InvalidDurationException as e:
        return InvalidPayloadErrorResponse(str(e))
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
                "ave_cadence": null,
                "ave_hr": null,
                "ave_power": null,
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
                "max_cadence": null,
                "max_hr": null,
                "max_power": null,
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
        file_content: Optional[str] = None
        can_see_heart_rate = can_view_heart_rate(workout.user, auth_user)
        if data_type == "chart_data":
            chart_data_content = get_chart_data(
                absolute_gpx_filepath,
                workout.sport.label,
                workout.ave_cadence,
                can_see_heart_rate=can_see_heart_rate,
                segment_id=segment_id,
            )
        else:  # data_type == 'gpx'
            with open(absolute_gpx_filepath, encoding="utf-8") as f:
                gpx_content = f.read()
                if segment_id is not None:
                    gpx_segment_content = extract_segment_from_gpx_file(
                        gpx_content, segment_id
                    )
            file_content = (
                gpx_content if segment_id is None else gpx_segment_content
            )
            if file_content and not can_see_heart_rate:
                file_content = re.sub(
                    r"<(.*):hr>([\r\n\d]*)</(.*):hr>",
                    "",
                    file_content,
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
                    else file_content
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
    Download gpx file (original or generated by FitTrackee).

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
    return download_workout_file(
        workout_short_id, auth_user.id, original_file=False
    )


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/original/download",
    methods=["GET"],
)
@require_auth(scopes=["workouts:read"])
def download_workout_original_file(
    auth_user: User, workout_short_id: str
) -> Union[HttpResponse, Response]:
    """
    Download original file (gpx, kml, tcx or fit file).

    **Scope**: ``workouts:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/kjxavSTUrJvoAh2wvCeGEF/original/download HTTP/1.1

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
        - ``no original file for workout``
    """
    return download_workout_file(
        workout_short_id, auth_user.id, original_file=True
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
    Post a workout with a file.

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/workouts/ HTTP/1.1
      Content-Type: multipart/form-data

    **Example response**:

    - when upload is synchronous

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

        {
          "data": {
            "errored_workouts": [],
            "workouts": [
              {
                "analysis_visibility": "private",
                "ascent": 435.621,
                "ave_cadence": null,
                "ave_hr": null,
                "ave_power": null,
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
                "max_cadence": null,
                "max_hr": null,
                "max_power": null,
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
                    "ave_cadence": null,
                    "ave_hr": null,
                    "ave_power": null,
                    "ave_speed": 13.14,
                    "descent": 427.499,
                    "distance": 23.478,
                    "duration": "2:08:35",
                    "max_alt": 158.41,
                    "max_cadence": null,
                    "max_hr": null,
                    "max_power": null,
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

    - when upload is asynchronous

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

        {
          "data": {
            "task_id": "JKtd4tpQDgAPwNTsjjPdVh"
          },
          "status": "in_progress"
        }

    :form file: workout file or archive (allowed extensions: .gpx, .kml, .kmz,
       .fit, .tcx, .zip)
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

    :statuscode 200: archive upload in progress
    :statuscode 201: workout created
    :statuscode 400:
        - ``invalid payload``
        - ``no file part``
        - ``no selected file``
        - ``file extension not allowed``
        - ``error when parsing fit file``
        - ``error when parsing gpx file``
        - ``error when parsing kml file``
        - ``error when parsing kmz file``
        - ``error when parsing tcx file``
        - ``gpx file is invalid``
        - ``no activities in tcx file``
        - ``no coordinates in tcx file``
        - ``no laps or no tracks in tcx file``
        - ``no tracks in gpx file``
        - ``no tracks in kml file``
        - ``<time> is missing in gpx file``
        - ``unsupported kml file``
        - ``no valid segments with GPS found in fit file``
        - ``equipment_ids must be an array of strings``
        - ``only one equipment can be added``
        - ``equipment with id <equipment_id> does not exist``
        - ``invalid equipment id <equipment_id> for sport``
        - ``equipment with id <equipment_id> is inactive``
        - ``one or more values, entered or calculated, exceed the limits``
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
    workout_file = request.files["file"]

    try:
        service = WorkoutsFromFileCreationService(
            auth_user, workout_data, workout_file
        )
        new_workouts, processing_output = service.process()
        if processing_output["task_short_id"]:
            return {
                "status": "in_progress",
                "data": {"task_id": processing_output["task_short_id"]},
            }, 200

        if len(new_workouts) > 0 and not processing_output["errored_workouts"]:
            response_object = {
                "status": "created",
                "data": {
                    "workouts": [
                        new_workout.serialize(user=auth_user, light=False)
                        for new_workout in new_workouts
                    ],
                },
            }
        else:
            return {
                "status": "fail",
                "new_workouts": len(new_workouts),
                "errored_workouts": processing_output["errored_workouts"],
            }, 400
    except WorkoutExceedingValueException as e:
        appLog.error(e.detail)
        return ExceedingValueErrorResponse()
    except InvalidEquipmentsException as e:
        return InvalidPayloadErrorResponse(str(e))
    except InvalidEquipmentException as e:
        return EquipmentInvalidPayloadErrorResponse(
            equipment_id=e.equipment_id, message=e.message, status=e.status
        )
    except (WorkoutException, WorkoutFileException) as e:
        db.session.rollback()
        if e.status == "error":
            appLog.exception("Error when creating workout")
            return InternalServerErrorResponse(e.message)
        return InvalidPayloadErrorResponse(e.message, e.status)
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
                "ave_cadence": null,
                "ave_hr": null,
                "ave_power": null,
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
                "max_cadence": null,
                "max_hr": null,
                "max_power": null,
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
        - ``one or more values, entered or calculated, exceed the limits``
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

    try:
        service = WorkoutCreationService(auth_user, workout_data)
        [new_workout], _ = service.process()
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
    except WorkoutExceedingValueException as e:
        appLog.error(e.detail)
        return ExceedingValueErrorResponse()
    except InvalidEquipmentsException as e:
        return InvalidPayloadErrorResponse(str(e))
    except InvalidEquipmentException as e:
        return EquipmentInvalidPayloadErrorResponse(
            equipment_id=e.equipment_id, message=e.message, status=e.status
        )
    except WorkoutException as e:
        db.session.rollback()
        if e.e:
            appLog.error(e.e)
        if e.status == "error":
            return InternalServerErrorResponse(e.message)
        return InvalidPayloadErrorResponse(e.message, e.status)
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
                "ave_cadence": null,
                "ave_hr": null,
                "ave_power": null,
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
                "max_cadence": null,
                "max_hr": null,
                "max_power": null,
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
        - ``one or more values, entered or calculated, exceed the limits``
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
        service = WorkoutUpdateService(auth_user, workout, workout_data)
        service.update()
        db.session.commit()

        return {
            "status": "success",
            "data": {
                "workouts": [workout.serialize(user=auth_user, light=False)]
            },
        }
    except WorkoutExceedingValueException as e:
        appLog.error(e.detail)
        return ExceedingValueErrorResponse()
    except InvalidEquipmentsException as e:
        return InvalidPayloadErrorResponse(str(e))
    except InvalidEquipmentException as e:
        return EquipmentInvalidPayloadErrorResponse(
            equipment_id=e.equipment_id, message=e.message, status=e.status
        )
    except WorkoutException as e:
        db.session.rollback()
        if e.e:
            appLog.error(e.e)
        if e.status == "error":
            return InternalServerErrorResponse(e.message)
        return InvalidPayloadErrorResponse(e.message, e.status)
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
                "ave_cadence": null,
                "ave_hr": null,
                "ave_power": null,
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
                "max_cadence": null,
                "max_hr": null,
                "max_power": null,
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
                "ave_cadence": null,
                "ave_hr": null,
                "ave_power": null,
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
                "max_cadence": null,
                "max_hr": null,
                "max_power": null,
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


@workouts_blueprint.route("/workouts/upload-tasks", methods=["GET"])
@require_auth(scopes=["workouts:read"])
def get_workouts_upload_tasks(
    auth_user: User,
) -> Tuple[Dict, int]:
    """
    Get user tasks for workouts archive upload

    **Scope**: ``workouts:read``

    **Example request**:

    - without parameters:

    .. sourcecode:: http

      GET /api/workouts/tasks HTTP/1.1
      Content-Type: application/json

    - with 'page' parameter:

    .. sourcecode:: http

      GET /api/workouts/tasks?page=2 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "data": {
          "tasks": [
            {
              "created_at": "Sun, 30 Mar 2025 10:26:17 GMT",
              "errored_files": {},
              "files_count": 10,
              "id": "JEiR6cDcADX8bZ6ZeQssnr",
              "progress": 10,
              "status": "in_progress",
              "type": "workouts_archive_upload"
            }
          ]
        },
        "pagination": {
          "has_next": false,
          "has_prev": false,
          "page": 1,
          "pages": 1,
          "total": 1
        },
        "status": "success"
      }

    :query integer page: page for pagination (default: 1)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    """
    params = request.args.copy()
    page = int(params.get("page", 1))
    per_page = DEFAULT_TASKS_PER_PAGE
    tasks_pagination = (
        UserTask.query.filter_by(
            user_id=auth_user.id, task_type="workouts_archive_upload"
        )
        .order_by(UserTask.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return {
        "status": "success",
        "data": {
            "tasks": [
                task.serialize(current_user=auth_user)
                for task in tasks_pagination.items
            ]
        },
        "pagination": {
            "has_next": tasks_pagination.has_next,
            "has_prev": tasks_pagination.has_prev,
            "page": tasks_pagination.page,
            "pages": tasks_pagination.pages,
            "total": tasks_pagination.total,
        },
    }, 200


@workouts_blueprint.route(
    "/workouts/upload-tasks/<string:task_short_id>", methods=["GET"]
)
@require_auth(scopes=["workouts:read"])
def get_workouts_upload_task(
    auth_user: User, task_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Get a given task for workouts archive upload

    **Scope**: ``workouts:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/workouts/tasks/JEiR6cDcADX8bZ6ZeQssnr HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "task": {
          "created_at": "Sun, 30 Mar 2025 10:26:17 GMT",
          "errored_files": {},
          "files_count": 10,
          "id": "JEiR6cDcADX8bZ6ZeQssnr",
          "progress": 10,
          "status": "in_progress",
          "type": "workouts_archive_upload"
        },
        "status": "success"
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404:
        - ``no task found``
    """
    task = UserTask.query.filter_by(
        user_id=auth_user.id, uuid=decode_short_id(task_short_id)
    ).first()

    if not task or task.task_type != "workouts_archive_upload":
        return NotFoundErrorResponse("no task found")

    return {
        "status": "success",
        "task": task.serialize(current_user=auth_user),
    }, 200


@workouts_blueprint.route(
    "/workouts/upload-tasks/<string:task_short_id>/abort", methods=["POST"]
)
@require_auth(scopes=["workouts:write"])
def abort_workouts_upload_task(
    auth_user: User, task_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Abort ongoing task for workouts archive upload

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/workouts/tasks/JEiR6cDcADX8bZ6ZeQssnr/abort HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "task": {
          "created_at": "Sun, 30 Mar 2025 10:26:17 GMT",
          "errored_files": {},
          "files_count": 10,
          "id": "JEiR6cDcADX8bZ6ZeQssnr",
          "progress": 10,
          "status": "aborted",
          "type": "workouts_archive_upload"
        },
        "status": "success"
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``only queued and ongoing tasks can be aborted``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404:
        - ``no task found``
    :statuscode 500:
        - ``error when aborting task``
    """
    task = UserTask.query.filter_by(
        user_id=auth_user.id, uuid=decode_short_id(task_short_id)
    ).first()

    if not task or task.task_type != "workouts_archive_upload":
        return NotFoundErrorResponse("no task found")

    if not task.message_id:
        return InternalServerErrorResponse("error when aborting task")

    if task.status not in [
        "in_progress",
        "queued",
    ]:
        return InvalidPayloadErrorResponse(
            "only queued and ongoing tasks can be aborted"
        )

    try:
        abort(message_id=task.message_id, middleware=abortable)
        task.aborted = True
        db.session.commit()
    except Exception as e:
        appLog.exception(e)
        return InternalServerErrorResponse("error when aborting task")

    return {
        "status": "success",
        "task": task.serialize(current_user=auth_user),
    }, 200


@workouts_blueprint.route(
    "/workouts/upload-tasks/<string:task_short_id>", methods=["DELETE"]
)
@require_auth(scopes=["workouts:read"])
def delete_workouts_upload_task(
    auth_user: User, task_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Delete workouts archive upload task if status is successful or errored

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      DELETE /api/workouts/tasks/JEiR6cDcADX8bZ6ZeQssnr HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404:
        - ``no task found``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    task = UserTask.query.filter_by(
        user_id=auth_user.id, uuid=decode_short_id(task_short_id)
    ).first()

    if not task or task.task_type != "workouts_archive_upload":
        return NotFoundErrorResponse("no task found")

    if task.status in ["in_progress", "queued"]:
        return InvalidPayloadErrorResponse(
            "queued or ongoing workout upload task can not be deleted"
        )

    try:
        db.session.delete(task)
        db.session.commit()
        return {"status": "no content"}, 204
    except Exception as e:
        return handle_error_and_return_response(e, db=db)


@workouts_blueprint.route(
    "/workouts/<string:workout_short_id>/refresh", methods=["POST"]
)
@require_auth(scopes=["workouts:write"])
@check_workout(only_owner=True)
def refresh_workout(
    auth_user: User, workout: Workout, workout_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Refresh a workout (created by uploading a file):

    - recalculate workout data like max. speed, pauses...
    - regenerate gpx file if original file is not a gpx
    - update weather if weather provided is set and workout does not have
      weather data

    **Scope**: ``workouts:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/workouts/kjxavSTUrJvoAh2wvCeGEF/refresh HTTP/1.1
      Content-Type: application/json

    **Example response**:


    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

        {
          "data": {
            "errored_workouts": [],
            "workouts": [
              {
                "analysis_visibility": "private",
                "ascent": 435.621,
                "ave_cadence": null,
                "ave_hr": null,
                "ave_power": null,
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
                "max_cadence": null,
                "max_hr": null,
                "max_power": null,
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
                    "ave_cadence": null,
                    "ave_hr": null,
                    "ave_power": null,
                    "ave_speed": 13.14,
                    "descent": 427.499,
                    "distance": 23.478,
                    "duration": "2:08:35",
                    "max_alt": 158.41,
                    "max_cadence": null,
                    "max_hr": null,
                    "max_power": null,
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

    :param string workout_short_id: workout short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: workout updated
    :statuscode 400:
        - ``error when parsing fit file``
        - ``error when parsing gpx file``
        - ``error when parsing kml file``
        - ``error when parsing kmz file``
        - ``error when parsing tcx file``
        - ``one or more values, entered or calculated, exceed the limits``
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
        service = WorkoutFromFileRefreshService(workout, update_weather=True)
        updated_workout = service.refresh()
    except WorkoutExceedingValueException as e:
        appLog.error(e.detail)
        return ExceedingValueErrorResponse()
    except (
        WorkoutException,
        WorkoutFileException,
        WorkoutRefreshException,
    ) as e:
        db.session.rollback()
        if e.status == "error":
            appLog.exception("Error when refreshing workout")
            return InternalServerErrorResponse(e.message)
        return InvalidPayloadErrorResponse(e.message, e.status)
    return {
        "status": "success",
        "data": {
            "workouts": [
                updated_workout.serialize(user=auth_user, light=False)
            ]
        },
    }, 200
