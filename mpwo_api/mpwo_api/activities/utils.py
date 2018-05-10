import os
from datetime import datetime, timedelta

import gpxpy.gpx
from flask import current_app
from werkzeug.utils import secure_filename

from .models import Activity


def create_activity(
        auth_user_id, activity_data, gpx_data=None, file_path=None
):
    activity_date = gpx_data['start'] if gpx_data else datetime.strptime(
        activity_data.get('activity_date'), '%Y-%m-%d %H:%M')
    duration = timedelta(seconds=gpx_data['duration']) if gpx_data \
        else timedelta(seconds=activity_data.get('duration'))

    new_activity = Activity(
        user_id=auth_user_id,
        sport_id=activity_data.get('sport_id'),
        activity_date=activity_date,
        duration=duration
    )

    if gpx_data:
        new_activity.gpx = file_path
        new_activity.pauses = timedelta(seconds=gpx_data['stop_time'])
        new_activity.moving = timedelta(seconds=gpx_data['moving_time'])
        new_activity.distance = gpx_data['distance']
        new_activity.min_alt = gpx_data['elevation_min']
        new_activity.max_alt = gpx_data['elevation_max']
        new_activity.descent = gpx_data['downhill']
        new_activity.ascent = gpx_data['uphill']
        new_activity.max_speed = gpx_data['max_speed']
        new_activity.ave_speed = gpx_data['average_speed']
    else:
        new_activity.moving = duration
        new_activity.distance = activity_data.get('distance')
        new_activity.ave_speed = new_activity.distance / (
            duration.seconds / 3600)
        new_activity.max_speed = new_activity.ave_speed
    return new_activity


def edit_activity_wo_gpx(activity, activity_data):
    activity.sport_id = activity_data.get('sport_id')
    activity.activity_date = datetime.strptime(
            activity_data.get('activity_date'), '%Y-%m-%d %H:%M')
    activity.duration = timedelta(seconds=activity_data.get('duration'))
    activity.moving = activity.duration
    activity.distance = activity_data.get('distance')
    activity.ave_speed = activity.distance / (
        activity.duration.seconds / 3600)
    activity.max_speed = activity.ave_speed
    return activity


def get_gpx_info(gpx_file):

    gpx_data = {'filename': gpx_file}

    gpx_file = open(gpx_file, 'r')
    gpx = gpxpy.parse(gpx_file)

    max_speed = 0
    start = 0

    for track in gpx.tracks:
        for segment in track.segments:
            for point_idx, point in enumerate(segment.points):
                if point_idx == 0:
                    start = point.time
                speed = segment.get_speed(point_idx)
                try:
                    if speed > max_speed:
                        max_speed = speed
                except Exception:
                    pass

    gpx_data['max_speed'] = (max_speed / 1000) * 3600
    gpx_data['start'] = start

    duration = gpx.get_duration()
    gpx_data['duration'] = duration

    ele = gpx.get_elevation_extremes()
    gpx_data['elevation_max'] = ele.maximum
    gpx_data['elevation_min'] = ele.minimum

    hill = gpx.get_uphill_downhill()
    gpx_data['uphill'] = hill.uphill
    gpx_data['downhill'] = hill.downhill

    mv = gpx.get_moving_data()
    gpx_data['moving_time'] = mv.moving_time
    gpx_data['stop_time'] = mv.stopped_time
    distance = mv.moving_distance + mv.stopped_distance
    gpx_data['distance'] = distance/1000

    average_speed = distance / duration
    gpx_data['average_speed'] = (average_speed / 1000) * 3600

    return gpx_data


def get_file_path(auth_user_id, activity_file):
    filename = secure_filename(activity_file.filename)
    dir_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'], 'activities', str(auth_user_id))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, filename)
    return file_path
