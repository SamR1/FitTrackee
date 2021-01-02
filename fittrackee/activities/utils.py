import hashlib
import os
import tempfile
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

import gpxpy.gpx
import pytz
from fittrackee import appLog, db
from flask import current_app
from sqlalchemy import exc
from staticmap import Line, StaticMap
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..users.models import User
from .models import Activity, ActivitySegment, Sport
from .utils_files import get_absolute_file_path
from .utils_gpx import get_gpx_info


class ActivityException(Exception):
    def __init__(
        self, status: str, message: str, e: Optional[Exception] = None
    ) -> None:
        self.status = status
        self.message = message
        self.e = e


def get_datetime_with_tz(
    timezone: str, activity_date: datetime, gpx_data: Optional[Dict] = None
) -> Tuple[Optional[datetime], datetime]:
    """
    Return naive datetime and datetime with user timezone
    """
    activity_date_tz = None
    if timezone:
        user_tz = pytz.timezone(timezone)
        utc_tz = pytz.utc
        if gpx_data:
            # activity date in gpx is in UTC, but in naive datetime
            fmt = '%Y-%m-%d %H:%M:%S'
            activity_date_string = activity_date.strftime(fmt)
            activity_date_tmp = utc_tz.localize(
                datetime.strptime(activity_date_string, fmt)
            )
            activity_date_tz = activity_date_tmp.astimezone(user_tz)
        else:
            activity_date_tz = user_tz.localize(activity_date)
            activity_date = activity_date_tz.astimezone(utc_tz)
            # make datetime 'naive' like in gpx file
            activity_date = activity_date.replace(tzinfo=None)

    return activity_date_tz, activity_date


def update_activity_data(
    activity: Union[Activity, ActivitySegment], gpx_data: Dict
) -> Union[Activity, ActivitySegment]:
    """
    Update activity or activity segment with data from gpx file
    """
    activity.pauses = gpx_data['stop_time']
    activity.moving = gpx_data['moving_time']
    activity.min_alt = gpx_data['elevation_min']
    activity.max_alt = gpx_data['elevation_max']
    activity.descent = gpx_data['downhill']
    activity.ascent = gpx_data['uphill']
    activity.max_speed = gpx_data['max_speed']
    activity.ave_speed = gpx_data['average_speed']
    return activity


def create_activity(
    user: User, activity_data: Dict, gpx_data: Optional[Dict] = None
) -> Activity:
    """
    Create Activity from data entered by user and from gpx if a gpx file is
    provided
    """
    activity_date = (
        gpx_data['start']
        if gpx_data
        else datetime.strptime(
            activity_data['activity_date'], '%Y-%m-%d %H:%M'
        )
    )
    activity_date_tz, activity_date = get_datetime_with_tz(
        user.timezone, activity_date, gpx_data
    )

    duration = (
        gpx_data['duration']
        if gpx_data
        else timedelta(seconds=activity_data['duration'])
    )
    distance = gpx_data['distance'] if gpx_data else activity_data['distance']
    title = gpx_data['name'] if gpx_data else activity_data.get('title', '')

    new_activity = Activity(
        user_id=user.id,
        sport_id=activity_data['sport_id'],
        activity_date=activity_date,
        distance=distance,
        duration=duration,
    )
    new_activity.notes = activity_data.get('notes')

    if title is not None and title != '':
        new_activity.title = title
    else:
        sport = Sport.query.filter_by(id=new_activity.sport_id).first()
        fmt = "%Y-%m-%d %H:%M:%S"
        activity_datetime = (
            activity_date_tz.strftime(fmt)
            if activity_date_tz
            else new_activity.activity_date.strftime(fmt)
        )
        new_activity.title = f'{sport.label} - {activity_datetime}'

    if gpx_data:
        new_activity.gpx = gpx_data['filename']
        new_activity.bounds = gpx_data['bounds']
        update_activity_data(new_activity, gpx_data)
    else:
        new_activity.moving = duration
        new_activity.ave_speed = (
            None
            if duration.seconds == 0
            else float(new_activity.distance) / (duration.seconds / 3600)
        )
        new_activity.max_speed = new_activity.ave_speed
    return new_activity


