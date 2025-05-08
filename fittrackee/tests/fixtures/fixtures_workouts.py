import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Generator, Iterator, List
from unittest.mock import MagicMock, Mock, patch
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
from fittrackee.workouts.services.workout_from_file.base_workout_with_segment_service import (
    StaticMap,
)

from ..utils import random_string

byte_io = BytesIO()
Image.new("RGB", (256, 256)).save(byte_io, "PNG")
byte_image = byte_io.getvalue()


@dataclass
class DramatiqMessage:
    message_id: str


MESSAGE_ID = "e7640357-3b8d-47be-885d-68104cdfe4b2"
message = DramatiqMessage(message_id=MESSAGE_ID)


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


@pytest.fixture()
def sport_4_paragliding() -> Sport:
    sport = Sport(label="Paragliding")
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


track_points_part_1_coordinates = [
    (6.07367, 44.68095),
    (6.07367, 44.68091),
    (6.07364, 44.6808),
    (6.07364, 44.68075),
    (6.07364, 44.68071),
    (6.07361, 44.68049),
    (6.07356, 44.68019),
    (6.07355, 44.68014),
    (6.07358, 44.67995),
]
track_points_part_2_coordinates = [
    (6.07364, 44.67977),
    (6.07367, 44.67972),
    (6.07368, 44.67966),
    (6.0737, 44.67961),
    (6.07377, 44.67938),
    (6.07381, 44.67933),
    (6.07385, 44.67922),
    (6.0739, 44.67911),
    (6.07399, 44.679),
    (6.07402, 44.67896),
    (6.07408, 44.67884),
    (6.07423, 44.67863),
    (6.07425, 44.67858),
    (6.07434, 44.67842),
    (6.07435, 44.67837),
    (6.07442, 44.67822),
]


track_points_part_1 = """
           <trkpt lat="44.68095" lon="6.07367">
             <ele>998</ele>
             <time>2018-03-13T12:44:45Z</time>
           </trkpt>
           <trkpt lat="44.68091" lon="6.07367">
             <ele>998</ele>
             <time>2018-03-13T12:44:50Z</time>
           </trkpt>
           <trkpt lat="44.6808" lon="6.07364">
             <ele>994</ele>
             <time>2018-03-13T12:45:00Z</time>
           </trkpt>
           <trkpt lat="44.68075" lon="6.07364">
             <ele>994</ele>
             <time>2018-03-13T12:45:05Z</time>
           </trkpt>
           <trkpt lat="44.68071" lon="6.07364">
             <ele>994</ele>
             <time>2018-03-13T12:45:10Z</time>
           </trkpt>
           <trkpt lat="44.68049" lon="6.07361">
             <ele>993</ele>
             <time>2018-03-13T12:45:30Z</time>
           </trkpt>
           <trkpt lat="44.68019" lon="6.07356">
             <ele>992</ele>
             <time>2018-03-13T12:45:55Z</time>
           </trkpt>
           <trkpt lat="44.68014" lon="6.07355">
             <ele>992</ele>
             <time>2018-03-13T12:46:00Z</time>
           </trkpt>
           <trkpt lat="44.67995" lon="6.07358">
             <ele>987</ele>
             <time>2018-03-13T12:46:15Z</time>
           </trkpt>
"""
track_points_part_2 = """
           <trkpt lat="44.67977" lon="6.07364">
             <ele>987</ele>
             <time>2018-03-13T12:46:30Z</time>
           </trkpt>
           <trkpt lat="44.67972" lon="6.07367">
             <ele>987</ele>
             <time>2018-03-13T12:46:35Z</time>
           </trkpt>
           <trkpt lat="44.67966" lon="6.07368">
             <ele>987</ele>
             <time>2018-03-13T12:46:40Z</time>
           </trkpt>
           <trkpt lat="44.67961" lon="6.0737">
             <ele>986</ele>
             <time>2018-03-13T12:46:45Z</time>
           </trkpt>
           <trkpt lat="44.67938" lon="6.07377">
             <ele>986</ele>
             <time>2018-03-13T12:47:05Z</time>
           </trkpt>
           <trkpt lat="44.67933" lon="6.07381">
             <ele>986</ele>
             <time>2018-03-13T12:47:10Z</time>
           </trkpt>
           <trkpt lat="44.67922" lon="6.07385">
             <ele>985</ele>
             <time>2018-03-13T12:47:20Z</time>
           </trkpt>
           <trkpt lat="44.67911" lon="6.0739">
             <ele>980</ele>
             <time>2018-03-13T12:47:30Z</time>
           </trkpt>
           <trkpt lat="44.679" lon="6.07399">
             <ele>980</ele>
             <time>2018-03-13T12:47:40Z</time>
           </trkpt>
           <trkpt lat="44.67896" lon="6.07402">
             <ele>980</ele>
             <time>2018-03-13T12:47:45Z</time>
           </trkpt>
           <trkpt lat="44.67884" lon="6.07408">
             <ele>979</ele>
             <time>2018-03-13T12:47:55Z</time>
           </trkpt>
           <trkpt lat="44.67863" lon="6.07423">
             <ele>981</ele>
             <time>2018-03-13T12:48:15Z</time>
           </trkpt>
           <trkpt lat="44.67858" lon="6.07425">
             <ele>980</ele>
             <time>2018-03-13T12:48:20Z</time>
           </trkpt>
           <trkpt lat="44.67842" lon="6.07434">
             <ele>979</ele>
             <time>2018-03-13T12:48:35Z</time>
           </trkpt>
           <trkpt lat="44.67837" lon="6.07435">
             <ele>979</ele>
             <time>2018-03-13T12:48:40Z</time>
           </trkpt>
           <trkpt lat="44.67822" lon="6.07442">
             <ele>975</ele>
             <time>2018-03-13T12:48:55Z</time>
           </trkpt>
"""


@pytest.fixture()
def gpx_file() -> str:
    return (
        """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <name>just a workout</name>
    <trkseg>
"""
        + track_points_part_1
        + track_points_part_2
        + """
    </trkseg>
  </trk>
</gpx>
"""
    )


@pytest.fixture()
def gpx_file_wo_name() -> str:
    return (
        """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
    <trk>
      <trkseg>
"""
        + track_points_part_1
        + track_points_part_2
        + """
       </trkseg>
    </trk>
</gpx>
"""
    )


@pytest.fixture()
def gpx_file_with_description() -> str:
    return (
        """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <name>just a workout</name>
    <desc>this is workout description</desc>
    <trkseg>
"""
        + track_points_part_1
        + track_points_part_2
        + """
    </trkseg>
  </trk>
</gpx>
"""
    )


@pytest.fixture()
def gpx_file_with_empty_description() -> str:
    return (
        """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <name>just a workout</name>
    <desc></desc>
    <trkseg>
"""
        + track_points_part_1
        + track_points_part_2
        + """
    </trkseg>
  </trk>
</gpx>
"""
    )


