import datetime
from io import BytesIO
from typing import Generator
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

from fittrackee import db
from fittrackee.workouts.models import Sport, Workout, WorkoutSegment
from fittrackee.workouts.utils import StaticMap

byte_io = BytesIO()
Image.new('RGB', (256, 256)).save(byte_io, 'PNG')
byte_image = byte_io.getvalue()


@pytest.fixture(scope='session', autouse=True)
def static_map_get_mock() -> Generator:
    # to avoid unnecessary requests calls through staticmap
    m = Mock(return_value=(200, byte_image))
    with patch.object(StaticMap, 'get', m) as _fixture:
        yield _fixture


@pytest.fixture()
def sport_1_cycling() -> Sport:
    sport = Sport(label='Cycling')
    db.session.add(sport)
    db.session.commit()
    return sport


@pytest.fixture()
def sport_1_cycling_inactive() -> Sport:
    sport = Sport(label='Cycling')
    sport.is_active = False
    db.session.add(sport)
    db.session.commit()
    return sport


@pytest.fixture()
def sport_2_running() -> Sport:
    sport = Sport(label='Running')
    sport.stopped_speed_threshold = 0.1
    db.session.add(sport)
    db.session.commit()
    return sport


@pytest.fixture()
def workout_cycling_user_1() -> Workout:
    workout = Workout(
        user_id=1,
        sport_id=1,
        workout_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=3600),
    )
    workout.max_speed = 10
    workout.ave_speed = 10
    workout.moving = workout.duration
    db.session.add(workout)
    db.session.commit()
    return workout


@pytest.fixture()
def workout_cycling_user_1_segment(
    workout_cycling_user_1: Workout,
) -> WorkoutSegment:
    workout_segment = WorkoutSegment(
        workout_id=workout_cycling_user_1.id,
        workout_uuid=workout_cycling_user_1.uuid,
        segment_id=0,
    )
    workout_segment.duration = datetime.timedelta(seconds=6000)
    workout_segment.moving = workout_segment.duration
    workout_segment.distance = 5
    db.session.add(workout_segment)
    db.session.commit()
    return workout_segment


@pytest.fixture()
def workout_running_user_1() -> Workout:
    workout = Workout(
        user_id=1,
        sport_id=2,
        workout_date=datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        distance=12,
        duration=datetime.timedelta(seconds=6000),
    )
    workout.moving = workout.duration
    db.session.add(workout)
    db.session.commit()
    return workout