def create_segment(
    activity_id: int, activity_uuid: UUID, segment_data: Dict
) -> ActivitySegment:
    """
    Create Activity Segment from gpx data
    """
    new_segment = ActivitySegment(
        activity_id=activity_id,
        activity_uuid=activity_uuid,
        segment_id=segment_data['idx'],
    )
    new_segment.duration = segment_data['duration']
    new_segment.distance = segment_data['distance']
    update_activity_data(new_segment, segment_data)
    return new_segment


def update_activity(activity: Activity) -> Activity:
    """
    Update activity data from gpx file
    """
    gpx_data, _, _ = get_gpx_info(
        get_absolute_file_path(activity.gpx), False, False
    )
    updated_activity = update_activity_data(activity, gpx_data)
    updated_activity.duration = gpx_data['duration']
    updated_activity.distance = gpx_data['distance']
    db.session.flush()

    for segment_idx, segment in enumerate(updated_activity.segments):
        segment_data = gpx_data['segments'][segment_idx]
        updated_segment = update_activity_data(segment, segment_data)
        updated_segment.duration = segment_data['duration']
        updated_segment.distance = segment_data['distance']
        db.session.flush()

    return updated_activity


def edit_activity(
    activity: Activity, activity_data: Dict, auth_user_id: int
) -> Activity:
    """
    Edit an activity
    Note: the gpx file is NOT modified

    In a next version, map_data and weather_data will be updated
    (case of a modified gpx file, see issue #7)
    """
    user = User.query.filter_by(id=auth_user_id).first()
    if activity_data.get('refresh'):
        activity = update_activity(activity)
    if activity_data.get('sport_id'):
        activity.sport_id = activity_data.get('sport_id')
    if activity_data.get('title'):
        activity.title = activity_data.get('title')
    if activity_data.get('notes'):
        activity.notes = activity_data.get('notes')
    if not activity.gpx:
        if activity_data.get('activity_date'):
            activity_date = datetime.strptime(
                activity_data['activity_date'], '%Y-%m-%d %H:%M'
            )
            _, activity.activity_date = get_datetime_with_tz(
                user.timezone, activity_date
            )

        if activity_data.get('duration'):
            activity.duration = timedelta(seconds=activity_data['duration'])
            activity.moving = activity.duration

        if activity_data.get('distance'):
            activity.distance = activity_data['distance']

        activity.ave_speed = (
            None
            if activity.duration.seconds == 0
            else float(activity.distance) / (activity.duration.seconds / 3600)
        )
        activity.max_speed = activity.ave_speed
    return activity


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
    activity_date: str,
    sport: str,
    old_filename: Optional[str] = None,
    extension: Optional[str] = None,
) -> str:
    """
    Generate a file path from user and activity data
    """
    if not extension and old_filename:
        extension = f".{old_filename.rsplit('.', 1)[1].lower()}"
    _, new_filename = tempfile.mkstemp(
        prefix=f'{activity_date}_{sport}_', suffix=extension
    )
    dir_path = os.path.join('activities', str(auth_user_id))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, new_filename.split('/')[-1])
    return file_path


def generate_map(map_filepath: str, map_data: List) -> None:
    """
    Generate and save map image from map data
    """
    m = StaticMap(400, 225, 10)
    line = Line(map_data, '#3388FF', 4)
    m.add_line(line)
    image = m.render()
    image.save(map_filepath)


