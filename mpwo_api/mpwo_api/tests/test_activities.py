import datetime
import json

from mpwo_api.tests.base import BaseTestCase
from mpwo_api.tests.utils import add_activity, add_sport, add_user


class TestActivitiesService(BaseTestCase):
    """Tests for Activities."""

    def test_get_all_sports(self):
        add_user('test', 'test@test.com', '12345678')
        add_sport('cycling')
        add_sport('running')

        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678'
                )),
                content_type='application/json'
            )
            response = self.client.get(
                '/api/sports',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])

            self.assertEqual(len(data['data']['sports']), 2)
            self.assertIn('cycling', data['data']['sports'][0]['label'])
            self.assertIn('running', data['data']['sports'][1]['label'])

    def test_get_all_activities(self):
        add_user('test', 'test@test.com', '12345678')
        add_user('toto', 'toto@toto.com', '12345678')
        add_sport('cycling')
        add_sport('running')
        add_activity(
            1,
            2,
            datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
            datetime.timedelta(seconds=1024))
        add_activity(
            2,
            1,
            datetime.datetime.strptime('23/01/2018', '%d/%m/%Y'),
            datetime.timedelta(seconds=3600))

        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678'
                )),
                content_type='application/json'
            )
            response = self.client.get(
                '/api/activities',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertEqual(len(data['data']['activities']), 2)
            self.assertTrue('creation_date' in data['data']['activities'][0])
            self.assertTrue('creation_date' in data['data']['activities'][1])
            self.assertEqual('Tue, 23 Jan 2018 00:00:00 GMT',
                             data['data']['activities'][0][
                                 'activity_date'])
            self.assertEqual('Mon, 01 Jan 2018 00:00:00 GMT',
                             data['data']['activities'][1][
                                 'activity_date'])
            self.assertTrue('creation_date' in data['data']['activities'][1])
            self.assertEqual(2, data['data']['activities'][0]['user_id'])
            self.assertEqual(1, data['data']['activities'][1]['user_id'])
            self.assertEqual(1, data['data']['activities'][0]['sport_id'])
            self.assertEqual(2, data['data']['activities'][1]['sport_id'])
            self.assertEqual(3600, data['data']['activities'][0]['duration'])
            self.assertEqual(1024, data['data']['activities'][1]['duration'])