@pytest.fixture()
def gpx_file_with_offset() -> str:
    return """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <trkseg>
      <trkpt lat="44.68095" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T13:44:45+01:00</time>
      </trkpt>
      <trkpt lat="44.68091" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T13:44:50+01:00</time>
      </trkpt>
      <trkpt lat="44.6808" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T13:45:00+01:00</time>
      </trkpt>
      <trkpt lat="44.68075" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T13:45:05+01:00</time>
      </trkpt>
      <trkpt lat="44.68071" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T13:45:10+01:00</time>
      </trkpt>
      <trkpt lat="44.68049" lon="6.07361">
        <ele>993</ele>
        <time>2018-03-13T13:45:30+01:00</time>
      </trkpt>
      <trkpt lat="44.68019" lon="6.07356">
        <ele>992</ele>
        <time>2018-03-13T13:45:55+01:00</time>
      </trkpt>
      <trkpt lat="44.68014" lon="6.07355">
        <ele>992</ele>
        <time>2018-03-13T13:46:00+01:00</time>
      </trkpt>
      <trkpt lat="44.67995" lon="6.07358">
        <ele>987</ele>
        <time>2018-03-13T13:46:15+01:00</time>
      </trkpt>
      <trkpt lat="44.67977" lon="6.07364">
        <ele>987</ele>
        <time>2018-03-13T13:46:30+01:00</time>
      </trkpt>
      <trkpt lat="44.67972" lon="6.07367">
        <ele>987</ele>
        <time>2018-03-13T13:46:35+01:00</time>
      </trkpt>
      <trkpt lat="44.67966" lon="6.07368">
        <ele>987</ele>
        <time>2018-03-13T13:46:40+01:00</time>
      </trkpt>
      <trkpt lat="44.67961" lon="6.0737">
        <ele>986</ele>
        <time>2018-03-13T13:46:45+01:00</time>
      </trkpt>
      <trkpt lat="44.67938" lon="6.07377">
        <ele>986</ele>
        <time>2018-03-13T13:47:05+01:00</time>
      </trkpt>
      <trkpt lat="44.67933" lon="6.07381">
        <ele>986</ele>
        <time>2018-03-13T13:47:10+01:00</time>
      </trkpt>
      <trkpt lat="44.67922" lon="6.07385">
        <ele>985</ele>
        <time>2018-03-13T13:47:20+01:00</time>
      </trkpt>
      <trkpt lat="44.67911" lon="6.0739">
        <ele>980</ele>
        <time>2018-03-13T13:47:30+01:00</time>
      </trkpt>
      <trkpt lat="44.679" lon="6.07399">
        <ele>980</ele>
        <time>2018-03-13T13:47:40+01:00</time>
      </trkpt>
      <trkpt lat="44.67896" lon="6.07402">
        <ele>980</ele>
        <time>2018-03-13T13:47:45+01:00</time>
      </trkpt>
      <trkpt lat="44.67884" lon="6.07408">
        <ele>979</ele>
        <time>2018-03-13T13:47:55+01:00</time>
      </trkpt>
      <trkpt lat="44.67863" lon="6.07423">
        <ele>981</ele>
        <time>2018-03-13T13:48:15+01:00</time>
      </trkpt>
      <trkpt lat="44.67858" lon="6.07425">
        <ele>980</ele>
        <time>2018-03-13T13:48:20+01:00</time>
      </trkpt>
      <trkpt lat="44.67842" lon="6.07434">
        <ele>979</ele>
        <time>2018-03-13T13:48:35+01:00</time>
      </trkpt>
      <trkpt lat="44.67837" lon="6.07435">
        <ele>979</ele>
        <time>2018-03-13T13:48:40+01:00</time>
      </trkpt>
      <trkpt lat="44.67822" lon="6.07442">
        <ele>975</ele>
        <time>2018-03-13T13:48:55+01:00</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""


@pytest.fixture()
def gpx_file_with_microseconds() -> str:
    return """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <trkseg>
      <trkpt lat="44.68095" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T13:44:45.787Z</time>
      </trkpt>
      <trkpt lat="44.68091" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T13:44:50.912Z</time>
      </trkpt>
      <trkpt lat="44.6808" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T13:45:00.895Z</time>
      </trkpt>
      <trkpt lat="44.68075" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T13:45:05.894Z</time>
      </trkpt>
      <trkpt lat="44.68071" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T13:45:10.875Z</time>
      </trkpt>
      <trkpt lat="44.68049" lon="6.07361">
        <ele>993</ele>
        <time>2018-03-13T13:45:30.834Z</time>
      </trkpt>
      <trkpt lat="44.68019" lon="6.07356">
        <ele>992</ele>
        <time>2018-03-13T13:45:55.887Z</time>
      </trkpt>
      <trkpt lat="44.68014" lon="6.07355">
        <ele>992</ele>
        <time>2018-03-13T13:46:00.898Z</time>
      </trkpt>
      <trkpt lat="44.67995" lon="6.07358">
        <ele>987</ele>
        <time>2018-03-13T13:46:15.904Z</time>
      </trkpt>
    </trkseg>
    <trkseg>
      <trkpt lat="44.67977" lon="6.07364">
        <ele>987</ele>
        <time>2018-03-13T13:46:30.883Z</time>
      </trkpt>
      <trkpt lat="44.67972" lon="6.07367">
        <ele>987</ele>
        <time>2018-03-13T13:46:35.899Z</time>
      </trkpt>
      <trkpt lat="44.67966" lon="6.07368">
        <ele>987</ele>
        <time>2018-03-13T13:46:40.909Z</time>
      </trkpt>
      <trkpt lat="44.67961" lon="6.0737">
        <ele>986</ele>
        <time>2018-03-13T13:46:45.889Z</time>
      </trkpt>
      <trkpt lat="44.67938" lon="6.07377">
        <ele>986</ele>
        <time>2018-03-13T13:47:05.884Z</time>
      </trkpt>
      <trkpt lat="44.67933" lon="6.07381">
        <ele>986</ele>
        <time>2018-03-13T13:47:10.918Z</time>
      </trkpt>
      <trkpt lat="44.67922" lon="6.07385">
        <ele>985</ele>
        <time>2018-03-13T13:47:20.903Z</time>
      </trkpt>
      <trkpt lat="44.67911" lon="6.0739">
        <ele>980</ele>
        <time>2018-03-13T13:47:30.917Z</time>
      </trkpt>
      <trkpt lat="44.679" lon="6.07399">
        <ele>980</ele>
        <time>2018-03-13T13:47:40.902Z</time>
      </trkpt>
      <trkpt lat="44.67896" lon="6.07402">
        <ele>980</ele>
        <time>2018-03-13T13:47:45.918Z</time>
      </trkpt>
      <trkpt lat="44.67884" lon="6.07408">
        <ele>979</ele>
        <time>2018-03-13T13:47:55.909Z</time>
      </trkpt>
      <trkpt lat="44.67863" lon="6.07423">
        <ele>981</ele>
        <time>2018-03-13T13:48:15.922Z</time>
      </trkpt>
      <trkpt lat="44.67858" lon="6.07425">
        <ele>980</ele>
        <time>2018-03-13T13:48:20.916Z</time>
      </trkpt>
      <trkpt lat="44.67842" lon="6.07434">
        <ele>979</ele>
        <time>2018-03-13T13:48:35.889Z</time>
      </trkpt>
      <trkpt lat="44.67837" lon="6.07435">
        <ele>979</ele>
        <time>2018-03-13T13:48:40.911Z</time>
      </trkpt>
      <trkpt lat="44.67822" lon="6.07442">
        <ele>975</ele>
        <time>2018-03-13T13:48:55.891Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""


