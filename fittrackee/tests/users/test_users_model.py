from flask import Flask

from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout


class TestUserModel:
    def test_user_model(self, app: Flask, user_1: User) -> None:
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
        assert serialized_user['nb_sports'] == 0
        assert serialized_user['nb_workouts'] == 0
        assert serialized_user['records'] == []
        assert serialized_user['sports_list'] == []
        assert serialized_user['total_distance'] == 0
        assert serialized_user['total_duration'] == '0:00:00'

    def test_encode_auth_token(self, app: Flask, user_1: User) -> None:
        auth_token = user_1.encode_auth_token(user_1.id)
        assert isinstance(auth_token, str)

    def test_encode_password_token(self, app: Flask, user_1: User) -> None:
        password_token = user_1.encode_password_reset_token(user_1.id)
        assert isinstance(password_token, str)

    def test_decode_auth_token(self, app: Flask, user_1: User) -> None:
        auth_token = user_1.encode_auth_token(user_1.id)
        assert isinstance(auth_token, str)
        assert User.decode_auth_token(auth_token) == user_1.id

    def test_it_returns_user_records(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize()
        assert len(serialized_user['records']) == 4
        assert serialized_user['records'][0]['record_type'] == 'AS'
        assert serialized_user['records'][0]['sport_id'] == sport_1_cycling.id
        assert serialized_user['records'][0]['user'] == user_1.username
        assert serialized_user['records'][0]['value'] > 0
        assert (
            serialized_user['records'][0]['workout_id']
            == workout_cycling_user_1.short_id
        )
        assert serialized_user['records'][0]['workout_date']
