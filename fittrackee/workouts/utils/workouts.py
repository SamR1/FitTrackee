import os
import secrets
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

import gpxpy.gpx
import pytz
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from fittrackee import appLog, db
from fittrackee.files import get_absolute_file_path
from fittrackee.users.models import User, UserSportPreference
from fittrackee.utils import decode_short_id
from fittrackee.visibility_levels import (
    VisibilityLevel,
    can_view,
    get_map_visibility,
)

from ..constants import WORKOUT_DATE_FORMAT
from ..exceptions import (
    InvalidGPXException,
    WorkoutException,
    WorkoutForbiddenException,
)
from ..models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
    TITLE_MAX_CHARACTERS,
    Sport,
    Workout,
    WorkoutSegment,
)
from .gpx import get_gpx_info
from .maps import generate_map, get_map_hash


def get_workout_datetime(
    workout_date: Union[datetime, str],
    user_timezone: Optional[str],
    date_str_format: Optional[str] = None,
    with_timezone: bool = False,
) -> Tuple[datetime, Optional[datetime]]:
    """
    Return naive datetime and datetime with user timezone if with_timezone
    """
    workout_date_with_user_tz = None

    # workout w/o gpx
    if isinstance(workout_date, str):
        if not date_str_format:
            date_str_format = '%Y-%m-%d %H:%M:%S'
        workout_date = datetime.strptime(workout_date, date_str_format)
        if user_timezone:
            workout_date = pytz.timezone(user_timezone).localize(workout_date)

    if workout_date.tzinfo is None:
        naive_workout_date = workout_date
        if user_timezone and with_timezone:
            # pytz.utc.localize(naive_workout_date)
            workout_date_with_user_tz = pytz.utc.localize(
                naive_workout_date
            ).astimezone(pytz.timezone(user_timezone))
    else:
        naive_workout_date = workout_date.astimezone(pytz.utc).replace(
            tzinfo=None
        )
        if user_timezone and with_timezone:
            workout_date_with_user_tz = workout_date.astimezone(
                pytz.timezone(user_timezone)
            )

    return naive_workout_date, workout_date_with_user_tz


def get_datetime_from_request_args(
    params: Dict, user: User
) -> Tuple[Optional[datetime], Optional[datetime]]:
    date_from = None
    date_to = None

    date_from_str = params.get('from')
    if date_from_str:
        date_from, _ = get_workout_datetime(
            workout_date=date_from_str,
            user_timezone=user.timezone,
            date_str_format='%Y-%m-%d',
        )
    date_to_str = params.get('to')
    if date_to_str:
        date_to, _ = get_workout_datetime(
            workout_date=f'{date_to_str} 23:59:59',
            user_timezone=user.timezone,
        )
    return date_from, date_to


def _remove_microseconds(delta: timedelta) -> timedelta:
    return delta - timedelta(microseconds=delta.microseconds)


def update_workout_data(
    workout: Union[Workout, WorkoutSegment], gpx_data: Dict
) -> Union[Workout, WorkoutSegment]:
    """
    Update workout or workout segment with data from gpx file
    """
    workout.pauses = _remove_microseconds(gpx_data['stop_time'])
    workout.moving = _remove_microseconds(gpx_data['moving_time'])
    workout.min_alt = gpx_data['elevation_min']
    workout.max_alt = gpx_data['elevation_max']
    workout.descent = gpx_data['downhill']
    workout.ascent = gpx_data['uphill']
    workout.max_speed = gpx_data['max_speed']
    workout.ave_speed = gpx_data['average_speed']
    return workout


