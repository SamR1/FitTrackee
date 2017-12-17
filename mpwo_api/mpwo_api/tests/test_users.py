import json

from mpwo_api.tests.base import BaseTestCase
from mpwo_api.tests.utils import add_user
from mpwo_api.users.models import User


class TestUserService(BaseTestCase):
    """Tests for the Users Service."""

    def test_users(self):
        """ => Ensure the /ping route behaves correctly."""
        response = self.client.get('/api/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_single_user(self):
        """=> Get single user details"""
        user = add_user('test', 'test@test.com', 'test')

        with self.client:
            response = self.client.get(f'/api/users/{user.id}')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])

            self.assertTrue('created_at' in data['data'])
            self.assertIn('test', data['data']['username'])
            self.assertIn('test@test.com', data['data']['email'])

    def test_single_user_no_id(self):
        """=> Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get(f'/api/users/blah')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertIn('fail', data['status'])
            self.assertIn('User does not exist', data['message'])

    def test_single_user_wrong_id(self):
        """=> Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get(f'/api/users/99999999999')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertIn('fail', data['status'])
            self.assertIn('User does not exist', data['message'])

    def test_users_list(self):
        """=> Ensure get single user behaves correctly."""
        add_user('test', 'test@test.com', 'test')
        add_user('toto', 'toto@toto.com', 'toto')
        with self.client:
            response = self.client.get('/api/users')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])

            self.assertEqual(len(data['data']['users']), 2)
            self.assertTrue('created_at' in data['data']['users'][0])
            self.assertTrue('created_at' in data['data']['users'][1])
            self.assertIn('test', data['data']['users'][0]['username'])
            self.assertIn('toto', data['data']['users'][1]['username'])
            self.assertIn('test@test.com', data['data']['users'][0]['email'])
            self.assertIn('toto@toto.com', data['data']['users'][1]['email'])

    def test_encode_auth_token(self):
        """=> Ensure correct auth token generation"""
        user = add_user('test', 'test@test.com', 'test')
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        user = add_user('test', 'test@test.com', 'test')
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(User.decode_auth_token(auth_token), user.id)
