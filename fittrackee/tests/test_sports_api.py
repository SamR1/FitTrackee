import json

expected_sport_1_cycling_result = {
    'id': 1,
    'label': 'Cycling',
    'img': None,
    'is_active': True,
}
expected_sport_1_cycling_admin_result = expected_sport_1_cycling_result.copy()
expected_sport_1_cycling_admin_result['has_activities'] = False

expected_sport_2_running_result = {
    'id': 2,
    'label': 'Running',
    'img': None,
    'is_active': True,
}
expected_sport_2_running_admin_result = expected_sport_2_running_result.copy()
expected_sport_2_running_admin_result['has_activities'] = False

expected_sport_1_cycling_inactive_result = {
    'id': 1,
    'label': 'Cycling',
    'img': None,
    'is_active': False,
}
expected_sport_1_cycling_inactive_admin_result = (
    expected_sport_1_cycling_inactive_result.copy()
)
expected_sport_1_cycling_inactive_admin_result['has_activities'] = False


class TestGetSports:
    def test_it_gets_all_sports(
        self, app, user_1, sport_1_cycling, sport_2_running
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/sports',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 2
        assert data['data']['sports'][0] == expected_sport_1_cycling_result
        assert data['data']['sports'][1] == expected_sport_2_running_result

    def test_it_gets_all_sports_with_inactive_one(
        self, app, user_1, sport_1_cycling_inactive, sport_2_running
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/sports',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 2
        assert (
            data['data']['sports'][0]
            == expected_sport_1_cycling_inactive_result
        )
        assert data['data']['sports'][1] == expected_sport_2_running_result

    def test_it_gets_all_sports_with_admin_rights(
        self, app, user_1_admin, sport_1_cycling_inactive, sport_2_running
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
            content_type='application/json',
        )

        response = client.get(
            '/api/sports',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 2
        assert (
            data['data']['sports'][0]
            == expected_sport_1_cycling_inactive_admin_result
        )
        assert (
            data['data']['sports'][1] == expected_sport_2_running_admin_result
        )


class TestGetSport:
    def test_it_gets_a_sport(self, app, user_1, sport_1_cycling):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/sports/1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0] == expected_sport_1_cycling_result

    def test_it_returns_404_if_sport_does_not_exist(self, app, user_1):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/sports/1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['sports']) == 0

    def test_it_gets_a_inactive_sport(
        self, app, user_1, sport_1_cycling_inactive
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.get(
            '/api/sports/1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']

        assert len(data['data']['sports']) == 1
        assert (
            data['data']['sports'][0]
            == expected_sport_1_cycling_inactive_result
        )

    def test_it_get_an_inactive_sport_with_admin_rights(
        self, app, user_1_admin, sport_1_cycling_inactive
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
            content_type='application/json',
        )
        response = client.get(
            '/api/sports/1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']

        assert len(data['data']['sports']) == 1
        assert (
            data['data']['sports'][0]
            == expected_sport_1_cycling_inactive_admin_result
        )


class TestUpdateSport:
    def test_it_disables_a_sport(self, app, user_1_admin, sport_1_cycling):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
            content_type='application/json',
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=False)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0]['is_active'] is False
        assert data['data']['sports'][0]['has_activities'] is False

    def test_it_enables_a_sport(self, app, user_1_admin, sport_1_cycling):
        sport_1_cycling.is_active = False
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
            content_type='application/json',
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=True)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0]['is_active'] is True
        assert data['data']['sports'][0]['has_activities'] is False

    def test_it_disables_a_sport_with_activities(
        self, app, user_1_admin, sport_1_cycling, activity_cycling_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
            content_type='application/json',
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=False)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0]['is_active'] is False
        assert data['data']['sports'][0]['has_activities'] is True

    def test_it_enables_a_sport_with_activities(
        self, app, user_1_admin, sport_1_cycling, activity_cycling_user_1
    ):
        sport_1_cycling.is_active = False
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
            content_type='application/json',
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=True)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0]['is_active'] is True
        assert data['data']['sports'][0]['has_activities'] is True

    def test_returns_error_if_user_has_no_admin_rights(
        self, app, user_1, sport_1_cycling
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=False)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 403
        assert 'success' not in data['status']
        assert 'error' in data['status']
        assert 'You do not have permissions.' in data['message']

    def test_returns_error_if_payload_is_invalid(self, app, user_1_admin):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
            content_type='application/json',
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert 'Invalid payload.' in data['message']

    def test_it_returns_error_if_sport_does_not_exist(self, app, user_1_admin):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
            content_type='application/json',
        )
        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=False)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['sports']) == 0