def create_workout(
    user: User, workout_data: Dict, gpx_data: Optional[Dict] = None
) -> Workout:
    """
    Create Workout from data entered by user and from gpx if a gpx file is
    provided
    """
    workout_date, workout_date_tz = get_workout_datetime(
        workout_date=(
            gpx_data['start'] if gpx_data else workout_data['workout_date']
        ),
        date_str_format=None if gpx_data else WORKOUT_DATE_FORMAT,
        user_timezone=user.timezone,
        with_timezone=True,
    )

    duration = (
        _remove_microseconds(gpx_data['duration'])
        if gpx_data
        else timedelta(seconds=workout_data['duration'])
    )
    distance = gpx_data['distance'] if gpx_data else workout_data['distance']
    title = (
        workout_data.get('title', '')
        if workout_data.get('title', '')
        else gpx_data['name']
        if gpx_data
        else ''
    )
    description = (
        workout_data.get('description', '')
        if workout_data.get('description', '')
        else gpx_data['description']
        if gpx_data
        else ''
    )

    new_workout = Workout(
        user_id=user.id,
        sport_id=workout_data['sport_id'],
        workout_date=workout_date,
        distance=distance,
        duration=duration,
    )
    new_workout.notes = (
        None
        if workout_data.get('notes') is None
        else workout_data['notes'][:NOTES_MAX_CHARACTERS]
    )
    new_workout.description = (
        description[:DESCRIPTION_MAX_CHARACTERS] if description else None
    )

    new_workout.workout_visibility = VisibilityLevel(
        workout_data.get('workout_visibility', user.workouts_visibility.value)
    )
    new_workout.map_visibility = get_map_visibility(
        VisibilityLevel(
            workout_data.get('map_visibility', user.map_visibility.value)
        ),
        new_workout.workout_visibility,
    )

    if title is not None and title != '':
        new_workout.title = title[:TITLE_MAX_CHARACTERS]
    else:
        sport = Sport.query.filter_by(id=new_workout.sport_id).first()
        fmt = "%Y-%m-%d %H:%M:%S"
        workout_datetime = (
            workout_date_tz.strftime(fmt)
            if workout_date_tz
            else new_workout.workout_date.strftime(fmt)
        )
        new_workout.title = f'{sport.label} - {workout_datetime}'

    if gpx_data:
        new_workout.gpx = gpx_data['filename']
        new_workout.bounds = gpx_data['bounds']
        update_workout_data(new_workout, gpx_data)
    else:
        new_workout.moving = duration
        new_workout.ave_speed = (
            None
            if duration.seconds == 0
            else float(new_workout.distance) / (duration.seconds / 3600)
        )
        new_workout.max_speed = new_workout.ave_speed
        new_workout.ascent = workout_data.get('ascent')
        new_workout.descent = workout_data.get('descent')
    if workout_data.get('equipments_list') is not None:
        new_workout.equipments = workout_data.get('equipments_list')
    return new_workout


def create_segment(
    workout_id: int, workout_uuid: UUID, segment_data: Dict
) -> WorkoutSegment:
    """
    Create Workout Segment from gpx data
    """
    new_segment = WorkoutSegment(
        workout_id=workout_id,
        workout_uuid=workout_uuid,
        segment_id=segment_data['idx'],
    )
    new_segment.duration = _remove_microseconds(segment_data['duration'])
    new_segment.distance = segment_data['distance']
    update_workout_data(new_segment, segment_data)
    return new_segment


def update_workout(workout: Workout) -> Workout:
    """
    Update workout data from gpx file
    """
    gpx_data, _, _ = get_gpx_info(
        get_absolute_file_path(workout.gpx), False, False
    )
    updated_workout = update_workout_data(workout, gpx_data)
    updated_workout.duration = gpx_data['duration']
    updated_workout.distance = gpx_data['distance']
    db.session.flush()

    for segment_idx, segment in enumerate(updated_workout.segments):
        segment_data = gpx_data['segments'][segment_idx]
        updated_segment = update_workout_data(segment, segment_data)
        updated_segment.duration = segment_data['duration']
        updated_segment.distance = segment_data['distance']
        db.session.flush()

    return updated_workout


def edit_workout(
    workout: Workout, workout_data: Dict, auth_user: User
) -> Workout:
    """
    Edit a workout
    Note: the gpx file is NOT modified

    In a next version, map_data and weather_data will be updated
    (case of a modified gpx file, see issue #7)
    """
    if workout_data.get('sport_id'):
        workout.sport_id = workout_data.get('sport_id')
    if workout_data.get('title'):
        workout.title = workout_data['title'][:TITLE_MAX_CHARACTERS]
    if workout_data.get('notes') is not None:
        workout.notes = workout_data['notes'][:NOTES_MAX_CHARACTERS]
    if workout_data.get('description') is not None:
        workout.description = workout_data['description'][
            :DESCRIPTION_MAX_CHARACTERS
        ]
    if workout_data.get('equipments_list') is not None:
        workout.equipments = workout_data.get('equipments_list')
    if workout_data.get('workout_visibility') is not None:
        workout.workout_visibility = VisibilityLevel(
            workout_data.get('workout_visibility')
        )
    if not workout.gpx:
        if workout_data.get('workout_date'):
            workout.workout_date, _ = get_workout_datetime(
                workout_date=workout_data.get('workout_date', ''),
                date_str_format=WORKOUT_DATE_FORMAT,
                user_timezone=auth_user.timezone,
            )

        if workout_data.get('duration'):
            workout.duration = timedelta(seconds=workout_data['duration'])
            workout.moving = workout.duration

        if workout_data.get('distance'):
            workout.distance = workout_data['distance']

        workout.ave_speed = (
            None
            if workout.duration.seconds == 0
            else float(workout.distance) / (workout.duration.seconds / 3600)
        )
        workout.max_speed = workout.ave_speed

        if 'ascent' in workout_data:
            workout.ascent = workout_data.get('ascent')

        if 'descent' in workout_data:
            workout.descent = workout_data.get('descent')

    else:
        if workout_data.get('map_visibility') is not None:
            map_visibility = VisibilityLevel(
                workout_data.get('map_visibility')
            )
            workout.map_visibility = get_map_visibility(
                map_visibility, workout.workout_visibility
            )
    return workout


