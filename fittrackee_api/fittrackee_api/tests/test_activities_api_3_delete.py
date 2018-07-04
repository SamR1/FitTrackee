import json
import os
from io import BytesIO

from fittrackee_api.activities.models import Activity
from fittrackee_api.activities.utils import get_absolute_file_path


def get_gpx_filepath(activity_id):
    activity = Activity.query.filter_by(id=activity_id).first()
    return activity.gpx


def test_delete_an_activity_with_gpx(app, user_1, sport_1_cycling, gpx_file):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    client.post(
        '/api/activities',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
            data='{"sport_id": 1}'
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    response = client.delete(
        '/api/activities/1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    assert response.status_code == 204


def test_delete_an_activity_with_gpx_different_user(
        app, user_1, user_2, sport_1_cycling, gpx_file):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    client.post(
        '/api/activities',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
            data='{"sport_id": 1}'
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='toto@toto.com',
            password='87654321'
        )),
        content_type='application/json'
    )
    response = client.delete(
        '/api/activities/1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 403
    assert 'error' in data['status']
    assert 'You do not have permissions.' in data['message']


def test_delete_an_activity_wo_gpx(
        app, user_1, sport_1_cycling, activity_cycling_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.delete(
        '/api/activities/1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    assert response.status_code == 204


def test_delete_an_activity_wo_gpx_different_user(
        app, user_1, user_2, sport_1_cycling, activity_cycling_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='toto@toto.com',
            password='87654321'
        )),
        content_type='application/json'
    )
    response = client.delete(
        '/api/activities/1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 403
    assert 'error' in data['status']
    assert 'You do not have permissions.' in data['message']


def test_delete_an_activity_no_activity(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.delete(
        '/api/activities/9999',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 404
    assert 'not found' in data['status']


def test_delete_an_activity_with_gpx_invalid_file(
        app, user_1, sport_1_cycling, gpx_file):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    client.post(
        '/api/activities',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
            data='{"sport_id": 1}'
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    gpx_filepath = get_gpx_filepath(1)
    gpx_filepath = get_absolute_file_path(gpx_filepath)
    os.remove(gpx_filepath)

    response = client.delete(
        '/api/activities/1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'Error. Please try again or contact the administrator.' \
           in data['message']