@pytest.fixture()
def gpx_file_with_gpxtpx_extensions() -> str:
    return """<gpx
  xmlns="http://www.topografix.com/GPX/1/1"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  creator="Garmin Connect"
  version="1.1"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1
  http://www.topografix.com/GPX/11.xsd"
>
<metadata>
<link href="connect.garmin.com">
<text>Garmin Connect</text>
</link>
<time>2017-06-07T12:55:10.000Z</time>
</metadata>
<trk>
    <trkseg>
      <trkpt lat="44.68095" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T12:44:45Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>92</gpxtpx:hr>
            <gpxtpx:cad>0</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68091" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T12:44:50Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>87</gpxtpx:hr>
            <gpxtpx:cad>50</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.6808" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T12:45:00Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>88</gpxtpx:hr>
            <gpxtpx:cad>51</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68075" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T12:45:05Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>90</gpxtpx:hr>
            <gpxtpx:cad>54</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68071" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T12:45:10Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>87</gpxtpx:hr>
            <gpxtpx:cad>53</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68049" lon="6.07361">
        <ele>993</ele>
        <time>2018-03-13T12:45:30Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>85</gpxtpx:hr>
            <gpxtpx:cad>54</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68019" lon="6.07356">
        <ele>992</ele>
        <time>2018-03-13T12:45:55Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>86</gpxtpx:hr>
            <gpxtpx:cad>54</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68014" lon="6.07355">
        <ele>992</ele>
        <time>2018-03-13T12:46:00Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>84</gpxtpx:hr>
            <gpxtpx:cad>55</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67995" lon="6.07358">
        <ele>987</ele>
        <time>2018-03-13T12:46:15Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>86</gpxtpx:hr>
            <gpxtpx:cad>53</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67977" lon="6.07364">
        <ele>987</ele>
        <time>2018-03-13T12:46:30Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>88</gpxtpx:hr>
            <gpxtpx:cad>56</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67972" lon="6.07367">
        <ele>987</ele>
        <time>2018-03-13T12:46:35Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>86</gpxtpx:hr>
            <gpxtpx:cad>56</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67966" lon="6.07368">
        <ele>987</ele>
        <time>2018-03-13T12:46:40Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>83</gpxtpx:hr>
            <gpxtpx:cad>55</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67961" lon="6.0737">
        <ele>986</ele>
        <time>2018-03-13T12:46:45Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>83</gpxtpx:hr>
            <gpxtpx:cad>56</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67938" lon="6.07377">
        <ele>986</ele>
        <time>2018-03-13T12:47:05Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>85</gpxtpx:hr>
            <gpxtpx:cad>54</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67933" lon="6.07381">
        <ele>986</ele>
        <time>2018-03-13T12:47:10Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>86</gpxtpx:hr>
            <gpxtpx:cad>56</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67922" lon="6.07385">
        <ele>985</ele>
        <time>2018-03-13T12:47:20Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>85</gpxtpx:hr>
            <gpxtpx:cad>53</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67911" lon="6.0739">
        <ele>980</ele>
        <time>2018-03-13T12:47:30Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>84</gpxtpx:hr>
            <gpxtpx:cad>56</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.679" lon="6.07399">
        <ele>980</ele>
        <time>2018-03-13T12:47:40Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>86</gpxtpx:hr>
            <gpxtpx:cad>55</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67896" lon="6.07402">
        <ele>980</ele>
        <time>2018-03-13T12:47:45Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>83</gpxtpx:hr>
            <gpxtpx:cad>55</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67884" lon="6.07408">
        <ele>979</ele>
        <time>2018-03-13T12:47:55Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>83</gpxtpx:hr>
            <gpxtpx:cad>55</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67863" lon="6.07423">
        <ele>981</ele>
        <time>2018-03-13T12:48:15Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>82</gpxtpx:hr>
            <gpxtpx:cad>54</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67858" lon="6.07425">
        <ele>980</ele>
        <time>2018-03-13T12:48:20Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>85</gpxtpx:hr>
            <gpxtpx:cad>57</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67842" lon="6.07434">
        <ele>979</ele>
        <time>2018-03-13T12:48:35Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>84</gpxtpx:hr>
            <gpxtpx:cad>57</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67837" lon="6.07435">
        <ele>979</ele>
        <time>2018-03-13T12:48:40Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>84</gpxtpx:hr>
            <gpxtpx:cad>52</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67822" lon="6.07442">
        <ele>975</ele>
        <time>2018-03-13T12:48:55Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>81</gpxtpx:hr>
            <gpxtpx:cad>50</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""


@pytest.fixture()
def gpx_file_with_ns3_extensions() -> str:
    return """<gpx
  xmlns="http://www.topografix.com/GPX/1/1"
  xmlns:ns3="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:ns2="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  creator="Garmin Connect"
  version="1.1"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1
  http://www.topografix.com/GPX/11.xsd"
>
<metadata>
<link href="connect.garmin.com">
<text>Garmin Connect</text>
</link>
<time>2017-06-07T12:55:10.000Z</time>
</metadata>
<trk>
    <trkseg>
      <trkpt lat="44.68095" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T12:44:45Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>92</ns3:hr>
            <ns3:cad>0</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68091" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T12:44:50Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>87</ns3:hr>
            <ns3:cad>50</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.6808" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T12:45:00Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>88</ns3:hr>
            <ns3:cad>51</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68075" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T12:45:05Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>90</ns3:hr>
            <ns3:cad>54</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68071" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T12:45:10Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>87</ns3:hr>
            <ns3:cad>53</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68049" lon="6.07361">
        <ele>993</ele>
        <time>2018-03-13T12:45:30Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>85</ns3:hr>
            <ns3:cad>54</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68019" lon="6.07356">
        <ele>992</ele>
        <time>2018-03-13T12:45:55Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>86</ns3:hr>
            <ns3:cad>54</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.68014" lon="6.07355">
        <ele>992</ele>
        <time>2018-03-13T12:46:00Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>84</ns3:hr>
            <ns3:cad>55</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67995" lon="6.07358">
        <ele>987</ele>
        <time>2018-03-13T12:46:15Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>86</ns3:hr>
            <ns3:cad>53</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67977" lon="6.07364">
        <ele>987</ele>
        <time>2018-03-13T12:46:30Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>88</ns3:hr>
            <ns3:cad>56</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67972" lon="6.07367">
        <ele>987</ele>
        <time>2018-03-13T12:46:35Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>86</ns3:hr>
            <ns3:cad>56</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67966" lon="6.07368">
        <ele>987</ele>
        <time>2018-03-13T12:46:40Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>83</ns3:hr>
            <ns3:cad>55</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67961" lon="6.0737">
        <ele>986</ele>
        <time>2018-03-13T12:46:45Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>83</ns3:hr>
            <ns3:cad>56</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67938" lon="6.07377">
        <ele>986</ele>
        <time>2018-03-13T12:47:05Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>85</ns3:hr>
            <ns3:cad>54</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67933" lon="6.07381">
        <ele>986</ele>
        <time>2018-03-13T12:47:10Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>86</ns3:hr>
            <ns3:cad>56</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67922" lon="6.07385">
        <ele>985</ele>
        <time>2018-03-13T12:47:20Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>85</ns3:hr>
            <ns3:cad>53</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67911" lon="6.0739">
        <ele>980</ele>
        <time>2018-03-13T12:47:30Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>84</ns3:hr>
            <ns3:cad>56</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.679" lon="6.07399">
        <ele>980</ele>
        <time>2018-03-13T12:47:40Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>86</ns3:hr>
            <ns3:cad>55</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67896" lon="6.07402">
        <ele>980</ele>
        <time>2018-03-13T12:47:45Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>83</ns3:hr>
            <ns3:cad>55</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67884" lon="6.07408">
        <ele>979</ele>
        <time>2018-03-13T12:47:55Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>83</ns3:hr>
            <ns3:cad>55</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67863" lon="6.07423">
        <ele>981</ele>
        <time>2018-03-13T12:48:15Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>82</ns3:hr>
            <ns3:cad>54</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67858" lon="6.07425">
        <ele>980</ele>
        <time>2018-03-13T12:48:20Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>85</ns3:hr>
            <ns3:cad>57</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67842" lon="6.07434">
        <ele>979</ele>
        <time>2018-03-13T12:48:35Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>84</ns3:hr>
            <ns3:cad>57</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67837" lon="6.07435">
        <ele>979</ele>
        <time>2018-03-13T12:48:40Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>84</ns3:hr>
            <ns3:cad>52</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="44.67822" lon="6.07442">
        <ele>975</ele>
        <time>2018-03-13T12:48:55Z</time>
        <extensions>
          <ns3:TrackPointExtension>
            <ns3:atemp>28.0</ns3:atemp>
            <ns3:hr>81</ns3:hr>
            <ns3:cad>50</ns3:cad>
          </ns3:TrackPointExtension>
        </extensions>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""


