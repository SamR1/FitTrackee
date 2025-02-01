from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Generator, Iterator, List
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

from fittrackee import db
from fittrackee.workouts.models import (
    TITLE_MAX_CHARACTERS,
    Sport,
    Workout,
    WorkoutSegment,
)
from fittrackee.workouts.utils.maps import StaticMap

from ..utils import random_string

byte_io = BytesIO()
Image.new("RGB", (256, 256)).save(byte_io, "PNG")
byte_image = byte_io.getvalue()


@pytest.fixture(autouse=True)
def update_records_patch(request: pytest.FixtureRequest) -> Iterator[None]:
    # allows to disable record creation/update on tests where
    # records are not needed
    if "disable_autouse_update_records_patch" in request.keywords:
        yield
    else:
        with patch(
            "fittrackee.workouts.models.update_records", return_value=None
        ):
            yield


@pytest.fixture(scope="session", autouse=True)
def static_map_get_mock() -> Generator:
    # to avoid unnecessary requests calls through staticmap
    m = Mock(return_value=(200, byte_image))
    with patch.object(StaticMap, "get", m) as _fixture:
        yield _fixture


@pytest.fixture()
def sport_1_cycling() -> Sport:
    sport = Sport(label="Cycling (Sport)")
    db.session.add(sport)
    db.session.commit()
    return sport


@pytest.fixture()
def sport_1_cycling_inactive() -> Sport:
    sport = Sport(label="Cycling (Sport)")
    sport.is_active = False
    db.session.add(sport)
    db.session.commit()
    return sport


@pytest.fixture()
def sport_2_running() -> Sport:
    sport = Sport(label="Running")
    sport.stopped_speed_threshold = 0.1
    db.session.add(sport)
    db.session.commit()
    return sport


@pytest.fixture()
def sport_3_cycling_transport() -> Sport:
    sport = Sport(label="Cycling (Transport)")
    db.session.add(sport)
    db.session.commit()
    return sport


def update_workout(workout: Workout) -> None:
    distance = workout.distance if workout.distance else 0
    workout.ave_speed = float(distance) / (workout.duration.seconds / 3600)
    workout.max_speed = workout.ave_speed
    workout.moving = workout.duration


@pytest.fixture()
def workout_cycling_user_1() -> Workout:
    workout = Workout(
        user_id=1,
        sport_id=1,
        # workout_date: 'Mon, 01 Jan 2018 00:00:00 GMT'
        workout_date=datetime(2018, 1, 1, tzinfo=timezone.utc),
        distance=10,
        duration=timedelta(seconds=3600),
    )
    update_workout(workout)
    db.session.add(workout)
    db.session.commit()
    return workout


@pytest.fixture()
def another_workout_cycling_user_1() -> Workout:
    workout = Workout(
        user_id=1,
        sport_id=1,
        # workout_date: 'Mon, 01 Jan 2024 00:00:00 GMT'
        workout_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        distance=18,
        duration=timedelta(seconds=3600),
    )
    update_workout(workout)
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
    workout_segment.duration = timedelta(seconds=6000)
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
        # workout_date: 'Mon, 02 Apr 2018 00:00:00 GMT'
        workout_date=datetime(2018, 4, 2, tzinfo=timezone.utc),
        distance=12,
        duration=timedelta(seconds=6000),
    )
    update_workout(workout)
    db.session.add(workout)
    db.session.commit()
    return workout