def get_map_hash(map_filepath: str) -> str:
    """
    Generate a md5 hash used as id instead of activity id, to retrieve map
    image (maps are sensitive data)
    """
    md5 = hashlib.md5()
    absolute_map_filepath = get_absolute_file_path(map_filepath)
    with open(absolute_map_filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()


def process_one_gpx_file(params: Dict, filename: str) -> Activity:
    """
    Get all data from a gpx file to create an activity with map image
    """
    try:
        gpx_data, map_data, weather_data = get_gpx_info(params['file_path'])
        auth_user_id = params['user'].id
        new_filepath = get_new_file_path(
            auth_user_id=auth_user_id,
            activity_date=gpx_data['start'],
            old_filename=filename,
            sport=params['sport_label'],
        )
        absolute_gpx_filepath = get_absolute_file_path(new_filepath)
        os.rename(params['file_path'], absolute_gpx_filepath)
        gpx_data['filename'] = new_filepath

        map_filepath = get_new_file_path(
            auth_user_id=auth_user_id,
            activity_date=gpx_data['start'],
            extension='.png',
            sport=params['sport_label'],
        )
        absolute_map_filepath = get_absolute_file_path(map_filepath)
        generate_map(absolute_map_filepath, map_data)
    except (gpxpy.gpx.GPXXMLSyntaxException, TypeError) as e:
        raise ActivityException('error', 'Error during gpx file parsing.', e)
    except Exception as e:
        raise ActivityException('error', 'Error during gpx processing.', e)

    try:
        new_activity = create_activity(
            params['user'], params['activity_data'], gpx_data
        )
        new_activity.map = map_filepath
        new_activity.map_id = get_map_hash(map_filepath)
        new_activity.weather_start = weather_data[0]
        new_activity.weather_end = weather_data[1]
        db.session.add(new_activity)
        db.session.flush()

        for segment_data in gpx_data['segments']:
            new_segment = create_segment(
                new_activity.id, new_activity.uuid, segment_data
            )
            db.session.add(new_segment)
        db.session.commit()
        return new_activity
    except (exc.IntegrityError, ValueError) as e:
        raise ActivityException('fail', 'Error during activity save.', e)


def process_zip_archive(common_params: Dict, extract_dir: str) -> List:
    """
    Get files from a zip archive and create activities, if number of files
    does not exceed defined limit.
    """
    with zipfile.ZipFile(common_params['file_path'], "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    new_activities = []
    gpx_files_limit = os.getenv('REACT_APP_GPX_LIMIT_IMPORT', 10)
    if (
        gpx_files_limit
        and isinstance(gpx_files_limit, str)
        and gpx_files_limit.isdigit()
    ):
        gpx_files_limit = int(gpx_files_limit)
    else:
        gpx_files_limit = 10
        appLog.warning('GPX limit not configured, set to 10.')
    gpx_files_ok = 0

    for gpx_file in os.listdir(extract_dir):
        if (
            '.' in gpx_file
            and gpx_file.rsplit('.', 1)[1].lower()
            in current_app.config['ACTIVITY_ALLOWED_EXTENSIONS']
        ):
            gpx_files_ok += 1
            if gpx_files_ok > gpx_files_limit:
                break
            file_path = os.path.join(extract_dir, gpx_file)
            params = common_params
            params['file_path'] = file_path
            new_activity = process_one_gpx_file(params, gpx_file)
            new_activities.append(new_activity)

    return new_activities


def process_files(
    auth_user_id: int,
    activity_data: Dict,
    activity_file: FileStorage,
    folders: Dict,
) -> List:
    """
    Store gpx file or zip archive and create activities
    """
    if activity_file.filename is None:
        raise ActivityException('error', 'File has no filename.')
    filename = secure_filename(activity_file.filename)
    extension = f".{filename.rsplit('.', 1)[1].lower()}"
    file_path = get_file_path(folders['tmp_dir'], filename)
    sport = Sport.query.filter_by(id=activity_data.get('sport_id')).first()
    if not sport:
        raise ActivityException(
            'error',
            f"Sport id: {activity_data.get('sport_id')} does not exist",
        )
    user = User.query.filter_by(id=auth_user_id).first()

    common_params = {
        'user': user,
        'activity_data': activity_data,
        'file_path': file_path,
        'sport_label': sport.label,
    }

    try:
        activity_file.save(file_path)
    except Exception as e:
        raise ActivityException('error', 'Error during activity file save.', e)

    if extension == ".gpx":
        return [process_one_gpx_file(common_params, filename)]
    else:
        return process_zip_archive(common_params, folders['extract_dir'])


def get_upload_dir_size() -> int:
    """
    Return upload directory size
    """
    upload_path = get_absolute_file_path('')
    total_size = 0
    for dir_path, _, filenames in os.walk(upload_path):
        for f in filenames:
            fp = os.path.join(dir_path, f)
            total_size += os.path.getsize(fp)
    return total_size