@pytest.fixture()
def gpx_file_without_elevation() -> str:
    return """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <name>just a workout</name>
    <trkseg>
      <trkpt lat="44.68095" lon="6.07367">
        <time>2018-03-13T12:44:45Z</time>
      </trkpt>
      <trkpt lat="44.68091" lon="6.07367">
        <time>2018-03-13T12:44:50Z</time>
      </trkpt>
      <trkpt lat="44.6808" lon="6.07364">
        <time>2018-03-13T12:45:00Z</time>
      </trkpt>
      <trkpt lat="44.68075" lon="6.07364">
        <time>2018-03-13T12:45:05Z</time>
      </trkpt>
      <trkpt lat="44.68071" lon="6.07364">
        <time>2018-03-13T12:45:10Z</time>
      </trkpt>
      <trkpt lat="44.68049" lon="6.07361">
        <time>2018-03-13T12:45:30Z</time>
      </trkpt>
      <trkpt lat="44.68019" lon="6.07356">
        <time>2018-03-13T12:45:55Z</time>
      </trkpt>
      <trkpt lat="44.68014" lon="6.07355">
        <time>2018-03-13T12:46:00Z</time>
      </trkpt>
      <trkpt lat="44.67995" lon="6.07358">
        <time>2018-03-13T12:46:15Z</time>
      </trkpt>
      <trkpt lat="44.67977" lon="6.07364">
        <time>2018-03-13T12:46:30Z</time>
      </trkpt>
      <trkpt lat="44.67972" lon="6.07367">
        <time>2018-03-13T12:46:35Z</time>
      </trkpt>
      <trkpt lat="44.67966" lon="6.07368">
        <time>2018-03-13T12:46:40Z</time>
      </trkpt>
      <trkpt lat="44.67961" lon="6.0737">
        <time>2018-03-13T12:46:45Z</time>
      </trkpt>
      <trkpt lat="44.67938" lon="6.07377">
        <time>2018-03-13T12:47:05Z</time>
      </trkpt>
      <trkpt lat="44.67933" lon="6.07381">
        <time>2018-03-13T12:47:10Z</time>
      </trkpt>
      <trkpt lat="44.67922" lon="6.07385">
        <time>2018-03-13T12:47:20Z</time>
      </trkpt>
      <trkpt lat="44.67911" lon="6.0739">
        <time>2018-03-13T12:47:30Z</time>
      </trkpt>
      <trkpt lat="44.679" lon="6.07399">
        <time>2018-03-13T12:47:40Z</time>
      </trkpt>
      <trkpt lat="44.67896" lon="6.07402">
        <time>2018-03-13T12:47:45Z</time>
      </trkpt>
      <trkpt lat="44.67884" lon="6.07408">
        <time>2018-03-13T12:47:55Z</time>
      </trkpt>
      <trkpt lat="44.67863" lon="6.07423">
        <time>2018-03-13T12:48:15Z</time>
      </trkpt>
      <trkpt lat="44.67858" lon="6.07425">
        <time>2018-03-13T12:48:20Z</time>
      </trkpt>
      <trkpt lat="44.67842" lon="6.07434">
        <time>2018-03-13T12:48:35Z</time>
      </trkpt>
      <trkpt lat="44.67837" lon="6.07435">
        <time>2018-03-13T12:48:40Z</time>
      </trkpt>
      <trkpt lat="44.67822" lon="6.07442">
        <time>2018-03-13T12:48:55Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""


@pytest.fixture()
def gpx_file_w_title_exceeding_limit() -> str:
    return (
        """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <name>"""
        + random_string(TITLE_MAX_CHARACTERS + 1)
        + """</name>
    <trkseg>
"""
        + track_points_part_1
        + track_points_part_2
        + """
    </trkseg>
  </trk>
</gpx>
"""
    )


@pytest.fixture()
def gpx_file_wo_track() -> str:
    return """<?xml version='1.0' encoding='UTF-8'?>
<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata/>
</gpx>
"""


@pytest.fixture()
def gpx_file_invalid_xml() -> str:
    return """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <name>just a workout</name>
"""


@pytest.fixture()
def gpx_file_without_time() -> str:
    return """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <name>just a workout</name>
    <trkseg>
      <trkpt lat="44.68095" lon="6.07367">
        <ele>998</ele>
      </trkpt>
      <trkpt lat="44.68091" lon="6.07367">
        <ele>998</ele>
      </trkpt>
      <trkpt lat="44.6808" lon="6.07364">
        <ele>994</ele>
      </trkpt>
      <trkpt lat="44.68075" lon="6.07364">
        <ele>994</ele>
      </trkpt>
      <trkpt lat="44.68071" lon="6.07364">
        <ele>994</ele>
      </trkpt>
      <trkpt lat="44.68049" lon="6.07361">
        <ele>993</ele>
      </trkpt>
      <trkpt lat="44.68019" lon="6.07356">
        <ele>992</ele>
      </trkpt>
      <trkpt lat="44.68014" lon="6.07355">
        <ele>992</ele>
      </trkpt>
      <trkpt lat="44.67995" lon="6.07358">
        <ele>987</ele>
      </trkpt>
      <trkpt lat="44.67977" lon="6.07364">
        <ele>987</ele>
      </trkpt>
      <trkpt lat="44.67972" lon="6.07367">
        <ele>987</ele>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""


@pytest.fixture()
def gpx_file_with_segments() -> str:
    return (
        """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <name>just a workout</name>
    <trkseg>
"""
        + track_points_part_1
        + """
    </trkseg>
    <trkseg>
"""
        + track_points_part_2
        + """
    </trkseg>
  </trk>
</gpx>
"""
    )


@pytest.fixture()
def gpx_file_with_3_segments() -> str:
    """60 seconds between each segment"""
    return """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <name>just a workout</name>
    <trkseg>
      <trkpt lat="44.68095" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T12:44:50Z</time>
      </trkpt>
      <trkpt lat="44.68091" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T12:44:55Z</time>
      </trkpt>
      <trkpt lat="44.6808" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T12:45:00Z</time>
      </trkpt>
    </trkseg>
    <trkseg>
      <trkpt lat="44.67972" lon="6.07367">
        <ele>987</ele>
        <time>2018-03-13T12:46:00Z</time>
      </trkpt>
      <trkpt lat="44.67966" lon="6.07368">
        <ele>987</ele>
        <time>2018-03-13T12:46:05Z</time>
      </trkpt>
      <trkpt lat="44.67961" lon="6.0737">
        <ele>986</ele>
        <time>2018-03-13T12:46:10Z</time>
      </trkpt>
    </trkseg>
    <trkseg>
      <trkpt lat="44.67858" lon="6.07425">
        <ele>980</ele>
        <time>2018-03-13T12:47:10Z</time>
      </trkpt>
      <trkpt lat="44.67842" lon="6.07434">
        <ele>979</ele>
        <time>2018-03-13T12:47:15Z</time>
      </trkpt>
      <trkpt lat="44.67837" lon="6.07435">
        <ele>979</ele>
        <time>2018-03-13T12:47:20Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""


@pytest.fixture()
def gpx_file_with_zero_distance_segment() -> str:
    return """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <name>just a workout</name>
    <trkseg>
      <trkpt lat="44.68095" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T12:44:50Z</time>
      </trkpt>
      <trkpt lat="44.68091" lon="6.07367">
        <ele>998</ele>
        <time>2018-03-13T12:44:55Z</time>
      </trkpt>
      <trkpt lat="44.6808" lon="6.07364">
        <ele>994</ele>
        <time>2018-03-13T12:45:00Z</time>
      </trkpt>
    </trkseg>
    <trkseg>
      <trkpt lat="44.67972" lon="6.07367">
        <ele>987</ele>
        <time>2018-03-13T12:46:00Z</time>
      </trkpt>
    </trkseg>
    <trkseg>
      <trkpt lat="44.67858" lon="6.07425">
        <ele>980</ele>
        <time>2018-03-13T12:47:10Z</time>
      </trkpt>
      <trkpt lat="44.67842" lon="6.07434">
        <ele>979</ele>
        <time>2018-03-13T12:47:15Z</time>
      </trkpt>
      <trkpt lat="44.67837" lon="6.07435">
        <ele>979</ele>
        <time>2018-03-13T12:47:20Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""


