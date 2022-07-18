import os
import tempfile
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

import gpxpy.gpx
import pytz
from flask import current_app
from sqlalchemy import exc
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from fittrackee import db
from fittrackee.files import get_absolute_file_path
from fittrackee.users.models import User, UserSportPreference

from ..exceptions import WorkoutException
from ..models import Sport, Workout, WorkoutSegment
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
            pytz.utc.localize(naive_workout_date)
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
        workout_date=gpx_data['start']
        if gpx_data
        else workout_data['workout_date'],
        date_str_format=None if gpx_data else '%Y-%m-%d %H:%M',
        user_timezone=user.timezone,
        with_timezone=True,
    )

    duration = (
        _remove_microseconds(gpx_data['duration'])
        if gpx_data
        else timedelta(seconds=workout_data['duration'])
    )
    distance = gpx_data['distance'] if gpx_data else workout_data['distance']
    title = gpx_data['name'] if gpx_data else workout_data.get('title', '')

    new_workout = Workout(
        user_id=user.id,
        sport_id=workout_data['sport_id'],
        workout_date=workout_date,
        distance=distance,
        duration=duration,
    )
    new_workout.notes = workout_data.get('notes')

    if title is not None and title != '':
        new_workout.title = title
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
    new_segment.duration = segment_data['duration']
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
        workout.title = workout_data.get('title')
    if workout_data.get('notes') is not None:
        workout.notes = workout_data.get('notes')
    if not workout.gpx:
        if workout_data.get('workout_date'):
            workout.workout_date, _ = get_workout_datetime(
                workout_date=workout_data.get('workout_date', ''),
                date_str_format='%Y-%m-%d %H:%M',
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
    _, new_filename = tempfile.mkstemp(
        prefix=f'{workout_date}_{sport_id}_', suffix=extension
    )
    dir_path = os.path.join('workouts', str(auth_user_id))
    file_path = os.path.join(dir_path, new_filename.split('/')[-1])
    return file_path


def process_one_gpx_file(
    params: Dict, filename: str, stopped_speed_threshold: float
) -> Workout:
    """
    Get all data from a gpx file to create a workout with map image
    """
    try:
        gpx_data, map_data, weather_data = get_gpx_info(
            params['file_path'], stopped_speed_threshold
        )
        auth_user = params['auth_user']
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
        raise WorkoutException('error', 'error during gpx file parsing', e)
    except Exception as e:
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
    except (exc.IntegrityError, ValueError) as e:
        raise WorkoutException('fail', 'Error during workout save.', e)


def process_zip_archive(
    common_params: Dict, extract_dir: str, stopped_speed_threshold: float
) -> List:
    """
    Get files from a zip archive and create workouts, if number of files
    does not exceed defined limit.
    """
    with zipfile.ZipFile(common_params['file_path'], "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    new_workouts = []
    gpx_files_limit = current_app.config['gpx_limit_import']
    gpx_files_ok = 0

    for gpx_file in os.listdir(extract_dir):
        if (
            '.' in gpx_file
            and gpx_file.rsplit('.', 1)[1].lower()
            in current_app.config['WORKOUT_ALLOWED_EXTENSIONS']
        ):
            gpx_files_ok += 1
            if gpx_files_ok > gpx_files_limit:
                break
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
    nb_workouts: int, total_average_speed: float, workout_average_speed: float
) -> float:
    return round(
        (
            (total_average_speed * (nb_workouts - 1))
            + float(workout_average_speed)
        )
        / nb_workouts,
        2,
    )
