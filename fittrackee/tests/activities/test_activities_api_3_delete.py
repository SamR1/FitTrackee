import json
import os
from uuid import uuid4

from fittrackee.activities.models import Activity
from fittrackee.activities.utils import get_absolute_file_path

from .utils import post_an_activity


def get_gpx_filepath(activity_id):
    activity = Activity.query.filter_by(id=activity_id).first()
    return activity.gpx


class TestDeleteActivityWithGpx:
    def test_it_deletes_an_activity_with_gpx(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        token, activity_uuid = post_an_activity(app, gpx_file)
        client = app.test_client()

        response = client.delete(
            f'/api/activities/{activity_uuid}',
            headers=dict(Authorization=f'Bearer {token}'),
        )

        assert response.status_code == 204

    def test_it_returns_403_when_deleting_an_activity_from_different_user(
        self, app, user_1, user_2, sport_1_cycling, gpx_file
    ):
        _, activity_uuid = post_an_activity(app, gpx_file)
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='toto@toto.com', password='87654321')),
            content_type='application/json',
        )

        response = client.delete(
            f'/api/activities/{activity_uuid}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 403
        assert 'error' in data['status']
        assert 'You do not have permissions.' in data['message']

    def test_it_returns_404_if_activity_does_not_exist(self, app, user_1):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.delete(
            f'/api/activities/{uuid4().hex}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']

    def test_it_returns_500_when_deleting_an_activity_with_gpx_invalid_file(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        token, activity_uuid = post_an_activity(app, gpx_file)
        client = app.test_client()
        gpx_filepath = get_gpx_filepath(1)
        gpx_filepath = get_absolute_file_path(gpx_filepath)
        os.remove(gpx_filepath)

        response = client.delete(
            f'/api/activities/{activity_uuid}',
            headers=dict(Authorization=f'Bearer {token}'),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 500
        assert 'error' in data['status']
        assert (
            'Error. Please try again or contact the administrator.'
            in data['message']
        )


class TestDeleteActivityWithoutGpx:
    def test_it_deletes_an_activity_wo_gpx(
        self, app, user_1, sport_1_cycling, activity_cycling_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.delete(
            f'/api/activities/{activity_cycling_user_1.uuid}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        assert response.status_code == 204

    def test_it_returns_403_when_deleting_an_activity_from_different_user(
        self, app, user_1, user_2, sport_1_cycling, activity_cycling_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='toto@toto.com', password='87654321')),
            content_type='application/json',
        )
        response = client.delete(
            f'/api/activities/{activity_cycling_user_1.uuid}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 403
        assert 'error' in data['status']
        assert 'You do not have permissions.' in data['message']
