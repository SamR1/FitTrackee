import json
import time
from io import BytesIO

from mpwo_api.tests.base import BaseTestCase
from mpwo_api.tests.utils import add_user, add_user_full


class TestAuthBlueprint(BaseTestCase):

    def test_user_registration(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    username='justatest',
                    email='test@test.com',
                    password='12345678',
                    password_conf='12345678'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_user_registration_user_already_exists(self):
        add_user('test', 'test@test.com', '12345678')
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    username='test',
                    email='test@test.com',
                    password='12345678',
                    password_conf='12345678'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(
                data['message'] == 'Sorry. That user already exists.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_user_registration_invalid_short_username(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    username='t',
                    email='test@test.com',
                    password='12345678',
                    password_conf='12345678'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(
                data['message'] == "Errors: Username: 3 to 12 characters required.\n")
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_user_registration_invalid_long_username(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    username='testestestestestest',
                    email='test@test.com',
                    password='12345678',
                    password_conf='12345678'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(
                data['message'] == "Errors: Username: 3 to 12 characters required.\n")
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_user_registration_invalid_email(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    username='test',
                    email='test@test',
                    password='12345678',
                    password_conf='12345678'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(
                data['message'] == "Errors: Valid email must be provided.\n")
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_user_registration_invalid_short_password(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    username='test',
                    email='test@test.com',
                    password='1234567',
                    password_conf='1234567'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(
                data['message'] == "Errors: Password: 8 characters required.\n")
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_user_registration_mismatched_password(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    username='test',
                    email='test@test.com',
                    password='12345678',
                    password_conf='87654321'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(
                data['message'] == "Errors: Password and password confirmation don\'t match.\n")
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_user_registration_invalid_json(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict()),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_user_registration_invalid_json_keys_no_username(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678',
                    password_conf='12345678')),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_user_registration_invalid_json_keys_no_email(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    username='test',
                    password='12345678',
                    password_conf='12345678')),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_user_registration_invalid_json_keys_no_password(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    username='test',
                    email='test@test.com',
                    password_conf='12345678')),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_user_registration_invalid_json_keys_no_password_conf(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps(dict(
                    username='test',
                    email='test@test.com',
                    password='12345678')),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_registered_user_login(self):
        with self.client:
            add_user('test', 'test@test.com', '12345678')
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_no_registered_user_login(self):
        with self.client:
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(data['message'] == 'Invalid credentials.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_registered_user_login_invalid_password(self):
        add_user('test', 'test@test.com', '12345678')
        with self.client:
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='123456789'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(data['message'] == 'Invalid credentials.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_valid_logout(self):
        add_user('test', 'test@test.com', '12345678')
        with self.client:
            # user login
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678'
                )),
                content_type='application/json'
            )
            # valid token logout
            response = self.client.get(
                '/api/auth/logout',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

    def test_invalid_logout_expired_token(self):
        add_user('test', 'test@test.com', '12345678')
        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678'
                )),
                content_type='application/json'
            )
            # invalid token logout
            time.sleep(4)
            response = self.client.get(
                '/api/auth/logout',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(
                data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout(self):
        with self.client:
            response = self.client.get(
                '/api/auth/logout',
                headers=dict(Authorization='Bearer invalid'))
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(
                data['message'] == 'Invalid token. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_user_profile_minimal(self):
        add_user('test', 'test@test.com', '12345678')
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
                '/api/auth/profile',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['data'] is not None)
            self.assertTrue(data['data']['username'] == 'test')
            self.assertTrue(data['data']['email'] == 'test@test.com')
            self.assertTrue(data['data']['created_at'])
            self.assertFalse(data['data']['admin'])
            self.assertEqual(response.status_code, 200)

    def test_user_profile_full(self):
        add_user_full('test', 'test@test.com', '12345678')
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
                '/api/auth/profile',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['data'] is not None)
            self.assertTrue(data['data']['username'] == 'test')
            self.assertTrue(data['data']['email'] == 'test@test.com')
            self.assertTrue(data['data']['created_at'])
            self.assertFalse(data['data']['admin'])
            self.assertTrue(data['data']['first_name'] == 'John')
            self.assertTrue(data['data']['last_name'] == 'Doe')
            self.assertTrue(data['data']['birth_date'])
            self.assertTrue(data['data']['bio'] == 'just a random guy')
            self.assertTrue(data['data']['location'] == 'somewhere')
            self.assertEqual(response.status_code, 200)

    def test_invalid_profile(self):
        with self.client:
            response = self.client.get(
                '/api/auth/profile',
                headers=dict(Authorization='Bearer invalid'))
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(
                data['message'] == 'Invalid token. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_user_profile_valid_update(self):
        add_user('test', 'test@test.com', '12345678')
        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/api/auth/profile/edit',
                content_type='application/json',
                data=json.dumps(dict(
                    first_name='John',
                    last_name='Doe',
                    location='Somewhere',
                    bio='just a random guy',
                    birth_date='01/01/1980'
                )),
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User profile updated.')
            self.assertEqual(response.status_code, 200)

    def test_user_profile_valid_update_with_one_field(self):
        add_user('test', 'test@test.com', '12345678')
        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/api/auth/profile/edit',
                content_type='application/json',
                data=json.dumps(dict(
                    first_name='John'
                )),
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User profile updated.')
            self.assertEqual(response.status_code, 200)

    def test_user_profile_update_invalid_json(self):
        add_user('test', 'test@test.com', '12345678')
        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/api/auth/profile/edit',
                content_type='application/json',
                data=json.dumps(dict()),
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_update_user_picture(self):
        add_user('test', 'test@test.com', '12345678')

        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='12345678'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/api/auth/picture',
                data=dict(
                    file=(BytesIO(b'avatar'), 'avatar.png')
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    authorization='Bearer ' +
                    json.loads(resp_login.data.decode())['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User picture updated.')
            self.assertEqual(response.status_code, 200)