@pytest.fixture()
def gpx_file_storage(gpx_file: str) -> FileStorage:
    return FileStorage(
        filename=f"{uuid4().hex}.gpx", stream=BytesIO(str.encode(gpx_file))
    )


@pytest.fixture()
def upload_workouts_archive_mock() -> Iterator[MagicMock]:
    with patch("fittrackee.workouts.tasks.upload_workouts_archive") as mock:
        mock.send = MagicMock()
        mock.send.return_value = message
        yield mock


@pytest.fixture()
def invalid_kml_file() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<kml
  xmlns="http://www.opengis.net/kml/2.2"
  xmlns:gx="http://www.google.com/kml/ext/2.2"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:opentracks="http://opentracksapp.com/xmlschemas/v1"
>
  <Document>
    <open>1</open>
"""


@pytest.fixture()
def kml_file_wo_tracks() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<kml
  xmlns="http://www.opengis.net/kml/2.2"
  xmlns:gx="http://www.google.com/kml/ext/2.2"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:opentracks="http://opentracksapp.com/xmlschemas/v1"
>
  <Document>
    <Placemark>
      <name>New York City</name>
      <Point>
       <coordinates>-74.006393,40.714172,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
"""


kml_track_points_part_1 = """
          <when>2018-03-13T13:43:45+01:00</when>
          <gx:coord/>
          <when>2018-03-13T13:44:45+01:00</when>
          <gx:coord>6.07367 44.68095 998</gx:coord>
          <when>2018-03-13T13:44:50+01:00</when>
          <gx:coord>6.07367 44.68091 998</gx:coord>
          <when>2018-03-13T13:45:00+01:00</when>
          <gx:coord>6.07364 44.6808 994</gx:coord>
          <when>2018-03-13T13:45:05+01:00</when>
          <gx:coord>6.07364 44.68075 994</gx:coord>
          <when>2018-03-13T13:45:10+01:00</when>
          <gx:coord>6.07364 44.68071 994</gx:coord>
          <when>2018-03-13T13:45:30+01:00</when>
          <gx:coord>6.07361 44.68049 993</gx:coord>
          <when>2018-03-13T13:45:55+01:00</when>
          <gx:coord>6.07356 44.68019 992</gx:coord>
          <when>2018-03-13T13:46:00+01:00</when>
          <gx:coord>6.07355 44.68014 992</gx:coord>
          <when>2018-03-13T13:46:15+01:00</when>
          <gx:coord>6.07358 44.67995 987</gx:coord>
"""
kml_track_points_part_2 = """
          <when>2018-03-13T13:46:30+01:00</when>
          <gx:coord>6.07364 44.67977 987</gx:coord>
          <when>2018-03-13T13:46:35+01:00</when>
          <gx:coord>6.07367 44.67972 987</gx:coord>
          <when>2018-03-13T13:46:40+01:00</when>
          <gx:coord>6.07368 44.67966 987</gx:coord>
          <when>2018-03-13T13:46:45+01:00</when>
          <gx:coord>6.0737 44.67961 986</gx:coord>
          <when>2018-03-13T13:47:05+01:00</when>
          <gx:coord>6.07377 44.67938 986</gx:coord>
          <when>2018-03-13T13:47:10+01:00</when>
          <gx:coord>6.07381 44.67933 986</gx:coord>
          <when>2018-03-13T13:47:20+01:00</when>
          <gx:coord>6.07385 44.67922 985</gx:coord>
          <when>2018-03-13T13:47:30+01:00</when>
          <gx:coord>6.0739 44.67911 985</gx:coord>
          <when>2018-03-13T13:47:40+01:00</when>
          <gx:coord>6.07399 44.679 980</gx:coord>
          <when>2018-03-13T13:47:45+01:00</when>
          <gx:coord>6.07402 44.67896 980</gx:coord>
          <when>2018-03-13T13:47:55+01:00</when>
          <gx:coord>6.07408 44.67884 979</gx:coord>
          <when>2018-03-13T13:48:15+01:00</when>
          <gx:coord>6.07423 44.67863 981</gx:coord>
          <when>2018-03-13T13:48:20+01:00</when>
          <gx:coord>6.07425 44.67858 980</gx:coord>
          <when>2018-03-13T13:48:35+01:00</when>
          <gx:coord>6.07434 44.67842 979</gx:coord>
          <when>2018-03-13T13:48:40+01:00</when>
          <gx:coord>6.07435 44.67837 979</gx:coord>
          <when>2018-03-13T13:48:55+01:00</when>
          <gx:coord>6.07442 44.67822 975</gx:coord>
"""


@pytest.fixture()
def kml_2_2_with_one_track() -> str:
    return (
        """<?xml version="1.0" encoding="UTF-8"?>
<kml
  xmlns="http://www.opengis.net/kml/2.2"
  xmlns:gx="http://www.google.com/kml/ext/2.2"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:opentracks="http://opentracksapp.com/xmlschemas/v1"
>
  <Document>
    <open>1</open>
    <visibility>1</visibility>
    <name><![CDATA[just a workout]]></name>
    <atom:generator><![CDATA[OpenTracks]]></atom:generator>
    <Style id="track">
      <LineStyle>
        <color>7f0000ff</color>
        <width>4</width>
      </LineStyle>
      <IconStyle>
        <scale>1.3</scale>
        <Icon/>
      </IconStyle>
    </Style>
    <Style id="waypoint">
      <IconStyle>
        <Icon/>
      </IconStyle>
    </Style>
    <Schema id="schema">
      <gx:SimpleArrayField name="speed" type="float">
        <displayName><![CDATA[Vitesse (m/s)]]></displayName>
      </gx:SimpleArrayField>
      <gx:SimpleArrayField name="power" type="float">
        <displayName><![CDATA[Puissance (W)]]></displayName>
      </gx:SimpleArrayField>
      <gx:SimpleArrayField name="cadence" type="float">
        <displayName><![CDATA[Cadence (tr/min)]]></displayName>
      </gx:SimpleArrayField>
      <gx:SimpleArrayField name="heart_rate" type="float">
        <displayName><![CDATA[Fréquence cardiaque (bpm)]]></displayName>
      </gx:SimpleArrayField>
    </Schema>
    <Placemark>
      <name><![CDATA[just a workout]]></name>
      <description><![CDATA[some description]]></description>
      <icon><![CDATA[WALK]]></icon>
      <opentracks:trackid>7ab3bdbd-6941-47be-9cbd-865b5cfe4f74 "
       </opentracks:trackid>
      <styleUrl>#track</styleUrl>
      <ExtendedData>
        <Data name="type">
          <value><![CDATA[marche]]></value>
        </Data>
      </ExtendedData>
      <gx:MultiTrack>
        <altitudeMode>absolute</altitudeMode>
        <gx:interpolate>1</gx:interpolate>
        <gx:Track>
"""
        + kml_track_points_part_1
        + kml_track_points_part_2
        + """
        </gx:Track>
      </gx:MultiTrack>
    </Placemark>
  </Document>
</kml>
"""
    )


