import datetime
import os

import pytest
from mpwo_api import create_app, db
from mpwo_api.activities.models import Activity, Record, Sport
from mpwo_api.users.models import User

os.environ["FLASK_ENV"] = 'testing'
os.environ["APP_SETTINGS"] = 'mpwo_api.config.TestingConfig'


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        return app


@pytest.fixture()
def user_1():
    user = User(username='test', email='test@test.com', password='12345678')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_admin():
    admin = User(
        username='admin',
        email='admin@example.com',
        password='12345678'
    )
    admin.admin = True
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture()
def user_1_full():
    user = User(username='test', email='test@test.com', password='12345678')
    user.first_name = 'John'
    user.last_name = 'Doe'
    user.bio = 'just a random guy'
    user.location = 'somewhere'
    user.birth_date = datetime.datetime.strptime('01/01/1980', '%d/%m/%Y')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2():
    user = User(username='toto', email='toto@toto.com', password='87654321')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def sport_1_cycling():
    sport = Sport(label='Cycling')
    db.session.add(sport)
    db.session.commit()
    return sport


@pytest.fixture()
def sport_2_running():
    sport = Sport(label='Running')
    db.session.add(sport)
    db.session.commit()
    return sport


@pytest.fixture()
def activity_cycling_user_1():
    activity = Activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    db.session.add(activity)
    db.session.commit()
    return activity


@pytest.fixture()
def activity_running_user_1():
    activity = Activity(
        user_id=1,
        sport_id=2,
        activity_date=datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        distance=12,
        duration=datetime.timedelta(seconds=6000)
    )
    db.session.add(activity)
    db.session.commit()
    return activity


@pytest.fixture()
def seven_activities_user_1():
    activity = Activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    db.session.add(activity)
    activity = Activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        distance=8,
        duration=datetime.timedelta(seconds=6000)
    )
    db.session.add(activity)
    activity = Activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('20/03/2017', '%d/%m/%Y'),
        distance=5,
        duration=datetime.timedelta(seconds=1024)
    )
    db.session.add(activity)
    activity = Activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('09/05/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=3000)
    )
    db.session.add(activity)
    activity = Activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/06/2017', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=3456)
    )
    db.session.add(activity)
    activity = Activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('23/02/2018', '%d/%m/%Y'),
        distance=1,
        duration=datetime.timedelta(seconds=600)
    )
    db.session.add(activity)
    activity = Activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('23/02/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1000)
    )
    db.session.add(activity)
    db.session.commit()
    return activity


@pytest.fixture()
def activity_cycling_user_2():
    activity = Activity(
        user_id=2,
        sport_id=1,
        activity_date=datetime.datetime.strptime('23/01/2018', '%d/%m/%Y'),
        distance=15,
        duration=datetime.timedelta(seconds=3600)
    )
    db.session.add(activity)
    db.session.commit()
    return activity


@pytest.fixture()
def record_as(activity_cycling_user_1):
    record = Record(
        user_id=1,
        sport_id=1,
        activity=activity_cycling_user_1,
        record_type='AS')
    db.session.add(record)
    db.session.commit()
    return record


@pytest.fixture()
def record_fd(activity_cycling_user_1):
    record = Record(
        user_id=1,
        sport_id=1,
        activity=activity_cycling_user_1,
        record_type='FD')
    db.session.add(record)
    db.session.commit()
    return record


@pytest.fixture()
def record_fd_running(activity_running_user_1):
    record = Record(
        user_id=1,
        sport_id=2,
        activity=activity_running_user_1,
        record_type='FD')
    db.session.add(record)
    db.session.commit()
    return record


@pytest.fixture()
def record_ld(activity_cycling_user_1):
    record = Record(
        user_id=1,
        sport_id=1,
        activity=activity_cycling_user_1,
        record_type='LD')
    db.session.add(record)
    db.session.commit()
    return record


@pytest.fixture()
def record_ms(activity_cycling_user_1):
    record = Record(
        user_id=1,
        sport_id=1,
        activity=activity_cycling_user_1,
        record_type='MS')
    db.session.add(record)
    db.session.commit()
    return record


@pytest.fixture()
def record_ms_user_2_cycling(activity_cycling_user_2):
    record = Record(
        user_id=2,
        sport_id=1,
        activity=activity_cycling_user_2,
        record_type='MS')
    db.session.add(record)
    db.session.commit()
    return record


@pytest.fixture()
def gpx_file():
        return (
        '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        '  <metadata/>'
        '  <trk>'
        '    <name>just an activity</name>'
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
def gpx_file_wo_name():
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
def gpx_file_wo_track():
    return (
        '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
        '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
        '  <metadata/>'
        '</gpx>'
    )