def get_file_path(dir_path: str, filename: str) -> str:
    """
    Get full path for a file
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, filename)
    return file_path


def get_new_file_path(
    auth_user_id: int,
    workout_date: str,
    sport_id: int,
    old_filename: Optional[str] = None,
    extension: Optional[str] = None,
) -> str:
    """
    Generate a file path from user and workout data
    """
    if not extension and old_filename:
        extension = f".{old_filename.rsplit('.', 1)[1].lower()}"
    suffix = secrets.token_urlsafe(8)
    new_filename = f"{workout_date}_{sport_id}_{suffix}{extension}"
    dir_path = os.path.join('workouts', str(auth_user_id))
    file_path = os.path.join(dir_path, new_filename.split('/')[-1])
    return file_path


def delete_files(
    absolute_gpx_filepath: Optional[str], absolute_map_filepath: Optional[str]
) -> None:
    try:
        if absolute_gpx_filepath and os.path.exists(absolute_gpx_filepath):
            os.remove(absolute_gpx_filepath)
        if absolute_map_filepath and os.path.exists(absolute_map_filepath):
            os.remove(absolute_map_filepath)
    except Exception:
        appLog.error('Unable to delete files after processing error.')


def process_one_gpx_file(
    params: Dict, filename: str, stopped_speed_threshold: float
) -> Workout:
    """
    Get all data from a gpx file to create a workout with map image
    """
    absolute_gpx_filepath = None
    absolute_map_filepath = None
    try:
        auth_user = params['auth_user']
        gpx_data, map_data, weather_data = get_gpx_info(
            gpx_file=params['file_path'],
            stopped_speed_threshold=stopped_speed_threshold,
            use_raw_gpx_speed=auth_user.use_raw_gpx_speed,
        )
        workout_date, _ = get_workout_datetime(
            workout_date=gpx_data['start'],
            date_str_format=None if gpx_data else '%Y-%m-%d %H:%M',
            user_timezone=None,
        )
        new_filepath = get_new_file_path(
            auth_user_id=auth_user.id,
            workout_date=workout_date.strftime('%Y-%m-%d_%H-%M-%S'),
            old_filename=filename,
            sport_id=params['sport_id'],
        )
        absolute_gpx_filepath = get_absolute_file_path(new_filepath)
        os.rename(params['file_path'], absolute_gpx_filepath)
        gpx_data['filename'] = new_filepath

        map_filepath = get_new_file_path(
            auth_user_id=auth_user.id,
            workout_date=workout_date.strftime('%Y-%m-%d_%H-%M-%S'),
            extension='.png',
            sport_id=params['sport_id'],
        )
        absolute_map_filepath = get_absolute_file_path(map_filepath)
        generate_map(absolute_map_filepath, map_data)
    except (gpxpy.gpx.GPXXMLSyntaxException, TypeError) as e:
        delete_files(absolute_gpx_filepath, absolute_map_filepath)
        raise WorkoutException('error', 'error during gpx file parsing', e)
    except InvalidGPXException as e:
        delete_files(absolute_gpx_filepath, absolute_map_filepath)
        raise WorkoutException('error', str(e))
    except Exception as e:
        delete_files(absolute_gpx_filepath, absolute_map_filepath)
        raise WorkoutException('error', 'error during gpx processing', e)

    try:
        new_workout = create_workout(
            auth_user, params['workout_data'], gpx_data
        )
        new_workout.map = map_filepath
        new_workout.map_id = get_map_hash(map_filepath)
        new_workout.weather_start = weather_data[0]
        new_workout.weather_end = weather_data[1]
        db.session.add(new_workout)
        db.session.flush()

        for segment_data in gpx_data['segments']:
            new_segment = create_segment(
                new_workout.id, new_workout.uuid, segment_data
            )
            db.session.add(new_segment)
        db.session.commit()
        return new_workout
    except Exception as e:
        delete_files(absolute_gpx_filepath, absolute_map_filepath)
        raise WorkoutException('error', 'error when saving workout', e)


def is_gpx_file(filename: str) -> bool:
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower()
        in current_app.config['WORKOUT_ALLOWED_EXTENSIONS']
    )


def process_zip_archive(
    common_params: Dict, extract_dir: str, stopped_speed_threshold: float
) -> List:
    """
    Get files from a zip archive and create workouts, if number of files
    does not exceed defined limit.
    """
    with zipfile.ZipFile(common_params['file_path'], "r") as zip_ref:
        max_file_size = current_app.config['max_single_file_size']
        gpx_files_count = 0
        files_with_invalid_size_count = 0
        for zip_info in zip_ref.infolist():
            if is_gpx_file(zip_info.filename):
                gpx_files_count += 1
                if zip_info.file_size > max_file_size:
                    files_with_invalid_size_count += 1

        if gpx_files_count > current_app.config['gpx_limit_import']:
            raise WorkoutException(
                'fail', 'the number of files in the archive exceeds the limit'
            )

        if files_with_invalid_size_count > 0:
            raise WorkoutException(
                'fail',
                'at least one file in zip archive exceeds size limit, '
                'please check the archive',
            )

        zip_ref.extractall(extract_dir)

    new_workouts = []

    for gpx_file in os.listdir(extract_dir):
        if is_gpx_file(gpx_file):
            file_path = os.path.join(extract_dir, gpx_file)
            params = common_params
            params['file_path'] = file_path
            new_workout = process_one_gpx_file(
                params, gpx_file, stopped_speed_threshold
            )
            new_workouts.append(new_workout)

    return new_workouts


def process_files(
    auth_user: User,
    workout_data: Dict,
    workout_file: FileStorage,
    folders: Dict,
) -> List:
    """
    Store gpx file or zip archive and create workouts
    """
    if workout_file.filename is None:
        raise WorkoutException('error', 'File has no filename.')
    filename = secure_filename(workout_file.filename)
    extension = f".{filename.rsplit('.', 1)[1].lower()}"
    file_path = get_file_path(folders['tmp_dir'], filename)
    sport = Sport.query.filter_by(id=workout_data.get('sport_id')).first()
    if not sport:
        raise WorkoutException(
            'error',
            f"Sport id: {workout_data.get('sport_id')} does not exist",
        )
    sport_preferences = UserSportPreference.query.filter_by(
        user_id=auth_user.id, sport_id=sport.id
    ).first()
    stopped_speed_threshold = (
        sport.stopped_speed_threshold
        if sport_preferences is None
        else sport_preferences.stopped_speed_threshold
    )

    # get default equipment if sport preferences exists
    if "equipments_list" not in workout_data and sport_preferences:
        workout_data['equipments_list'] = [
            equipment
            for equipment in sport_preferences.default_equipments.all()
            if equipment.is_active is True
        ]

    common_params = {
        'auth_user': auth_user,
        'workout_data': workout_data,
        'file_path': file_path,
        'sport_id': sport.id,
    }

    try:
        workout_file.save(file_path)
    except Exception as e:
        raise WorkoutException('error', 'Error during workout file save.', e)

    if extension == ".gpx":
        return [
            process_one_gpx_file(
                common_params,
                filename,
                stopped_speed_threshold,
            )
        ]
    else:
        return process_zip_archive(
            common_params,
            folders['extract_dir'],
            stopped_speed_threshold,
        )


def get_average_speed(
    total_workouts: int,
    total_average_speed: float,
    workout_average_speed: float,
) -> float:
    return round(
        (
            (total_average_speed * (total_workouts - 1))
            + float(workout_average_speed)
        )
        / total_workouts,
        2,
    )


def get_ordered_workouts(workouts: List[Workout], limit: int) -> List[Workout]:
    return sorted(
        workouts, key=lambda workout: workout.workout_date, reverse=True
    )[:limit]


def get_workout(
    workout_short_id: str, auth_user: Optional[User], allow_admin: bool = False
) -> Workout:
    workout_uuid = decode_short_id(workout_short_id)
    workout = Workout.query.filter(Workout.uuid == workout_uuid).first()
    if not workout or (
        not can_view(workout, 'workout_visibility', auth_user)
        and not (allow_admin and auth_user and auth_user.has_admin_rights)
    ):
        raise WorkoutForbiddenException()
    return workout