@pytest.fixture()
def kml_2_2_with_two_tracks() -> str:
    return (
        """<?xml version="1.0" encoding="UTF-8"?>
<kml
  xmlns="http://www.opengis.net/kml/2.2"
  xmlns:gx="http://www.google.com/kml/ext/2.2"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:opentracks="http://opentracksapp.com/xmlschemas/v1"
>
  <Document>
    <open>1</open>
    <visibility>1</visibility>
    <name><![CDATA[just a workout]]></name>
    <atom:generator><![CDATA[OpenTracks]]></atom:generator>
    <Style id="track">
      <LineStyle>
        <color>7f0000ff</color>
        <width>4</width>
      </LineStyle>
      <IconStyle>
        <scale>1.3</scale>
        <Icon/>
      </IconStyle>
    </Style>
    <Style id="waypoint">
      <IconStyle>
        <Icon/>
      </IconStyle>
    </Style>
    <Schema id="schema">
      <gx:SimpleArrayField name="speed" type="float">
        <displayName><![CDATA[Vitesse (m/s)]]></displayName>
      </gx:SimpleArrayField>
      <gx:SimpleArrayField name="power" type="float">
        <displayName><![CDATA[Puissance (W)]]></displayName>
      </gx:SimpleArrayField>
      <gx:SimpleArrayField name="cadence" type="float">
        <displayName><![CDATA[Cadence (tr/min)]]></displayName>
      </gx:SimpleArrayField>
      <gx:SimpleArrayField name="heart_rate" type="float">
        <displayName><![CDATA[Fréquence cardiaque (bpm)]]></displayName>
      </gx:SimpleArrayField>
    </Schema>
    <Placemark>
      <name><![CDATA[just a workout]]></name>
      <description><![CDATA[some description]]></description>
      <icon><![CDATA[WALK]]></icon>
      <opentracks:trackid>7ab3bdbd-6941-47be-9cbd-865b5cfe4f74 "
       </opentracks:trackid>
      <styleUrl>#track</styleUrl>
      <ExtendedData>
        <Data name="type">
          <value><![CDATA[marche]]></value>
        </Data>
      </ExtendedData>
      <gx:MultiTrack>
        <altitudeMode>absolute</altitudeMode>
        <gx:interpolate>1</gx:interpolate>
        <gx:Track>
"""
        + kml_track_points_part_1
        + """
        </gx:Track>
        <gx:Track>
"""
        + kml_track_points_part_2
        + """
        </gx:Track>
      </gx:MultiTrack>
    </Placemark>
  </Document>
</kml>
"""
    )


def kml_2_2_to_kml_2_3(kml_content: str) -> str:
    return kml_content.replace('/2.2"', '/2.3"').replace("gx:", "")


@pytest.fixture()
def kml_2_3_with_one_track(kml_2_2_with_one_track: str) -> str:
    return kml_2_2_to_kml_2_3(kml_2_2_with_one_track)


@pytest.fixture()
def kml_2_3_with_two_tracks(kml_2_2_with_two_tracks: str) -> str:
    return kml_2_2_to_kml_2_3(kml_2_2_with_two_tracks)


@pytest.fixture()
def kml_2_3_wo_name_and_description(kml_2_2_with_one_track: str) -> str:
    return (
        kml_2_2_to_kml_2_3(kml_2_2_with_one_track)
        .replace("<name><![CDATA[just a workout]]></name>", "")
        .replace("<description><![CDATA[some description]]></description>", "")
    )


@pytest.fixture()
def invalid_tcx_file() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
>
    <Activities>
        <Activity Sport="Other">
            <Id>2018-03-13T12:44:45Z</Id>
    """


@pytest.fixture()
def tcx_file_wo_activities() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
>
</TrainingCenterDatabase>"""


@pytest.fixture()
def tcx_file_wo_laps() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
>
    <Activities>
        <Activity Sport="Other">
            <Id>2018-03-13T12:44:45Z</Id>
        </Activity>
    </Activities>
</TrainingCenterDatabase>"""


@pytest.fixture()
def tcx_file_wo_tracks() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
>
    <Activities>
        <Activity Sport="Other">
            <Id>2018-03-13T12:44:45Z</Id>
            <Lap StartTime="2018-03-13T12:44:45Z">
            </Lap>
        </Activity>
    </Activities>
</TrainingCenterDatabase>"""


tcx_track_points_part_1 = """        <Trackpoint>
          <Time>2018-03-13T12:44:45Z</Time>
          <Position>
            <LatitudeDegrees>44.68095000</LatitudeDegrees>
            <LongitudeDegrees>6.073670000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>997.00000</AltitudeMeters>
          <DistanceMeters>0.000</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:44:50Z</Time>
          <Position>
            <LatitudeDegrees>44.68091000</LatitudeDegrees>
            <LongitudeDegrees>6.073670000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>996.00000</AltitudeMeters>
          <DistanceMeters>4.449</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:45:00Z</Time>
          <Position>
            <LatitudeDegrees>44.68080000</LatitudeDegrees>
            <LongitudeDegrees>6.073640000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>996.00000</AltitudeMeters>
          <DistanceMeters>16.908</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:45:05Z</Time>
          <Position>
            <LatitudeDegrees>44.68075000</LatitudeDegrees>
            <LongitudeDegrees>6.073640000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>996.00000</AltitudeMeters>
          <DistanceMeters>22.467</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:45:10Z</Time>
          <Position>
            <LatitudeDegrees>44.68071000</LatitudeDegrees>
            <LongitudeDegrees>6.073640000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>996.00000</AltitudeMeters>
          <DistanceMeters>26.914</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:45:30Z</Time>
          <Position>
            <LatitudeDegrees>44.68049000</LatitudeDegrees>
            <LongitudeDegrees>6.073610000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>995.00000</AltitudeMeters>
          <DistanceMeters>51.492</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:45:55Z</Time>
          <Position>
            <LatitudeDegrees>44.68019000</LatitudeDegrees>
            <LongitudeDegrees>6.073560000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>993.00000</AltitudeMeters>
          <DistanceMeters>85.083</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:46:00Z</Time>
          <Position>
            <LatitudeDegrees>44.68014000</LatitudeDegrees>
            <LongitudeDegrees>6.073550000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>992.00000</AltitudeMeters>
          <DistanceMeters>90.698</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:46:15Z</Time>
          <Position>
            <LatitudeDegrees>44.67995000</LatitudeDegrees>
            <LongitudeDegrees>6.073580000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>991.00000</AltitudeMeters>
          <DistanceMeters>111.958</DistanceMeters>
        </Trackpoint>"""


tcx_track_points_part_2 = """<Trackpoint>
          <Time>2018-03-13T12:46:30Z</Time>
          <Position>
            <LatitudeDegrees>44.67977000</LatitudeDegrees>
            <LongitudeDegrees>6.073640000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>989.00000</AltitudeMeters>
          <DistanceMeters>132.527</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:46:35Z</Time>
          <Position>
            <LatitudeDegrees>44.67972000</LatitudeDegrees>
            <LongitudeDegrees>6.073670000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>988.00000</AltitudeMeters>
          <DistanceMeters>138.572</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:46:40Z</Time>
          <Position>
            <LatitudeDegrees>44.67966000</LatitudeDegrees>
            <LongitudeDegrees>6.073680000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>988.00000</AltitudeMeters>
          <DistanceMeters>145.290</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:46:45Z</Time>
          <Position>
            <LatitudeDegrees>44.67961000</LatitudeDegrees>
            <LongitudeDegrees>6.073700000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>987.00000</AltitudeMeters>
          <DistanceMeters>151.071</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:47:05Z</Time>
          <Position>
            <LatitudeDegrees>44.67938000</LatitudeDegrees>
            <LongitudeDegrees>6.073770000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>985.00000</AltitudeMeters>
          <DistanceMeters>177.238</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:47:10Z</Time>
          <Position>
            <LatitudeDegrees>44.67933000</LatitudeDegrees>
            <LongitudeDegrees>6.073810000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>985.00000</AltitudeMeters>
          <DistanceMeters>183.635</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:47:20Z</Time>
          <Position>
            <LatitudeDegrees>44.67922000</LatitudeDegrees>
            <LongitudeDegrees>6.073850000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>985.00000</AltitudeMeters>
          <DistanceMeters>196.269</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:47:30Z</Time>
          <Position>
            <LatitudeDegrees>44.67911000</LatitudeDegrees>
            <LongitudeDegrees>6.073900000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>984.00000</AltitudeMeters>
          <DistanceMeters>209.123</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:47:40Z</Time>
          <Position>
            <LatitudeDegrees>44.67900000</LatitudeDegrees>
            <LongitudeDegrees>6.073990000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>983.00000</AltitudeMeters>
          <DistanceMeters>223.274</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:47:45Z</Time>
          <Position>
            <LatitudeDegrees>44.67896000</LatitudeDegrees>
            <LongitudeDegrees>6.074020000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>983.00000</AltitudeMeters>
          <DistanceMeters>228.315</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:47:55Z</Time>
          <Position>
            <LatitudeDegrees>44.67884000</LatitudeDegrees>
            <LongitudeDegrees>6.074080000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>982.00000</AltitudeMeters>
          <DistanceMeters>242.477</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:48:15Z</Time>
          <Position>
            <LatitudeDegrees>44.67863000</LatitudeDegrees>
            <LongitudeDegrees>6.074230000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>979.00000</AltitudeMeters>
          <DistanceMeters>268.667</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:48:20Z</Time>
          <Position>
            <LatitudeDegrees>44.67858000</LatitudeDegrees>
            <LongitudeDegrees>6.074250000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>979.00000</AltitudeMeters>
          <DistanceMeters>274.448</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:48:35Z</Time>
          <Position>
            <LatitudeDegrees>44.67842000</LatitudeDegrees>
            <LongitudeDegrees>6.074340000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>978.00000</AltitudeMeters>
          <DistanceMeters>293.610</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:48:40Z</Time>
          <Position>
            <LatitudeDegrees>44.67837000</LatitudeDegrees>
            <LongitudeDegrees>6.074350000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>978.00000</AltitudeMeters>
          <DistanceMeters>299.225</DistanceMeters>
        </Trackpoint>
        <Trackpoint>
          <Time>2018-03-13T12:48:55Z</Time>
          <Position>
            <LatitudeDegrees>44.67822000</LatitudeDegrees>
            <LongitudeDegrees>6.074420000</LongitudeDegrees>
          </Position>
          <AltitudeMeters>976.00000</AltitudeMeters>
          <DistanceMeters>316.798</DistanceMeters>
        </Trackpoint>"""


