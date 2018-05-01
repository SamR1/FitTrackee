import gpxpy.gpx


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
