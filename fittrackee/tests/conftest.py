import datetime
import os
from typing import Generator, Optional

import pytest
from fittrackee import create_app, db
from fittrackee.application.models import AppConfig
from fittrackee.application.utils import update_app_config_from_database
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout, WorkoutSegment

os.environ['FLASK_ENV'] = 'testing'
os.environ['APP_SETTINGS'] = 'fittrackee.config.TestingConfig'
# to avoid resetting dev database during tests
os.environ['DATABASE_URL'] = os.environ['DATABASE_TEST_URL']


def get_app_config(with_config: Optional[bool] = False) -> Optional[AppConfig]:
    if with_config:
        config = AppConfig()
        config.gpx_limit_import = 10
        config.max_single_file_size = 1 * 1024 * 1024
        config.max_zip_file_size = 1 * 1024 * 1024 * 10
        config.max_users = 100
        db.session.add(config)
        db.session.commit()
        return config
    else:
        return None


def get_app(with_config: Optional[bool] = False) -> Generator:
    app = create_app()
    with app.app_context():
        db.create_all()
        app_db_config = get_app_config(with_config)
        if app_db_config:
            update_app_config_from_database(app, app_db_config)
        yield app
        db.session.remove()
        db.drop_all()
        # close unused idle connections => avoid the following error:
        # FATAL: remaining connection slots are reserved for non-replication
        # superuser connections
        db.engine.dispose()
        return app


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv('EMAIL_URL', 'smtp://none:none@0.0.0.0:1025')
    if os.getenv('TILE_SERVER_URL'):
        monkeypatch.delenv('TILE_SERVER_URL')
    if os.getenv('MAP_ATTRIBUTION'):
        monkeypatch.delenv('MAP_ATTRIBUTION')
    yield from get_app(with_config=True)


@pytest.fixture
def app_no_config() -> Generator:
    yield from get_app(with_config=False)


@pytest.fixture
def app_ssl(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv('EMAIL_URL', 'smtp://none:none@0.0.0.0:1025?ssl=True')
    yield from get_app(with_config=True)


@pytest.fixture
def app_tls(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv('EMAIL_URL', 'smtp://none:none@0.0.0.0:1025?tls=True')
    yield from get_app(with_config=True)


@pytest.fixture()
def app_config() -> AppConfig:
    config = AppConfig()
    config.gpx_limit_import = 10
    config.max_single_file_size = 1048576
    config.max_zip_file_size = 10485760
    config.max_users = 0
    db.session.add(config)
    db.session.commit()
    return config


@pytest.fixture()
def user_1() -> User:
    user = User(username='test', email='test@test.com', password='12345678')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_admin() -> User:
    admin = User(
        username='admin', email='admin@example.com', password='12345678'
    )
    admin.admin = True
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture()
def user_1_full() -> User:
    user = User(username='test', email='test@test.com', password='12345678')
    user.first_name = 'John'
    user.last_name = 'Doe'
    user.bio = 'just a random guy'
    user.location = 'somewhere'
    user.language = 'en'
    user.timezone = 'America/New_York'
    user.birth_date = datetime.datetime.strptime('01/01/1980', '%d/%m/%Y')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_paris() -> User:
    user = User(username='test', email='test@test.com', password='12345678')
    user.timezone = 'Europe/Paris'
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2() -> User:
    user = User(username='toto', email='toto@toto.com', password='87654321')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2_admin() -> User:
    user = User(username='toto', email='toto@toto.com', password='87654321')
    user.admin = True
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_3() -> User:
    user = User(username='sam', email='sam@test.com', password='12345678')
    user.weekm = True
    db.session.add(user)
    db.session.commit()
    return user


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