@pytest.fixture()
def seven_workouts_user_1() -> List[Workout]:
    workouts = []
    workout_1 = Workout(
        user_id=1,
        sport_id=1,
        # workout_date: 'Sun, 2 Apr 2017 22:00:00 GMT'
        workout_date=datetime(2017, 4, 2, 22, tzinfo=timezone.utc),
        distance=5,
        duration=timedelta(seconds=1024),
    )
    workout_1.title = "Workout 1 of 7"
    update_workout(workout_1)
    workout_1.ascent = 120
    workout_1.descent = 200
    db.session.add(workout_1)
    db.session.flush()
    workouts.append(workout_1)

    workout_2 = Workout(
        user_id=1,
        sport_id=1,
        # workout_date: 'Sun, 31 Dec 2017 23:00:00 GMT'
        workout_date=datetime(2017, 12, 31, 23, tzinfo=timezone.utc),
        distance=10,
        duration=timedelta(seconds=3456),
    )
    workout_2.title = "Workout 2 of 7"
    update_workout(workout_2)
    workout_2.ascent = 100
    workout_2.descent = 80
    db.session.add(workout_2)
    db.session.flush()
    workouts.append(workout_2)

    workout_3 = Workout(
        user_id=1,
        sport_id=1,
        # workout_date: 'Mon, 01 Jan 2018 00:00:00 GMT'
        workout_date=datetime(2018, 1, 1, tzinfo=timezone.utc),
        distance=10,
        duration=timedelta(seconds=1024),
    )
    workout_3.title = "Workout 3 of 7"
    update_workout(workout_3)
    workout_3.ascent = 80
    workout_3.descent = 100
    db.session.add(workout_3)
    db.session.flush()
    workouts.append(workout_3)

    workout_4 = Workout(
        user_id=1,
        sport_id=1,
        # workout_date: 'Fri, 23 Feb 2018 10:00:00 GMT'
        workout_date=datetime(2018, 2, 23, 10, tzinfo=timezone.utc),
        distance=1,
        duration=timedelta(seconds=600),
    )
    workout_4.title = "Workout 4 of 7"
    update_workout(workout_4)
    workout_4.ascent = 120
    workout_4.descent = 180
    db.session.add(workout_4)
    db.session.flush()
    workouts.append(workout_4)

    workout_5 = Workout(
        user_id=1,
        sport_id=1,
        # workout_date: 'Fri, 23 Feb 2018 00:00:00 GMT'
        workout_date=datetime(2018, 2, 23, tzinfo=timezone.utc),
        distance=10,
        duration=timedelta(seconds=1000),
    )
    workout_5.title = "Workout 5 of 7"
    update_workout(workout_5)
    workout_5.ascent = 100
    workout_5.descent = 200
    db.session.add(workout_5)
    db.session.flush()
    workouts.append(workout_5)

    workout_6 = Workout(
        user_id=1,
        sport_id=1,
        # workout_date: 'Sun, 01 Apr 2018 00:00:00 GMT'
        workout_date=datetime(2018, 4, 1, tzinfo=timezone.utc),
        distance=8,
        duration=timedelta(seconds=6000),
    )
    workout_6.title = "Workout 6 of 7"
    update_workout(workout_6)
    workout_6.ascent = 40
    workout_6.descent = 20
    db.session.add(workout_6)
    db.session.flush()
    workouts.append(workout_6)

    distance = 10
    workout_7 = Workout(
        user_id=1,
        sport_id=1,
        # workout_date: 'Wed, 09 May 2018 00:00:00 GMT'
        workout_date=datetime(2018, 5, 9, tzinfo=timezone.utc),
        distance=distance,
        duration=timedelta(seconds=3600),
    )
    workout_7.title = "Workout 7 of 7"
    workout_7.moving = timedelta(seconds=3000)
    workout_7.ave_speed = float(distance) / (workout_7.moving.seconds / 3600)
    workout_7.max_speed = workout_7.ave_speed + 5
    db.session.add(workout_7)
    db.session.commit()
    workouts.append(workout_7)

    return workouts


@pytest.fixture()
def three_workouts_2025_user_1() -> List[Workout]:
    workouts = []
    for workout_date in [
        datetime(2025, 1, 1, tzinfo=timezone.utc),
        datetime(2025, 1, 5, tzinfo=timezone.utc),
        datetime(2025, 1, 6, tzinfo=timezone.utc),
    ]:
        workout = Workout(
            user_id=1,
            sport_id=1,
            workout_date=workout_date,
            distance=20,
            duration=timedelta(seconds=3600),
        )
        update_workout(workout)
        db.session.add(workout)
        workouts.append(workout)
        db.session.flush()
    db.session.commit()
    return workouts


@pytest.fixture()
def workout_cycling_user_2() -> Workout:
    workout = Workout(
        user_id=2,
        sport_id=1,
        # workout_date: 'Tue, 23 Jan 2018 00:00:00 GMT'
        workout_date=datetime(2018, 1, 23, tzinfo=timezone.utc),
        distance=15,
        duration=timedelta(seconds=3600),
    )
    update_workout(workout)
    db.session.add(workout)
    db.session.commit()
    return workout