@pytest.fixture()
def tcx_with_one_lap_and_one_track() -> str:
    return (
        """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
>
    <Activities>
        <Activity Sport="Other">
            <Id>2018-03-13T12:44:45Z</Id>
            <Lap StartTime="2018-03-13T12:44:45Z">
                <Track>
"""
        + tcx_track_points_part_1
        + tcx_track_points_part_2
        + """
                </Track>
            </Lap>
        </Activity>
    </Activities>
</TrainingCenterDatabase>
"""
    )


@pytest.fixture()
def tcx_with_one_lap_and_two_tracks() -> str:
    return (
        """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
>
    <Activities>
        <Activity Sport="Other">
            <Id>2018-03-13T12:44:45Z</Id>
            <Lap StartTime="2018-03-13T12:44:45Z">
                <Track>
"""
        + tcx_track_points_part_1
        + """
                </Track>
                <Track>
"""
        + tcx_track_points_part_2
        + """
                </Track>
            </Lap>
        </Activity>
    </Activities>
</TrainingCenterDatabase>
"""
    )


@pytest.fixture()
def tcx_with_two_laps() -> str:
    return (
        """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
>
    <Activities>
        <Activity Sport="Other">
            <Id>2018-03-13T12:44:45Z</Id>
            <Lap StartTime="2018-03-13T12:44:45Z">
                <Track>
"""
        + tcx_track_points_part_1
        + """
                </Track>
            </Lap>
            <Lap StartTime="2018-03-13T12:46:30Z">
                <Track>
"""
        + tcx_track_points_part_2
        + """
                </Track>
            </Lap>
        </Activity>
    </Activities>
</TrainingCenterDatabase>
"""
    )


@pytest.fixture()
def tcx_with_two_activities() -> str:
    return (
        """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
>
    <Activities>
        <Activity Sport="Other">
            <Id>2018-03-13T12:44:45Z</Id>
            <Lap StartTime="2018-03-13T12:44:45Z">
                <Track>
"""
        + tcx_track_points_part_1
        + """
                </Track>
            </Lap>
        </Activity>
        <Activity Sport="Biking">
            <Id>2018-03-13T12:46:30Z</Id>
            <Lap StartTime="2018-03-13T12:46:30Z">
                <Track>
"""
        + tcx_track_points_part_2
        + """
                </Track>
            </Lap>
        </Activity>
    </Activities>
</TrainingCenterDatabase>
"""
    )


@pytest.fixture()
def tcx_with_invalid_elevation() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
>
    <Activities>
        <Activity Sport="Other">
            <Id>2018-03-13T12:44:45Z</Id>
            <Lap StartTime="2018-03-13T12:44:45Z">
                <Track>
                    <Trackpoint>
                      <Time>2018-03-13T12:44:45Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68095000</LatitudeDegrees>
                        <LongitudeDegrees>6.073670000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>10000.00</AltitudeMeters>
                      <DistanceMeters>0.000</DistanceMeters>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:44:50Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68091000</LatitudeDegrees>
                        <LongitudeDegrees>6.073670000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>10000.00</AltitudeMeters>
                      <DistanceMeters>4.449</DistanceMeters>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:00Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68080000</LatitudeDegrees>
                        <LongitudeDegrees>6.073640000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>11000.00</AltitudeMeters>
                      <DistanceMeters>16.908</DistanceMeters>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:05Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68075000</LatitudeDegrees>
                        <LongitudeDegrees>6.073640000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>12000.00</AltitudeMeters>
                      <DistanceMeters>22.467</DistanceMeters>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:10Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68071000</LatitudeDegrees>
                        <LongitudeDegrees>6.073640000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>13000.00</AltitudeMeters>
                      <DistanceMeters>26.914</DistanceMeters>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:30Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68049000</LatitudeDegrees>
                        <LongitudeDegrees>6.073610000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>-10000.00</AltitudeMeters>
                      <DistanceMeters>51.492</DistanceMeters>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:55Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68019000</LatitudeDegrees>
                        <LongitudeDegrees>6.073560000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>-12000.00</AltitudeMeters>
                      <DistanceMeters>85.083</DistanceMeters>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:46:00Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68014000</LatitudeDegrees>
                        <LongitudeDegrees>6.073550000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>-1200000</AltitudeMeters>
                      <DistanceMeters>90.698</DistanceMeters>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:46:15Z</Time>
                      <Position>
                        <LatitudeDegrees>44.67995000</LatitudeDegrees>
                        <LongitudeDegrees>6.073580000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>1200000</AltitudeMeters>
                      <DistanceMeters>111.958</DistanceMeters>
                    </Trackpoint>
                </Track>
            </Lap>
        </Activity>
    </Activities>
