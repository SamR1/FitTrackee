from datetime import datetime, timedelta
from typing import Dict

import pytest
from flask import Flask
from freezegun import freeze_time

from fittrackee import db
from fittrackee.tests.utils import random_int, random_string
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import (
    BlacklistedToken,
    User,
    UserDataExport,
    UserSportPreference,
)
from fittrackee.workouts.models import Sport, Workout


class TestUserModel:
    def test_it_returns_username_in_string_value(
        self, app: Flask, user_1: User
    ) -> None:
        assert '<User \'test\'>' == str(user_1)


class UserModelAssertMixin:
    @staticmethod
    def assert_user_account(serialized_user: Dict, user: User) -> None:
        assert serialized_user['admin'] == user.admin
        assert serialized_user['email_to_confirm'] == user.email_to_confirm
        assert serialized_user['is_active'] == user.is_active
        assert serialized_user['username'] == user.username

    @staticmethod
    def assert_user_profile(serialized_user: Dict, user: User) -> None:
        assert serialized_user['bio'] == user.bio
        assert serialized_user['birth_date'] == user.birth_date
        assert serialized_user['first_name'] == user.first_name
        assert serialized_user['last_name'] == user.last_name
        assert serialized_user['location'] == user.location
        assert serialized_user['picture'] is False

    @staticmethod
    def assert_workouts_keys_are_present(serialized_user: Dict) -> None:
        assert 'nb_sports' in serialized_user
        assert 'nb_workouts' in serialized_user
        assert 'records' in serialized_user
        assert 'sports_list' in serialized_user
        assert 'total_ascent' in serialized_user
        assert 'total_distance' in serialized_user
        assert 'total_duration' in serialized_user


