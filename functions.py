# #/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import yaml
import hashlib
import gpxpy.gpx

with open('param.yml', 'r') as stream:
    try:
        param = yaml.load(stream)
    except yaml.YAMLError as e:
        print(e)

# Hash
# -------------------------
def hash(word):
    hashword = hashlib.sha256(word.encode('utf-8')).hexdigest()
    return hashword




# GPX functions
# -------------------------
def gpx_info(gpx_file):

    gpx_data = {'filename': gpx_file}

    gpx_file = open(gpx_file, 'r')
    gpx = gpxpy.parse(gpx_file)

    maxspeed = 0

    for track in gpx.tracks:
        for segment in track.segments:
            for point_idx, point in enumerate(segment.points):
                if point_idx == 0:
                    start = point.time
                speed = segment.get_speed(point_idx)
                try:
                    if speed > maxspeed:
                        maxspeed = speed
                except:
                    pass

    gpx_data['maxspeed'] = str('%.2f km/h' % ((maxspeed / 1000) * 3600))
    gpx_data['start'] = start

    duration = gpx.get_duration()
    gpx_data['duration'] = time.strftime('%Hh:%Mm:%Ss', time.gmtime(duration))

    ele = gpx.get_elevation_extremes()
    gpx_data['elevationmax'] = str('%.2f m' % ele.maximum)
    gpx_data['elevationmin'] = str('%.2f m' % ele.minimum)

    hill = gpx.get_uphill_downhill()
    gpx_data['uphill'] = str('%.2f m' % hill.uphill)
    gpx_data['downhill'] = str('%.2f m' % hill.downhill)

    mv = gpx.get_moving_data()
    gpx_data['movingtime'] = time.strftime('%Hh %Mm %Ss', time.gmtime(mv.moving_time))
    gpx_data['stoptime'] = time.strftime('%Hh %Mm %Ss', time.gmtime(mv.stopped_time))
    distance = mv.moving_distance + mv.stopped_distance
    gpx_data['distance'] = str('%.2f km' % (distance/1000))

    averagespeed = distance / duration
    gpx_data['averagespeed'] = str('%.2f km/h' % ((averagespeed / 1000) * 3600))

    return gpx_data