@pytest.fixture()
def seven_workouts_user_1() -> Workout:
    workout = Workout(
        user_id=1,
        sport_id=1,
        workout_date=datetime.datetime.strptime('20/03/2017', '%d/%m/%Y'),
        distance=5,
        duration=datetime.timedelta(seconds=1024),
    )
    workout.ave_speed = float(workout.distance) / (1024 / 3600)
    workout.moving = workout.duration
    workout.ascent = 120
    workout.descent = 200
    db.session.add(workout)
    db.session.flush()

    workout = Workout(
        user_id=1,
        sport_id=1,
        workout_date=datetime.datetime.strptime('01/06/2017', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=3456),
    )
    workout.ave_speed = float(workout.distance) / (3456 / 3600)
    workout.moving = workout.duration
    workout.ascent = 100
    workout.descent = 80
    db.session.add(workout)
    db.session.flush()

    workout = Workout(
        user_id=1,
        sport_id=1,
        workout_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024),
    )
    workout.ave_speed = float(workout.distance) / (1024 / 3600)
    workout.moving = workout.duration
    workout.ascent = 80
    workout.descent = 100
    db.session.add(workout)
    db.session.flush()

    workout = Workout(
        user_id=1,
        sport_id=1,
        workout_date=datetime.datetime.strptime('23/02/2018', '%d/%m/%Y'),
        distance=1,
        duration=datetime.timedelta(seconds=600),
    )
    workout.ave_speed = float(workout.distance) / (600 / 3600)
    workout.moving = workout.duration
    workout.ascent = 120
    workout.descent = 180
    db.session.add(workout)
    db.session.flush()

    workout = Workout(
        user_id=1,
        sport_id=1,
        workout_date=datetime.datetime.strptime('23/02/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1000),
    )
    workout.ave_speed = float(workout.distance) / (1000 / 3600)
    workout.moving = workout.duration
    workout.ascent = 100
    workout.descent = 200
    db.session.add(workout)
    db.session.flush()

    workout = Workout(
        user_id=1,
        sport_id=1,
        workout_date=datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        distance=8,
        duration=datetime.timedelta(seconds=6000),
    )
    workout.ave_speed = float(workout.distance) / (6000 / 3600)
    workout.moving = workout.duration
    workout.ascent = 40
    workout.descent = 20
    db.session.add(workout)
    db.session.flush()

    workout = Workout(
        user_id=1,
        sport_id=1,
        workout_date=datetime.datetime.strptime('09/05/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=3000),
    )
    workout.ave_speed = float(workout.distance) / (3000 / 3600)
    workout.moving = workout.duration
    db.session.add(workout)
    db.session.commit()
    return workout


@pytest.fixture()
def workout_cycling_user_2() -> Workout:
    workout = Workout(
        user_id=2,
        sport_id=1,
        workout_date=datetime.datetime.strptime('23/01/2018', '%d/%m/%Y'),
        distance=15,
        duration=datetime.timedelta(seconds=3600),
    )
    workout.moving = workout.duration
    db.session.add(workout)
    db.session.commit()
    return workout


@pytest.fixture()
def gpx_file() -> str:
    return (
        '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        '  <metadata/>'
        '  <trk>'
        '    <name>just a workout</name>'
        '    <trkseg>'
        '      <trkpt lat="44.68095" lon="6.07367">'
        '        <ele>998</ele>'
        '        <time>2018-03-13T12:44:45Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68091" lon="6.07367">'
        '        <ele>998</ele>'
        '        <time>2018-03-13T12:44:50Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.6808" lon="6.07364">'
        '        <ele>994</ele>'
        '        <time>2018-03-13T12:45:00Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68075" lon="6.07364">'
        '        <ele>994</ele>'
        '        <time>2018-03-13T12:45:05Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68071" lon="6.07364">'
        '        <ele>994</ele>'
        '        <time>2018-03-13T12:45:10Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68049" lon="6.07361">'
        '        <ele>993</ele>'
        '        <time>2018-03-13T12:45:30Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68019" lon="6.07356">'
        '        <ele>992</ele>'
        '        <time>2018-03-13T12:45:55Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68014" lon="6.07355">'
        '        <ele>992</ele>'
        '        <time>2018-03-13T12:46:00Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67995" lon="6.07358">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:15Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67977" lon="6.07364">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:30Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67972" lon="6.07367">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:35Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67966" lon="6.07368">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:40Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67961" lon="6.0737">'
        '        <ele>986</ele>'
        '        <time>2018-03-13T12:46:45Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67938" lon="6.07377">'
        '        <ele>986</ele>'
        '        <time>2018-03-13T12:47:05Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67933" lon="6.07381">'
        '        <ele>986</ele>'
        '        <time>2018-03-13T12:47:10Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67922" lon="6.07385">'
        '        <ele>985</ele>'
        '        <time>2018-03-13T12:47:20Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67911" lon="6.0739">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:47:30Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.679" lon="6.07399">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:47:40Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67896" lon="6.07402">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:47:45Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67884" lon="6.07408">'
        '        <ele>979</ele>'
        '        <time>2018-03-13T12:47:55Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67863" lon="6.07423">'
        '        <ele>981</ele>'
        '        <time>2018-03-13T12:48:15Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67858" lon="6.07425">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:48:20Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67842" lon="6.07434">'
        '        <ele>979</ele>'
        '        <time>2018-03-13T12:48:35Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67837" lon="6.07435">'
        '        <ele>979</ele>'
        '        <time>2018-03-13T12:48:40Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67822" lon="6.07442">'
        '        <ele>975</ele>'
        '        <time>2018-03-13T12:48:55Z</time>'
        '      </trkpt>'
        '    </trkseg>'
        '  </trk>'
        '</gpx>'
    )


@pytest.fixture()
def gpx_file_wo_name() -> str:
    return (
        '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        '  <metadata/>'
        '  <trk>'
        '    <trkseg>'
        '      <trkpt lat="44.68095" lon="6.07367">'
        '        <ele>998</ele>'
        '        <time>2018-03-13T12:44:45Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68091" lon="6.07367">'
        '        <ele>998</ele>'
        '        <time>2018-03-13T12:44:50Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.6808" lon="6.07364">'
        '        <ele>994</ele>'
        '        <time>2018-03-13T12:45:00Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68075" lon="6.07364">'
        '        <ele>994</ele>'
        '        <time>2018-03-13T12:45:05Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68071" lon="6.07364">'
        '        <ele>994</ele>'
        '        <time>2018-03-13T12:45:10Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68049" lon="6.07361">'
        '        <ele>993</ele>'
        '        <time>2018-03-13T12:45:30Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68019" lon="6.07356">'
        '        <ele>992</ele>'
        '        <time>2018-03-13T12:45:55Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68014" lon="6.07355">'
        '        <ele>992</ele>'
        '        <time>2018-03-13T12:46:00Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67995" lon="6.07358">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:15Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67977" lon="6.07364">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:30Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67972" lon="6.07367">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:35Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67966" lon="6.07368">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:40Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67961" lon="6.0737">'
        '        <ele>986</ele>'
        '        <time>2018-03-13T12:46:45Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67938" lon="6.07377">'
        '        <ele>986</ele>'
        '        <time>2018-03-13T12:47:05Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67933" lon="6.07381">'
        '        <ele>986</ele>'
        '        <time>2018-03-13T12:47:10Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67922" lon="6.07385">'
        '        <ele>985</ele>'
        '        <time>2018-03-13T12:47:20Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67911" lon="6.0739">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:47:30Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.679" lon="6.07399">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:47:40Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67896" lon="6.07402">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:47:45Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67884" lon="6.07408">'
        '        <ele>979</ele>'
        '        <time>2018-03-13T12:47:55Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67863" lon="6.07423">'
        '        <ele>981</ele>'
        '        <time>2018-03-13T12:48:15Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67858" lon="6.07425">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:48:20Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67842" lon="6.07434">'
        '        <ele>979</ele>'
        '        <time>2018-03-13T12:48:35Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67837" lon="6.07435">'
        '        <ele>979</ele>'
        '        <time>2018-03-13T12:48:40Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67822" lon="6.07442">'
        '        <ele>975</ele>'
        '        <time>2018-03-13T12:48:55Z</time>'
        '      </trkpt>'
        '    </trkseg>'
        '  </trk>'
        '</gpx>'
    )


@pytest.fixture()
def gpx_file_wo_track() -> str:
    return (
        '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        '  <metadata/>'
        '</gpx>'
    )


@pytest.fixture()
def gpx_file_invalid_xml() -> str:
    return (
        '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        '  <metadata/>'
    )


@pytest.fixture()
def gpx_file_with_segments() -> str:
    return (
        '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        '  <metadata/>'
        '  <trk>'
        '    <name>just a workout</name>'
        '    <trkseg>'
        '      <trkpt lat="44.68095" lon="6.07367">'
        '        <ele>998</ele>'
        '        <time>2018-03-13T12:44:45Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68091" lon="6.07367">'
        '        <ele>998</ele>'
        '        <time>2018-03-13T12:44:50Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.6808" lon="6.07364">'
        '        <ele>994</ele>'
        '        <time>2018-03-13T12:45:00Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68075" lon="6.07364">'
        '        <ele>994</ele>'
        '        <time>2018-03-13T12:45:05Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68071" lon="6.07364">'
        '        <ele>994</ele>'
        '        <time>2018-03-13T12:45:10Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68049" lon="6.07361">'
        '        <ele>993</ele>'
        '        <time>2018-03-13T12:45:30Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68019" lon="6.07356">'
        '        <ele>992</ele>'
        '        <time>2018-03-13T12:45:55Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.68014" lon="6.07355">'
        '        <ele>992</ele>'
        '        <time>2018-03-13T12:46:00Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67995" lon="6.07358">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:15Z</time>'
        '      </trkpt>'
        '    </trkseg>'
        '    <trkseg>'
        '      <trkpt lat="44.67977" lon="6.07364">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:30Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67972" lon="6.07367">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:35Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67966" lon="6.07368">'
        '        <ele>987</ele>'
        '        <time>2018-03-13T12:46:40Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67961" lon="6.0737">'
        '        <ele>986</ele>'
        '        <time>2018-03-13T12:46:45Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67938" lon="6.07377">'
        '        <ele>986</ele>'
        '        <time>2018-03-13T12:47:05Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67933" lon="6.07381">'
        '        <ele>986</ele>'
        '        <time>2018-03-13T12:47:10Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67922" lon="6.07385">'
        '        <ele>985</ele>'
        '        <time>2018-03-13T12:47:20Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67911" lon="6.0739">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:47:30Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.679" lon="6.07399">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:47:40Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67896" lon="6.07402">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:47:45Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67884" lon="6.07408">'
        '        <ele>979</ele>'
        '        <time>2018-03-13T12:47:55Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67863" lon="6.07423">'
        '        <ele>981</ele>'
        '        <time>2018-03-13T12:48:15Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67858" lon="6.07425">'
        '        <ele>980</ele>'
        '        <time>2018-03-13T12:48:20Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67842" lon="6.07434">'
        '        <ele>979</ele>'
        '        <time>2018-03-13T12:48:35Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67837" lon="6.07435">'
        '        <ele>979</ele>'
        '        <time>2018-03-13T12:48:40Z</time>'
        '      </trkpt>'
        '      <trkpt lat="44.67822" lon="6.07442">'
        '        <ele>975</ele>'
        '        <time>2018-03-13T12:48:55Z</time>'
        '      </trkpt>'
        '    </trkseg>'
        '  </trk>'
        '</gpx>'
    )


@pytest.fixture()
def gpx_file_storage(gpx_file: str) -> FileStorage:
    return FileStorage(
        filename=f'{uuid4().hex}.gpx', stream=BytesIO(str.encode(gpx_file))
    )
