from fittrackee_api.users.models import User


class TestUserModel:
    def test_user_model(self, app, user_1):
        assert '<User \'test\'>' == str(user_1)

        serialized_user = user_1.serialize()
        assert 'test' == serialized_user['username']
        assert 'created_at' in serialized_user
        assert serialized_user['admin'] is False
        assert serialized_user['first_name'] is None
        assert serialized_user['last_name'] is None
        assert serialized_user['bio'] is None
        assert serialized_user['location'] is None
        assert serialized_user['birth_date'] is None
        assert serialized_user['picture'] is False
        assert serialized_user['timezone'] is None
        assert serialized_user['weekm'] is False
        assert serialized_user['language'] is None
        assert serialized_user['nb_activities'] == 0
        assert serialized_user['nb_sports'] == 0
        assert serialized_user['total_distance'] == 0
        assert serialized_user['total_duration'] == '0:00:00'

    def test_encode_auth_token(self, app, user_1):
        auth_token = user_1.encode_auth_token(user_1.id)
        assert isinstance(auth_token, bytes)

    def test_encode_password_token(self, app, user_1):
        password_token = user_1.encode_password_reset_token(user_1.id)
        assert isinstance(password_token, bytes)

    def test_decode_auth_token(self, app, user_1):
        auth_token = user_1.encode_auth_token(user_1.id)
        assert isinstance(auth_token, bytes)
        assert User.decode_auth_token(auth_token) == user_1.id
