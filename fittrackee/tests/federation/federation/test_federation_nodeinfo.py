import json

from flask import Flask

from fittrackee import VERSION
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ...mixins import ApiTestCaseMixin


class TestWellKnowNodeInfo(ApiTestCaseMixin):
    def test_it_returns_error_if_federation_is_disabled(
        self, app: Flask
    ) -> None:
        client = app.test_client()
        response = client.get(
            '/.well-known/nodeinfo',
            content_type='application/json',
        )

        self.assert_403(
            response,
            'error, federation is disabled for this instance',
        )

    def test_it_returns_instance_nodeinfo_url_if_federation_is_enabled(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        client = app_with_federation.test_client()
        response = client.get(
            '/.well-known/nodeinfo',
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        nodeinfo_url = (
            f'https://{app_with_federation.config["AP_DOMAIN"]}/nodeinfo/2.0'
        )
        assert data == {
            'links': [
                {
                    'rel': 'http://nodeinfo.diaspora.software/ns/schema/2.0',
                    'href': nodeinfo_url,
                }
            ]
        }

    def test_it_returns_error_if_domain_does_not_exist(
        self, app_wo_domain: Flask
    ) -> None:
        client = app_wo_domain.test_client()

        response = client.get(
            '/.well-known/nodeinfo',
            content_type='application/json',
        )

        self.assert_500(response)


class TestNodeInfo(ApiTestCaseMixin):
    def test_it_returns_error_if_federation_is_disabled(
        self, app: Flask
    ) -> None:
        client = app.test_client()
        response = client.get(
            '/nodeinfo/2.0',
            content_type='application/json',
        )

        self.assert_403(
            response,
            'error, federation is disabled for this instance',
        )

    def test_it_returns_instance_nodeinfo_if_federation_is_enabled(
        self,
        app_with_federation: Flask,
        user_1: User,
    ) -> None:
        client = app_with_federation.test_client()
        response = client.get(
            '/nodeinfo/2.0',
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            'version': '2.0',
            'software': {'name': 'fittrackee', 'version': VERSION},
            'protocols': ['activitypub'],
            'usage': {'users': {'total': 1}, 'localWorkouts': 0},
            'openRegistrations': True,
        }

    def test_it_displays_workouts_count(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client = app_with_federation.test_client()
        response = client.get(
            '/nodeinfo/2.0',
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['usage']['localWorkouts'] == 1

    def test_only_local_actors_are_counted(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        client = app_with_federation.test_client()
        response = client.get(
            '/nodeinfo/2.0',
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())

        assert data['usage']['users']['total'] == 1

    def test_it_displays_if_registration_is_disabled(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        app_with_federation.config['is_registration_enabled'] = False
        client = app_with_federation.test_client()
        response = client.get(
            '/nodeinfo/2.0',
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['openRegistrations'] is False