track_points_part_1 = (
    '      <trkpt lat="44.68095" lon="6.07367">'
    "        <ele>998</ele>"
    "        <time>2018-03-13T12:44:45Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.68091" lon="6.07367">'
    "        <ele>998</ele>"
    "        <time>2018-03-13T12:44:50Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.6808" lon="6.07364">'
    "        <ele>994</ele>"
    "        <time>2018-03-13T12:45:00Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.68075" lon="6.07364">'
    "        <ele>994</ele>"
    "        <time>2018-03-13T12:45:05Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.68071" lon="6.07364">'
    "        <ele>994</ele>"
    "        <time>2018-03-13T12:45:10Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.68049" lon="6.07361">'
    "        <ele>993</ele>"
    "        <time>2018-03-13T12:45:30Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.68019" lon="6.07356">'
    "        <ele>992</ele>"
    "        <time>2018-03-13T12:45:55Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.68014" lon="6.07355">'
    "        <ele>992</ele>"
    "        <time>2018-03-13T12:46:00Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67995" lon="6.07358">'
    "        <ele>987</ele>"
    "        <time>2018-03-13T12:46:15Z</time>"
    "      </trkpt>"
)
track_points_part_2 = (
    '      <trkpt lat="44.67977" lon="6.07364">'
    "        <ele>987</ele>"
    "        <time>2018-03-13T12:46:30Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67972" lon="6.07367">'
    "        <ele>987</ele>"
    "        <time>2018-03-13T12:46:35Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67966" lon="6.07368">'
    "        <ele>987</ele>"
    "        <time>2018-03-13T12:46:40Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67961" lon="6.0737">'
    "        <ele>986</ele>"
    "        <time>2018-03-13T12:46:45Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67938" lon="6.07377">'
    "        <ele>986</ele>"
    "        <time>2018-03-13T12:47:05Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67933" lon="6.07381">'
    "        <ele>986</ele>"
    "        <time>2018-03-13T12:47:10Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67922" lon="6.07385">'
    "        <ele>985</ele>"
    "        <time>2018-03-13T12:47:20Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67911" lon="6.0739">'
    "        <ele>980</ele>"
    "        <time>2018-03-13T12:47:30Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.679" lon="6.07399">'
    "        <ele>980</ele>"
    "        <time>2018-03-13T12:47:40Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67896" lon="6.07402">'
    "        <ele>980</ele>"
    "        <time>2018-03-13T12:47:45Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67884" lon="6.07408">'
    "        <ele>979</ele>"
    "        <time>2018-03-13T12:47:55Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67863" lon="6.07423">'
    "        <ele>981</ele>"
    "        <time>2018-03-13T12:48:15Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67858" lon="6.07425">'
    "        <ele>980</ele>"
    "        <time>2018-03-13T12:48:20Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67842" lon="6.07434">'
    "        <ele>979</ele>"
    "        <time>2018-03-13T12:48:35Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67837" lon="6.07435">'
    "        <ele>979</ele>"
    "        <time>2018-03-13T12:48:40Z</time>"
    "      </trkpt>"
    '      <trkpt lat="44.67822" lon="6.07442">'
    "        <ele>975</ele>"
    "        <time>2018-03-13T12:48:55Z</time>"
    "      </trkpt>"
)


