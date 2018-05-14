import os
import tempfile
from datetime import datetime, timedelta

import gpxpy.gpx
from flask import current_app
from mpwo_api import appLog
from werkzeug.utils import secure_filename

from .models import Activity, ActivitySegment, Sport


def update_activity_data(activity, gpx_data):
    """activity could be a complete activity or an activity segment"""
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
        auth_user_id, activity_data, gpx_data=None
):
    activity_date = gpx_data['start'] if gpx_data else datetime.strptime(
        activity_data.get('activity_date'), '%Y-%m-%d %H:%M')
    duration = gpx_data['duration'] if gpx_data \
        else timedelta(seconds=activity_data.get('duration'))
    distance = gpx_data['distance'] if gpx_data \
        else activity_data.get('distance')
    title = gpx_data['name'] if gpx_data \
        else activity_data.get('title')

    new_activity = Activity(
        user_id=auth_user_id,
        sport_id=activity_data.get('sport_id'),
        activity_date=activity_date,
        distance=distance,
        duration=duration
    )

    if title is not None:
        new_activity.title = title
    else:
        sport = Sport.query.filter_by(id=new_activity.sport_id).first()
        new_activity.title = '{} - {}'.format(sport.label,
                                              new_activity.activity_date)

    if gpx_data:
        new_activity.gpx = gpx_data['filename']
        new_activity.bounds = gpx_data['bounds']
        update_activity_data(new_activity, gpx_data)
    else:
        new_activity.moving = duration
        new_activity.ave_speed = new_activity.distance / (
            duration.seconds / 3600)
        new_activity.max_speed = new_activity.ave_speed
    return new_activity


def create_segment(activity_id, segment_data):
    new_segment = ActivitySegment(
        activity_id=activity_id,
        segment_id=segment_data['idx']
    )
    new_segment.duration = segment_data['duration']
    new_segment.distance = segment_data['distance']
    update_activity_data(new_segment, segment_data)
    return new_segment


def edit_activity(activity, activity_data):
    activity.sport_id = activity_data.get('sport_id')
    if activity_data.get('title'):
        activity.title = activity_data.get('title')
    if not activity.gpx:
        if activity_data.get('activity_date'):
            activity.activity_date = datetime.strptime(
                activity_data.get('activity_date'), '%Y-%m-%d %H:%M')
        if activity_data.get('duration'):
            activity.duration = timedelta(
                seconds=activity_data.get('duration'))
            activity.moving = activity.duration
        if activity_data.get('distance'):
            activity.distance = activity_data.get('distance')
        activity.ave_speed = activity.distance / (
            activity.duration.seconds / 3600)
        activity.max_speed = activity.ave_speed
    return activity


def get_gpx_data(parsed_gpx, max_speed, start):
    gpx_data = {'max_speed': (max_speed / 1000) * 3600, 'start': start}

    duration = parsed_gpx.get_duration()
    gpx_data['duration'] = timedelta(seconds=duration)

    ele = parsed_gpx.get_elevation_extremes()
    gpx_data['elevation_max'] = ele.maximum
    gpx_data['elevation_min'] = ele.minimum

    hill = parsed_gpx.get_uphill_downhill()
    gpx_data['uphill'] = hill.uphill
    gpx_data['downhill'] = hill.downhill

    mv = parsed_gpx.get_moving_data()
    gpx_data['moving_time'] = timedelta(seconds=mv.moving_time)
    gpx_data['stop_time'] = timedelta(seconds=mv.stopped_time)
    distance = mv.moving_distance + mv.stopped_distance
    gpx_data['distance'] = distance / 1000

    average_speed = distance / mv.moving_time
    gpx_data['average_speed'] = (average_speed / 1000) * 3600

    return gpx_data


def get_gpx_info(gpx_file):
    gpx_file = open(gpx_file, 'r')

    try:
        gpx = gpxpy.parse(gpx_file)
    except gpxpy.gpx.GPXXMLSyntaxException as e:
        appLog.error(e)
        return None

    # handle only one track per file
    if len(gpx.tracks) == 0:
        return None

    gpx_data = {
        'name': gpx.tracks[0].name,
        'segments': []
    }
    max_speed = 0
    start = 0

    for segment_idx, segment in enumerate(gpx.tracks[0].segments):
        segment_max_speed = 0
        segment_start = 0
        for point_idx, point in enumerate(segment.points):
            if point_idx == 0:
                segment_start = point.time
                if start == 0:
                    start = segment_start
            segment_speed = segment.get_speed(point_idx)
            if segment_speed > segment_max_speed:
                segment_max_speed = segment_speed
            if segment_max_speed > max_speed:
                max_speed = segment_max_speed

        segment_data = get_gpx_data(
            segment, segment_max_speed, segment_start
        )
        segment_data['idx'] = segment_idx
        gpx_data['segments'].append(segment_data)

    gull_gpx_data = get_gpx_data(gpx, max_speed, start)
    gpx_data = {**gpx_data, **gull_gpx_data}
    bounds = gpx.get_bounds()
    gpx_data['bounds'] = [
        bounds.min_latitude,
        bounds.min_longitude,
        bounds.max_latitude,
        bounds.max_longitude
    ]

    return gpx_data


def get_file_path(auth_user_id, activity_file):
    filename = secure_filename(activity_file.filename)
    dir_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'activities',
        str(auth_user_id),
        'tmp')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, filename)
    return file_path


def get_new_file_path(auth_user_id, activity_date, activity_file, sport):
    old_filename = secure_filename(activity_file.filename)
    extension = '.{}'.format(old_filename.rsplit('.', 1)[1].lower())
    _, new_filename = tempfile.mkstemp(
        prefix='{}_{}_'.format(activity_date, sport),
        suffix=extension
    )
    dir_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'], 'activities', str(auth_user_id))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path,
                             new_filename.replace('/tmp/', ''))
    return file_path