class TestUserSerializeAsAuthUser(UserModelAssertMixin):
    def test_it_returns_user_account_infos(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(user_1)

        self.assert_user_account(serialized_user, user_1)

    def test_it_returns_user_profile_infos(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(user_1)

        self.assert_user_profile(serialized_user, user_1)

    def test_it_returns_user_preferences(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(user_1)

        assert serialized_user['imperial_units'] == user_1.imperial_units
        assert serialized_user['language'] == user_1.language
        assert serialized_user['timezone'] == user_1.timezone
        assert serialized_user['weekm'] == user_1.weekm
        assert serialized_user['display_ascent'] == user_1.display_ascent
        assert (
            serialized_user['start_elevation_at_zero']
            == user_1.start_elevation_at_zero
        )
        assert serialized_user['use_raw_gpx_speed'] == user_1.use_raw_gpx_speed
        assert serialized_user['use_dark_mode'] == user_1.use_dark_mode

    def test_it_returns_workouts_infos(self, app: Flask, user_1: User) -> None:
        serialized_user = user_1.serialize(user_1)

        self.assert_workouts_keys_are_present(serialized_user)

    def test_it_returns_user_did_not_accept_default_privacy_policy(
        self, app: Flask, user_1: User
    ) -> None:
        # default privacy policy
        app.config['privacy_policy_date'] = None
        user_1.accepted_policy_date = None
        serialized_user = user_1.serialize(user_1)

        assert serialized_user['accepted_privacy_policy'] is False

    def test_it_returns_user_did_accept_default_privacy_policy(
        self, app: Flask, user_1: User
    ) -> None:
        # default privacy policy
        app.config['privacy_policy_date'] = None
        user_1.accepted_policy_date = datetime.utcnow()
        serialized_user = user_1.serialize(user_1)

        assert serialized_user['accepted_privacy_policy'] is True

    def test_it_returns_user_did_not_accept_last_policy(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.accepted_policy_date = datetime.utcnow()
        # custom privacy policy
        app.config['privacy_policy_date'] = datetime.utcnow()
        serialized_user = user_1.serialize(user_1)

        assert serialized_user['accepted_privacy_policy'] is False

    def test_it_returns_user_did_accept_last_policy(
        self, app: Flask, user_1: User
    ) -> None:
        # custom privacy policy
        app.config['privacy_policy_date'] = datetime.utcnow()
        user_1.accepted_policy_date = datetime.utcnow()
        serialized_user = user_1.serialize(user_1)

        assert serialized_user['accepted_privacy_policy'] is True

    def test_it_does_not_return_confirmation_token(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(user_1_admin)

        assert 'confirmation_token' not in serialized_user


class TestUserSerializeAsAdmin(UserModelAssertMixin):
    def test_it_returns_user_account_infos(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(user_1_admin)

        self.assert_user_account(serialized_user, user_2)

    def test_it_returns_user_profile_infos(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(user_1_admin)

        self.assert_user_profile(serialized_user, user_1_admin)

    def test_it_does_return_user_preferences(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(user_1_admin)

        assert 'imperial_units' not in serialized_user
        assert 'language' not in serialized_user
        assert 'timezone' not in serialized_user
        assert 'weekm' not in serialized_user
        assert 'start_elevation_at_zero' not in serialized_user
        assert 'use_raw_gpx_speed' not in serialized_user
        assert 'use_dark_mode' not in serialized_user

    def test_it_returns_workouts_infos(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(user_1_admin)

        self.assert_workouts_keys_are_present(serialized_user)

    def test_it_does_not_return_accepted_privacy_policy_date(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(user_1_admin)

        assert 'accepted_privacy_policy' not in serialized_user

    def test_it_does_not_return_confirmation_token(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(user_1_admin)

        assert 'confirmation_token' not in serialized_user


class TestInactiveUserSerialize(UserModelAssertMixin):
    def test_it_returns_is_active_to_false_for_inactive_user(
        self,
        app: Flask,
        inactive_user: User,
    ) -> None:
        serialized_user = inactive_user.serialize(inactive_user)

        assert serialized_user['is_active'] is False


class TestUserSerializeAsRegularUser(UserModelAssertMixin):
    def test_user_model_as_regular_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        with pytest.raises(UserNotFoundException):
            user_2.serialize(user_1)


class TestUserRecords(UserModelAssertMixin):
    def test_it_returns_empty_list_when_no_workouts(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        serialized_user = user_1.serialize(user_1)

        assert serialized_user['records'] == []

    def test_it_returns_user_records(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize(user_1)
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

    def test_it_returns_totals_when_user_has_workout_without_ascent(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize(user_1)
        assert serialized_user['total_ascent'] == 0
        assert serialized_user['total_distance'] == 10
        assert serialized_user['total_duration'] == '1:00:00'

    def test_it_returns_totals_when_user_has_workout_with_ascent(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.ascent = 100
        serialized_user = user_1.serialize(user_1)
        assert serialized_user['total_ascent'] == 100
        assert serialized_user['total_distance'] == 10
        assert serialized_user['total_duration'] == '1:00:00'

    def test_it_returns_totals_when_user_has_multiple_workouts(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.ascent = 100
        serialized_user = user_1.serialize(user_1)
        assert serialized_user['total_ascent'] == 100
        assert serialized_user['total_distance'] == 22
        assert serialized_user['total_duration'] == '2:40:00'


class TestUserWorkouts(UserModelAssertMixin):
    def test_it_returns_infos_when_no_workouts(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        serialized_user = user_1.serialize(user_1)

        assert serialized_user['nb_sports'] == 0
        assert serialized_user['nb_workouts'] == 0
        assert serialized_user['sports_list'] == []
        assert serialized_user['total_distance'] == 0
        assert serialized_user['total_duration'] == '0:00:00'

    def test_it_returns_infos_when_only_one_workout_exists(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize(user_1)

        assert serialized_user['nb_sports'] == 1
        assert serialized_user['nb_workouts'] == 1
        assert serialized_user['sports_list'] == [sport_1_cycling.id]
        assert (
            serialized_user['total_distance']
            == workout_cycling_user_1.distance
        )
        assert serialized_user['total_duration'] == str(
            workout_cycling_user_1.duration
        )

    def test_it_returns_infos_when_several_sports(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize(user_1)

        assert serialized_user['nb_sports'] == 2
        assert serialized_user['nb_workouts'] == 2
        assert serialized_user['sports_list'] == [
            sport_1_cycling.id,
            sport_2_running.id,
        ]
        assert serialized_user['total_distance'] == (
            workout_cycling_user_1.distance + workout_running_user_1.distance
        )
        assert serialized_user['total_duration'] == str(
            workout_cycling_user_1.duration + workout_running_user_1.duration
        )


class TestUserModelToken:
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

    def test_it_returns_error_when_token_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        assert (
            User.decode_auth_token(random_string())
            == 'invalid token, please log in again'
        )

    def test_it_returns_error_when_token_is_expired(
        self, app: Flask, user_1: User
    ) -> None:
        auth_token = user_1.encode_auth_token(user_1.id)
        now = datetime.utcnow()
        with freeze_time(now + timedelta(seconds=61)):
            assert (
                User.decode_auth_token(auth_token)
                == 'signature expired, please log in again'
            )

    def test_it_returns_error_when_token_is_blacklisted(
        self, app: Flask, user_1: User
    ) -> None:
        auth_token = user_1.encode_auth_token(user_1.id)
        db.session.add(BlacklistedToken(token=auth_token))
        db.session.commit()

        assert (
            User.decode_auth_token(auth_token)
            == 'blacklisted token, please log in again'
        )


class TestUserSportModel:
    def test_user_model(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_sport_1_preference: UserSportPreference,
    ) -> None:
        serialized_user_sport = user_sport_1_preference.serialize()
        assert serialized_user_sport['user_id'] == user_1.id
        assert serialized_user_sport['sport_id'] == sport_1_cycling.id
        assert serialized_user_sport['color'] is None
        assert serialized_user_sport['is_active']
        assert serialized_user_sport['stopped_speed_threshold'] == 1


class TestUserDataExportSerializer:
    def test_it_returns_ongoing_export(self, app: Flask, user_1: User) -> None:
        created_at = datetime.utcnow()
        data_export = UserDataExport(user_id=user_1.id, created_at=created_at)

        serialized_data_export = data_export.serialize()

        assert serialized_data_export["created_at"] == created_at
        assert serialized_data_export["status"] == "in_progress"
        assert serialized_data_export["file_name"] is None
        assert serialized_data_export["file_size"] is None

    def test_it_returns_successful_export(
        self, app: Flask, user_1: User
    ) -> None:
        created_at = datetime.utcnow()
        data_export = UserDataExport(user_id=user_1.id, created_at=created_at)
        data_export.completed = True
        data_export.file_name = random_string()
        data_export.file_size = random_int()

        serialized_data_export = data_export.serialize()

        assert serialized_data_export["created_at"] == created_at
        assert serialized_data_export["status"] == "successful"
        assert serialized_data_export["file_name"] == data_export.file_name
        assert serialized_data_export["file_size"] == data_export.file_size

    def test_it_returns_errored_export(self, app: Flask, user_1: User) -> None:
        created_at = datetime.utcnow()
        data_export = UserDataExport(user_id=user_1.id, created_at=created_at)
        data_export.completed = True

        serialized_data_export = data_export.serialize()

        assert serialized_data_export["created_at"] == created_at
        assert serialized_data_export["status"] == "errored"
        assert serialized_data_export["file_name"] is None
        assert serialized_data_export["file_size"] is None