@pytest.fixture()
def gpx_file() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        "    <name>just a workout</name>"
        "    <trkseg>"
        + track_points_part_1
        + track_points_part_2
        + "    </trkseg>"
        "  </trk>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_wo_name() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        "    <trkseg>"
        + track_points_part_1
        + track_points_part_2
        + "    </trkseg>"
        "  </trk>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_with_description() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        "    <name>just a workout</name>"
        "    <desc>this is workout description</desc>"
        "    <trkseg>"
        + track_points_part_1
        + track_points_part_2
        + "    </trkseg>"
        "  </trk>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_with_empty_description() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        "    <name>just a workout</name>"
        "    <desc></desc>"
        "    <trkseg>"
        + track_points_part_1
        + track_points_part_2
        + "    </trkseg>"
        "  </trk>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_with_offset() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        "    <trkseg>"
        '      <trkpt lat="44.68095" lon="6.07367">'
        "        <ele>998</ele>"
        "        <time>2018-03-13T13:44:45+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68091" lon="6.07367">'
        "        <ele>998</ele>"
        "        <time>2018-03-13T13:44:50+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.6808" lon="6.07364">'
        "        <ele>994</ele>"
        "        <time>2018-03-13T13:45:00+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68075" lon="6.07364">'
        "        <ele>994</ele>"
        "        <time>2018-03-13T13:45:05+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68071" lon="6.07364">'
        "        <ele>994</ele>"
        "        <time>2018-03-13T13:45:10+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68049" lon="6.07361">'
        "        <ele>993</ele>"
        "        <time>2018-03-13T13:45:30+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68019" lon="6.07356">'
        "        <ele>992</ele>"
        "        <time>2018-03-13T13:45:55+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68014" lon="6.07355">'
        "        <ele>992</ele>"
        "        <time>2018-03-13T13:46:00+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67995" lon="6.07358">'
        "        <ele>987</ele>"
        "        <time>2018-03-13T13:46:15+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67977" lon="6.07364">'
        "        <ele>987</ele>"
        "        <time>2018-03-13T13:46:30+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67972" lon="6.07367">'
        "        <ele>987</ele>"
        "        <time>2018-03-13T13:46:35+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67966" lon="6.07368">'
        "        <ele>987</ele>"
        "        <time>2018-03-13T13:46:40+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67961" lon="6.0737">'
        "        <ele>986</ele>"
        "        <time>2018-03-13T13:46:45+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67938" lon="6.07377">'
        "        <ele>986</ele>"
        "        <time>2018-03-13T13:47:05+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67933" lon="6.07381">'
        "        <ele>986</ele>"
        "        <time>2018-03-13T13:47:10+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67922" lon="6.07385">'
        "        <ele>985</ele>"
        "        <time>2018-03-13T13:47:20+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67911" lon="6.0739">'
        "        <ele>980</ele>"
        "        <time>2018-03-13T13:47:30+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.679" lon="6.07399">'
        "        <ele>980</ele>"
        "        <time>2018-03-13T13:47:40+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67896" lon="6.07402">'
        "        <ele>980</ele>"
        "        <time>2018-03-13T13:47:45+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67884" lon="6.07408">'
        "        <ele>979</ele>"
        "        <time>2018-03-13T13:47:55+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67863" lon="6.07423">'
        "        <ele>981</ele>"
        "        <time>2018-03-13T13:48:15+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67858" lon="6.07425">'
        "        <ele>980</ele>"
        "        <time>2018-03-13T13:48:20+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67842" lon="6.07434">'
        "        <ele>979</ele>"
        "        <time>2018-03-13T13:48:35+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67837" lon="6.07435">'
        "        <ele>979</ele>"
        "        <time>2018-03-13T13:48:40+01:00</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67822" lon="6.07442">'
        "        <ele>975</ele>"
        "        <time>2018-03-13T13:48:55+01:00</time>"
        "      </trkpt>"
        "    </trkseg>"
        "  </trk>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_without_elevation() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        "    <name>just a workout</name>"
        "    <trkseg>"
        '      <trkpt lat="44.68095" lon="6.07367">'
        "        <time>2018-03-13T12:44:45Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68091" lon="6.07367">'
        "        <time>2018-03-13T12:44:50Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.6808" lon="6.07364">'
        "        <time>2018-03-13T12:45:00Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68075" lon="6.07364">'
        "        <time>2018-03-13T12:45:05Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68071" lon="6.07364">'
        "        <time>2018-03-13T12:45:10Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68049" lon="6.07361">'
        "        <time>2018-03-13T12:45:30Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68019" lon="6.07356">'
        "        <time>2018-03-13T12:45:55Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68014" lon="6.07355">'
        "        <time>2018-03-13T12:46:00Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67995" lon="6.07358">'
        "        <time>2018-03-13T12:46:15Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67977" lon="6.07364">'
        "        <time>2018-03-13T12:46:30Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67972" lon="6.07367">'
        "        <time>2018-03-13T12:46:35Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67966" lon="6.07368">'
        "        <time>2018-03-13T12:46:40Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67961" lon="6.0737">'
        "        <time>2018-03-13T12:46:45Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67938" lon="6.07377">'
        "        <time>2018-03-13T12:47:05Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67933" lon="6.07381">'
        "        <time>2018-03-13T12:47:10Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67922" lon="6.07385">'
        "        <time>2018-03-13T12:47:20Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67911" lon="6.0739">'
        "        <time>2018-03-13T12:47:30Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.679" lon="6.07399">'
        "        <time>2018-03-13T12:47:40Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67896" lon="6.07402">'
        "        <time>2018-03-13T12:47:45Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67884" lon="6.07408">'
        "        <time>2018-03-13T12:47:55Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67863" lon="6.07423">'
        "        <time>2018-03-13T12:48:15Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67858" lon="6.07425">'
        "        <time>2018-03-13T12:48:20Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67842" lon="6.07434">'
        "        <time>2018-03-13T12:48:35Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67837" lon="6.07435">'
        "        <time>2018-03-13T12:48:40Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67822" lon="6.07442">'
        "        <time>2018-03-13T12:48:55Z</time>"
        "      </trkpt>"
        "    </trkseg>"
        "  </trk>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_w_title_exceeding_limit() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        f"    <name>{random_string(TITLE_MAX_CHARACTERS + 1)}</name>"
        "    <trkseg>"
        + track_points_part_1
        + track_points_part_2
        + "    </trkseg>"
        + "  </trk>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_wo_track() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_invalid_xml() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        "    <name>just a workout</name>"
    )