</TrainingCenterDatabase>
"""


@pytest.fixture()
def tcx_with_heart_rate_and_cadence() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
  xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
  xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
  xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
  xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
  xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1"
>
    <Activities>
        <Activity Sport="Biking">
            <Id>2018-03-13T12:44:45Z</Id>
            <Lap StartTime="2018-03-13T12:44:45Z">
                <Track>
                    <Trackpoint>
                      <Time>2018-03-13T12:44:45Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68095000</LatitudeDegrees>
                        <LongitudeDegrees>6.073670000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>997.00000</AltitudeMeters>
                      <DistanceMeters>0.000</DistanceMeters>
                      <HeartRateBpm>
                        <Value>92</Value>
                      </HeartRateBpm>
                      <Cadence>0</Cadence>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:44:50Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68091000</LatitudeDegrees>
                        <LongitudeDegrees>6.073670000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>996.00000</AltitudeMeters>
                      <DistanceMeters>4.449</DistanceMeters>
                      <HeartRateBpm>
                        <Value>87</Value>
                      </HeartRateBpm>
                      <Cadence>50</Cadence>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:00Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68080000</LatitudeDegrees>
                        <LongitudeDegrees>6.073640000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>996.00000</AltitudeMeters>
                      <DistanceMeters>16.908</DistanceMeters>
                      <HeartRateBpm>
                        <Value>88</Value>
                      </HeartRateBpm>
                      <Cadence>51</Cadence>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:05Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68075000</LatitudeDegrees>
                        <LongitudeDegrees>6.073640000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>996.00000</AltitudeMeters>
                      <DistanceMeters>22.467</DistanceMeters>
                      <HeartRateBpm>
                        <Value>90</Value>
                      </HeartRateBpm>
                      <Cadence>54</Cadence>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:10Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68071000</LatitudeDegrees>
                        <LongitudeDegrees>6.073640000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>996.00000</AltitudeMeters>
                      <DistanceMeters>26.914</DistanceMeters>
                      <HeartRateBpm>
                        <Value>87</Value>
                      </HeartRateBpm>
                      <Cadence>53</Cadence>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:30Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68049000</LatitudeDegrees>
                        <LongitudeDegrees>6.073610000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>995.00000</AltitudeMeters>
                      <DistanceMeters>51.492</DistanceMeters>
                      <HeartRateBpm>
                        <Value>85</Value>
                      </HeartRateBpm>
                      <Cadence>54</Cadence>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:55Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68019000</LatitudeDegrees>
                        <LongitudeDegrees>6.073560000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>993.00000</AltitudeMeters>
                      <DistanceMeters>85.083</DistanceMeters>
                      <HeartRateBpm>
                        <Value>86</Value>
                      </HeartRateBpm>
                      <Cadence>54</Cadence>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:46:00Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68014000</LatitudeDegrees>
                        <LongitudeDegrees>6.073550000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>992.00000</AltitudeMeters>
                      <DistanceMeters>90.698</DistanceMeters>
                      <HeartRateBpm>
                        <Value>84</Value>
                      </HeartRateBpm>
                      <Cadence>55</Cadence>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:46:15Z</Time>
                      <Position>
                        <LatitudeDegrees>44.67995000</LatitudeDegrees>
                        <LongitudeDegrees>6.073580000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>991.00000</AltitudeMeters>
                      <DistanceMeters>111.958</DistanceMeters>
                      <HeartRateBpm>
                        <Value>86</Value>
                      </HeartRateBpm>
                      <Cadence>53</Cadence>
                    </Trackpoint>
                </Track>
            </Lap>
        </Activity>
    </Activities>
</TrainingCenterDatabase>
"""


@pytest.fixture()
def tcx_with_heart_rate_and_ns3_run_cadence() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
  xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
  xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
  xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
  xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
  xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1"
>
    <Activities>
        <Activity Sport="Running">
            <Id>2018-03-13T12:44:45Z</Id>
            <Lap StartTime="2018-03-13T12:44:45Z">
                <Track>
                    <Trackpoint>
                      <Time>2018-03-13T12:44:45Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68095000</LatitudeDegrees>
                        <LongitudeDegrees>6.073670000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>997.00000</AltitudeMeters>
                      <DistanceMeters>0.000</DistanceMeters>
                      <HeartRateBpm>
                        <Value>92</Value>
                      </HeartRateBpm>                      
                      <Extensions>
                        <ns3:TPX>
                          <ns3:RunCadence>0</ns3:RunCadence>
                        </ns3:TPX>
                      </Extensions>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:44:50Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68091000</LatitudeDegrees>
                        <LongitudeDegrees>6.073670000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>996.00000</AltitudeMeters>
                      <DistanceMeters>4.449</DistanceMeters>
                      <HeartRateBpm>
                        <Value>87</Value>
                      </HeartRateBpm>
                      <Extensions>
                        <ns3:TPX>
                          <ns3:RunCadence>50</ns3:RunCadence>
                        </ns3:TPX>
                      </Extensions>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:00Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68080000</LatitudeDegrees>
                        <LongitudeDegrees>6.073640000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>996.00000</AltitudeMeters>
                      <DistanceMeters>16.908</DistanceMeters>
                      <HeartRateBpm>
                        <Value>88</Value>
                      </HeartRateBpm>
                      <Extensions>
                        <ns3:TPX>
                          <ns3:RunCadence>51</ns3:RunCadence>
                        </ns3:TPX>
                      </Extensions>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:05Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68075000</LatitudeDegrees>
                        <LongitudeDegrees>6.073640000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>996.00000</AltitudeMeters>
                      <DistanceMeters>22.467</DistanceMeters>
                      <HeartRateBpm>
                        <Value>90</Value>
                      </HeartRateBpm>
                      <Extensions>
                        <ns3:TPX>
                          <ns3:RunCadence>54</ns3:RunCadence>
                        </ns3:TPX>
                      </Extensions>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:10Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68071000</LatitudeDegrees>
                        <LongitudeDegrees>6.073640000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>996.00000</AltitudeMeters>
                      <DistanceMeters>26.914</DistanceMeters>
                      <HeartRateBpm>
                        <Value>87</Value>
                      </HeartRateBpm>
                      <Extensions>
                        <ns3:TPX>
                          <ns3:RunCadence>53</ns3:RunCadence>
                        </ns3:TPX>
                      </Extensions>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:30Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68049000</LatitudeDegrees>
                        <LongitudeDegrees>6.073610000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>995.00000</AltitudeMeters>
                      <DistanceMeters>51.492</DistanceMeters>
                      <HeartRateBpm>
                        <Value>85</Value>
                      </HeartRateBpm>
                      <Extensions>
                        <ns3:TPX>
                          <ns3:RunCadence>54</ns3:RunCadence>
                        </ns3:TPX>
                      </Extensions>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:45:55Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68019000</LatitudeDegrees>
                        <LongitudeDegrees>6.073560000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>993.00000</AltitudeMeters>
                      <DistanceMeters>85.083</DistanceMeters>
                      <HeartRateBpm>
                        <Value>86</Value>
                      </HeartRateBpm>
                      <Extensions>
                        <ns3:TPX>
                          <ns3:RunCadence>54</ns3:RunCadence>
                        </ns3:TPX>
                      </Extensions>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:46:00Z</Time>
                      <Position>
                        <LatitudeDegrees>44.68014000</LatitudeDegrees>
                        <LongitudeDegrees>6.073550000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>992.00000</AltitudeMeters>
                      <DistanceMeters>90.698</DistanceMeters>
                      <HeartRateBpm>
                        <Value>84</Value>
                      </HeartRateBpm>
                      <Extensions>
                        <ns3:TPX>
                          <ns3:RunCadence>55</ns3:RunCadence>
                        </ns3:TPX>
                      </Extensions>
                    </Trackpoint>
                    <Trackpoint>
                      <Time>2018-03-13T12:46:15Z</Time>
                      <Position>
                        <LatitudeDegrees>44.67995000</LatitudeDegrees>
                        <LongitudeDegrees>6.073580000</LongitudeDegrees>
                      </Position>
                      <AltitudeMeters>991.00000</AltitudeMeters>
                      <DistanceMeters>111.958</DistanceMeters>
                      <HeartRateBpm>
                        <Value>86</Value>
                      </HeartRateBpm>
                      <Extensions>
                        <ns3:TPX>
                          <ns3:RunCadence>53</ns3:RunCadence>
                        </ns3:TPX>
                      </Extensions>
                    </Trackpoint>
                </Track>
            </Lap>
        </Activity>
    </Activities>
</TrainingCenterDatabase>
"""


@pytest.fixture()
def tcx_with_heart_rate_and_run_cadence(
    tcx_with_heart_rate_and_ns3_run_cadence: str,
) -> str:
    return tcx_with_heart_rate_and_ns3_run_cadence.replace("ns3:", "")


@pytest.fixture()
def tcx_without_coordinates(
    tcx_with_one_lap_and_one_track: str,
) -> str:
    return re.sub(
        r"<Position>([\r\n\W\S]*)</Position>",
        "",
        tcx_with_one_lap_and_one_track,
    )