@pytest.fixture()
def gpx_file_without_time() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        "    <name>just a workout</name>"
        "    <trkseg>"
        '      <trkpt lat="44.68095" lon="6.07367">'
        "        <ele>998</ele>"
        "      </trkpt>"
        '      <trkpt lat="44.68091" lon="6.07367">'
        "        <ele>998</ele>"
        "      </trkpt>"
        '      <trkpt lat="44.6808" lon="6.07364">'
        "        <ele>994</ele>"
        "      </trkpt>"
        '      <trkpt lat="44.68075" lon="6.07364">'
        "        <ele>994</ele>"
        "      </trkpt>"
        '      <trkpt lat="44.68071" lon="6.07364">'
        "        <ele>994</ele>"
        "      </trkpt>"
        '      <trkpt lat="44.68049" lon="6.07361">'
        "        <ele>993</ele>"
        "      </trkpt>"
        '      <trkpt lat="44.68019" lon="6.07356">'
        "        <ele>992</ele>"
        "      </trkpt>"
        '      <trkpt lat="44.68014" lon="6.07355">'
        "        <ele>992</ele>"
        "      </trkpt>"
        '      <trkpt lat="44.67995" lon="6.07358">'
        "        <ele>987</ele>"
        "      </trkpt>"
        '      <trkpt lat="44.67977" lon="6.07364">'
        "        <ele>987</ele>"
        "      </trkpt>"
        '      <trkpt lat="44.67972" lon="6.07367">'
        "        <ele>987</ele>"
        "      </trkpt>"
        "    </trkseg>"
        "  </trk>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_with_segments() -> str:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        "    <name>just a workout</name>"
        "    <trkseg>" + track_points_part_1 + "    </trkseg>"
        "    <trkseg>" + track_points_part_2 + "    </trkseg>"
        "  </trk>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_with_3_segments() -> str:
    """60 seconds between each segment"""
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        "  <metadata/>"
        "  <trk>"
        "    <name>just a workout</name>"
        "    <trkseg>"
        '      <trkpt lat="44.68095" lon="6.07367">'
        "        <ele>998</ele>"
        "        <time>2018-03-13T12:44:50Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.68091" lon="6.07367">'
        "        <ele>998</ele>"
        "        <time>2018-03-13T12:44:55Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.6808" lon="6.07364">'
        "        <ele>994</ele>"
        "        <time>2018-03-13T12:45:00Z</time>"
        "      </trkpt>"
        "    </trkseg>"
        "    <trkseg>"
        '      <trkpt lat="44.67972" lon="6.07367">'
        "        <ele>987</ele>"
        "        <time>2018-03-13T12:46:00Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67966" lon="6.07368">'
        "        <ele>987</ele>"
        "        <time>2018-03-13T12:46:05Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67961" lon="6.0737">'
        "        <ele>986</ele>"
        "        <time>2018-03-13T12:46:10Z</time>"
        "      </trkpt>"
        "    </trkseg>"
        "    <trkseg>"
        '      <trkpt lat="44.67858" lon="6.07425">'
        "        <ele>980</ele>"
        "        <time>2018-03-13T12:47:10Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67842" lon="6.07434">'
        "        <ele>979</ele>"
        "        <time>2018-03-13T12:47:15Z</time>"
        "      </trkpt>"
        '      <trkpt lat="44.67837" lon="6.07435">'
        "        <ele>979</ele>"
        "        <time>2018-03-13T12:47:20Z</time>"
        "      </trkpt>"
        "    </trkseg>"
        "  </trk>"
        "</gpx>"
    )


@pytest.fixture()
def gpx_file_storage(gpx_file: str) -> FileStorage:
    return FileStorage(
        filename=f"{uuid4().hex}.gpx", stream=BytesIO(str.encode(gpx_file))
    )
