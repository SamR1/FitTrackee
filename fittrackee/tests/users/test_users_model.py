from datetime import datetime, timedelta
from typing import Dict
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from sqlalchemy.dialects.postgresql import insert
from time_machine import travel

from fittrackee import db
from fittrackee.administration.models import AdminAction
from fittrackee.equipments.models import Equipment
from fittrackee.federation.exceptions import FederationDisabledException
from fittrackee.tests.utils import random_int, random_string
from fittrackee.users.exceptions import (
    BlockUserException,
    FollowRequestAlreadyProcessedError,
    NotExistingFollowRequestError,
)
from fittrackee.users.models import (
    BlacklistedToken,
    BlockedUser,
    FollowRequest,
    Notification,
    User,
    UserDataExport,
    UserSportPreference,
    UserSportPreferenceEquipment,
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
        assert serialized_user['is_active'] == user.is_active
        assert serialized_user['username'] == user.username
        assert serialized_user['suspended_at'] is None

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
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        self.assert_user_account(serialized_user, user_1)
        assert serialized_user['email_to_confirm'] == user_1.email_to_confirm

    def test_it_returns_user_profile_infos(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        self.assert_user_profile(serialized_user, user_1)
        assert 'blocked' not in serialized_user

    def test_it_returns_user_preferences(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

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
        assert (
            serialized_user['workouts_visibility']
            == user_1.workouts_visibility
        )
        assert serialized_user['map_visibility'] == user_1.map_visibility
        assert (
            serialized_user['manually_approves_followers']
            == user_1.manually_approves_followers
        )
        assert (
            serialized_user['hide_profile_in_users_directory']
            == user_1.hide_profile_in_users_directory
        )

    def test_it_returns_workouts_infos(self, app: Flask, user_1: User) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        self.assert_workouts_keys_are_present(serialized_user)

    def test_it_returns_user_did_not_accept_default_privacy_policy(
        self, app: Flask, user_1: User
    ) -> None:
        # default privacy policy
        app.config['privacy_policy_date'] = None
        user_1.accepted_policy_date = None
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user['accepted_privacy_policy'] is False

    def test_it_returns_user_did_accept_default_privacy_policy(
        self, app: Flask, user_1: User
    ) -> None:
        # default privacy policy
        app.config['privacy_policy_date'] = None
        user_1.accepted_policy_date = datetime.utcnow()
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user['accepted_privacy_policy'] is True

    def test_it_returns_user_did_not_accept_last_policy(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.accepted_policy_date = datetime.utcnow()
        # custom privacy policy
        app.config['privacy_policy_date'] = datetime.utcnow()
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user['accepted_privacy_policy'] is False

    def test_it_returns_user_did_accept_last_policy(
        self, app: Flask, user_1: User
    ) -> None:
        # custom privacy policy
        app.config['privacy_policy_date'] = datetime.utcnow()
        user_1.accepted_policy_date = datetime.utcnow()
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user['accepted_privacy_policy'] is True

    def test_it_does_not_return_confirmation_token(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        assert 'confirmation_token' not in serialized_user


class TestUserSerializeAsAdmin(UserModelAssertMixin):
    def test_it_returns_user_account_infos(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        self.assert_user_account(serialized_user, user_2)
        assert serialized_user['email_to_confirm'] == user_2.email_to_confirm

    def test_it_returns_user_profile_infos(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        self.assert_user_profile(serialized_user, user_1_admin)
        assert serialized_user["blocked"] is False

    def test_it_does_return_user_preferences(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        assert 'imperial_units' not in serialized_user
        assert 'language' not in serialized_user
        assert 'timezone' not in serialized_user
        assert 'weekm' not in serialized_user
        assert 'start_elevation_at_zero' not in serialized_user
        assert 'use_raw_gpx_speed' not in serialized_user
        assert 'use_dark_mode' not in serialized_user
        assert 'workouts_visibility' not in serialized_user
        assert 'map_visibility' not in serialized_user
        assert 'manually_approves_followers' not in serialized_user
        assert 'hide_profile_in_users_directory' not in serialized_user

    def test_it_returns_workouts_infos(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        self.assert_workouts_keys_are_present(serialized_user)

    def test_it_does_not_return_accepted_privacy_policy_date(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        assert 'accepted_privacy_policy' not in serialized_user

    def test_it_does_not_return_confirmation_token(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        assert 'confirmation_token' not in serialized_user


class TestUserSerializeAsUser(UserModelAssertMixin):
    def test_it_returns_user_account_infos(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert serialized_user['admin'] == user_2.admin
        assert serialized_user['username'] == user_2.username
        assert 'email_to_confirm' not in serialized_user
        assert 'is_active' not in serialized_user

    def test_it_returns_user_profile_infos(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        self.assert_user_profile(serialized_user, user_1)
        assert serialized_user["blocked"] is False

    def test_it_does_return_user_preferences(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert 'imperial_units' not in serialized_user
        assert 'language' not in serialized_user
        assert 'timezone' not in serialized_user
        assert 'weekm' not in serialized_user
        assert 'workouts_visibility' not in serialized_user
        assert 'map_visibility' not in serialized_user
        assert 'manually_approves_followers' not in serialized_user
        assert 'hide_profile_in_users_directory' not in serialized_user

    def test_it_returns_workouts_infos(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        self.assert_workouts_keys_are_present(serialized_user)

    def test_it_does_not_return_confirmation_token(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        assert 'confirmation_token' not in serialized_user


class TestUserSerializeAsUnauthenticatedUser(UserModelAssertMixin):
    def test_it_returns_user_account_infos(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(light=False)

        assert serialized_user['admin'] == user_1.admin
        assert serialized_user['username'] == user_1.username
        assert 'blocked' not in serialized_user
        assert 'email_to_confirm' not in serialized_user
        assert 'is_active' not in serialized_user

    def test_it_returns_user_profile_infos(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(light=False)

        self.assert_user_profile(serialized_user, user_1)

    def test_it_does_return_user_preferences(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(light=False)

        assert 'imperial_units' not in serialized_user
        assert 'language' not in serialized_user
        assert 'timezone' not in serialized_user
        assert 'weekm' not in serialized_user
        assert 'workouts_visibility' not in serialized_user
        assert 'map_visibility' not in serialized_user
        assert 'manually_approves_followers' not in serialized_user
        assert 'hide_profile_in_users_directory' not in serialized_user

    def test_it_returns_some_workouts_infos(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(light=False)

        assert 'nb_workouts' in serialized_user
        assert 'nb_sports' not in serialized_user
        assert 'records' not in serialized_user
        assert 'sports_list' not in serialized_user
        assert 'total_ascent' not in serialized_user
        assert 'total_distance' not in serialized_user
        assert 'total_duration' not in serialized_user

    def test_it_does_not_return_confirmation_token(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(light=False)

        assert 'confirmation_token' not in serialized_user


class TestInactiveUserSerialize(UserModelAssertMixin):
    def test_it_returns_is_active_to_false_for_inactive_user(
        self,
        app: Flask,
        inactive_user: User,
    ) -> None:
        serialized_user = inactive_user.serialize(
            current_user=inactive_user, light=False
        )

        assert serialized_user['is_active'] is False


@pytest.mark.disable_autouse_update_records_patch
class TestUserRecords(UserModelAssertMixin):
    def test_it_returns_empty_list_when_no_workouts(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user['records'] == []

    def test_it_returns_user_records(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)
        assert len(serialized_user['records']) == 4
        records = sorted(
            serialized_user['records'], key=lambda r: r['record_type']
        )
        assert records[0]['record_type'] == 'AS'
        assert records[0]['sport_id'] == sport_1_cycling.id
        assert records[0]['user'] == user_1.username
        assert records[0]['value'] > 0
        assert records[0]['workout_id'] == workout_cycling_user_1.short_id
        assert records[0]['workout_date']

    def test_it_returns_totals_when_user_has_workout_without_ascent(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)
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
        serialized_user = user_1.serialize(current_user=user_1, light=False)
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
        serialized_user = user_1.serialize(current_user=user_1, light=False)
        assert serialized_user['total_ascent'] == 100
        assert serialized_user['total_distance'] == 22
        assert serialized_user['total_duration'] == '2:40:00'


class TestUserWorkouts(UserModelAssertMixin):
    def test_it_returns_infos_when_no_workouts(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

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
        serialized_user = user_1.serialize(current_user=user_1, light=False)

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
        serialized_user = user_1.serialize(current_user=user_1, light=False)

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
        with travel(now + timedelta(seconds=61), tick=False):
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
    def test_user_sport_preferences_model(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        serialized_user_sport = user_1_sport_1_preference.serialize()

        assert serialized_user_sport['user_id'] == user_1.id
        assert serialized_user_sport['sport_id'] == sport_1_cycling.id
        assert serialized_user_sport['color'] is None
        assert serialized_user_sport['is_active']
        assert serialized_user_sport['stopped_speed_threshold'] == 1
        assert serialized_user_sport['default_equipments'] == []

    def test_user_sport_preferences_model_with_default_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    },
                    {
                        "equipment_id": equipment_shoes_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    },
                ]
            )
        )

        serialized_user_sport = user_1_sport_1_preference.serialize()

        assert serialized_user_sport['user_id'] == user_1.id
        assert serialized_user_sport['sport_id'] == sport_1_cycling.id
        assert serialized_user_sport['color'] is None
        assert serialized_user_sport['is_active']
        assert serialized_user_sport['stopped_speed_threshold'] == 1
        assert len(serialized_user_sport['default_equipments']) == 2
        assert (
            equipment_bike_user_1.serialize()
            in serialized_user_sport['default_equipments']
        )
        assert (
            equipment_shoes_user_1.serialize()
            in serialized_user_sport['default_equipments']
        )


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


class TestFollowRequestModel:
    def test_follow_request_model(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        assert '<FollowRequest from user \'1\' to user \'2\'>' == str(
            follow_request_from_user_1_to_user_2
        )

        serialized_follow_request = (
            follow_request_from_user_1_to_user_2.serialize()
        )
        assert serialized_follow_request['from_user'] == user_1.serialize()
        assert serialized_follow_request['to_user'] == user_2.serialize()

    def test_it_raises_error_if_getting_activity_object_when_federation_is_disabled(  # noqa
        self,
        app: Flask,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        with pytest.raises(
            FederationDisabledException,
            match='Federation is disabled.',
        ):
            follow_request_from_user_1_to_user_2.get_activity()

    def test_it_deletes_follow_request_on_followed_user_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        followed_user_id = user_2.id

        db.session.delete(user_2)

        assert (
            FollowRequest.query.filter_by(
                follower_user_id=user_1.id,
                followed_user_id=followed_user_id,
            ).first()
            is None
        )

    def test_it_deletes_follow_request_on_follower_user_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follower_user_id = user_1.id

        db.session.delete(user_1)

        assert (
            FollowRequest.query.filter_by(
                follower_user_id=follower_user_id,
                followed_user_id=user_2.id,
            ).first()
            is None
        )


class TestUserFollowingModel:
    def test_user_2_sends_follow_requests_to_user_1(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        follow_request = user_2.send_follow_request_to(user_1)

        assert follow_request in user_2.sent_follow_requests.all()

    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_it_does_not_call_send_to_user_inbox_when_federation_is_disabled(
        self,
        send_to_remote_inbox_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_2.send_follow_request_to(user_1)

        send_to_remote_inbox_mock.send.assert_not_called()

    def test_user_1_receives_follow_requests_from_user_2(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        follow_request = user_2.send_follow_request_to(user_1)

        assert follow_request in user_1.received_follow_requests.all()

    def test_user_has_pending_follow_request(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        assert (
            follow_request_from_user_2_to_user_1
            in user_1.pending_follow_requests
        )

    def test_user_has_no_pending_follow_request(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.updated_at = datetime.utcnow()
        assert user_1.pending_follow_requests == []

    def test_user_approves_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        follow_request = user_1.approves_follow_request_from(user_2)

        assert follow_request.is_approved
        assert user_1.pending_follow_requests == [
            follow_request_from_user_3_to_user_1
        ]

    def test_user_refuses_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request = user_1.rejects_follow_request_from(user_2)

        assert not follow_request.is_approved
        assert user_1.pending_follow_requests == []

    def test_it_raises_error_if_follow_request_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        with pytest.raises(NotExistingFollowRequestError):
            user_1.approves_follow_request_from(user_2)

    def test_it_raises_error_if_user_approves_follow_request_already_processed(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.updated_at = datetime.utcnow()

        with pytest.raises(FollowRequestAlreadyProcessedError):
            user_1.approves_follow_request_from(user_2)

    def test_follow_request_is_automatically_accepted_if_manually_approved_if_false(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.manually_approves_followers = False
        follow_request = user_2.send_follow_request_to(user_1)

        assert follow_request in user_2.sent_follow_requests.all()
        assert follow_request.is_approved is True
        assert follow_request.updated_at is not None


class TestUserUnfollowModel:
    def test_it_raises_error_if_follow_request_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        with pytest.raises(NotExistingFollowRequestError):
            user_1.unfollows(user_2)

    def test_user_1_unfollows_user_2(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = True
        follow_request_from_user_1_to_user_2.updated_at = datetime.utcnow()

        user_1.unfollows(user_2)

        assert user_1.following.count() == 0
        assert user_2.followers.count() == 0

    def test_it_removes_pending_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_1.unfollows(user_2)

        assert user_1.sent_follow_requests.all() == []

    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_it_does_not_call_send_to_user_inbox_when_federation_is_disabled(
        self,
        send_to_remote_inbox_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = True
        follow_request_from_user_1_to_user_2.updated_at = datetime.utcnow()

        user_1.unfollows(user_2)

        send_to_remote_inbox_mock.send.assert_not_called()


class TestUserFollowers:
    def test_it_returns_empty_list_if_no_followers(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        assert user_1.followers.all() == []

    def test_it_returns_empty_list_if_follow_request_is_not_approved(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        assert user_1.followers.all() == []

    def test_it_returns_follower_if_follow_request_is_approved(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.is_approved = True
        follow_request_from_user_2_to_user_1.updated_at = datetime.utcnow()

        assert user_1.followers.all() == [user_2]

    def test_it_does_return_suspended_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.is_approved = True
        follow_request_from_user_2_to_user_1.updated_at = datetime.utcnow()
        user_2.suspended_at = datetime.utcnow()

        assert user_1.followers.all() == []


class TestUserFollowing:
    def test_it_returns_empty_list_if_no_following(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        assert user_1.following.all() == []

    def test_it_returns_empty_list_if_follow_request_is_not_approved(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        assert user_1.following.all() == []

    def test_it_returns_following_if_follow_request_is_approved(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = True
        follow_request_from_user_1_to_user_2.updated_at = datetime.utcnow()

        assert user_1.following.all() == [user_2]

    def test_it_does_not_return_suspended_following_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = True
        follow_request_from_user_1_to_user_2.updated_at = datetime.utcnow()
        user_2.suspended_at = datetime.utcnow()

        assert user_1.following.all() == []


class TestUserGetRecipientsSharedInbox:
    def test_it_raises_exception_if_federation_disabled(
        self, app: Flask, user_1: User
    ) -> None:
        with pytest.raises(FederationDisabledException):
            user_1.get_followers_shared_inboxes()


class TestUserFullname:
    def test_it_returns_user_actor_fullname(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        assert user_1.fullname == user_1.actor.fullname


class TestUserFollowRequestStatus(UserModelAssertMixin):
    def test_it_returns_user_1_and_user_2_dont_not_follow_each_other(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert serialized_user['followers'] == 0
        assert serialized_user['following'] == 0
        assert serialized_user['follows'] == 'false'
        assert serialized_user['is_followed_by'] == 'false'

    def test_status_when_follow_request_is_pending(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.send_follow_request_to(user_2)

        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert serialized_user['followers'] == 0
        assert serialized_user['following'] == 0
        assert serialized_user['follows'] == 'false'
        assert serialized_user['is_followed_by'] == 'pending'

    def test_status_when_user_rejects_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.send_follow_request_to(user_2)
        user_2.rejects_follow_request_from(user_1)

        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert serialized_user['followers'] == 0
        assert serialized_user['following'] == 0
        assert serialized_user['follows'] == 'false'
        assert serialized_user['is_followed_by'] == 'pending'

    def test_followed_user_status_when_follow_request_is_approved(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.send_follow_request_to(user_2)
        user_2.approves_follow_request_from(user_1)

        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert serialized_user['followers'] == 1
        assert serialized_user['following'] == 0
        assert serialized_user['follows'] == 'false'
        assert serialized_user['is_followed_by'] == 'true'

    def test_follower_status_when_follow_request_is_approved(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.send_follow_request_to(user_2)
        user_2.approves_follow_request_from(user_1)

        serialized_user = user_1.serialize(current_user=user_2, light=False)

        assert serialized_user['followers'] == 0
        assert serialized_user['following'] == 1
        assert serialized_user['follows'] == 'true'
        assert serialized_user['is_followed_by'] == 'false'


class TestUserLinkifyMention:
    def test_it_returns_linkified_mention_with_username(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        assert user_1.linkify_mention(with_domain=False) == (
            f'<a href="{user_1.get_user_url()}" target="_blank" '
            f'rel="noopener noreferrer">@{user_1.username}</a>'
        )

    def test_it_returns_linkified_mention_with_fullname(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        assert user_1.linkify_mention(with_domain=True) == (
            f'<a href="{user_1.get_user_url()}" target="_blank" '
            f'rel="noopener noreferrer">@{user_1.fullname}</a>'
        )


class TestBlocksUser:
    def test_it_blocks_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.blocks_user(user_2)

        assert (
            BlockedUser.query.filter_by(
                user_id=user_2.id,
                by_user_id=user_1.id,
            ).first()
            is not None
        )
        serialized_user = user_2.serialize(current_user=user_1, light=False)
        assert serialized_user['blocked'] is True

    def test_it_inits_created_at(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        now = datetime.utcnow()
        with travel(now, tick=False):
            user_1.blocks_user(user_2)

        blocked_user = BlockedUser.query.filter_by(
            user_id=user_2.id,
            by_user_id=user_1.id,
        ).first()
        assert blocked_user.created_at == now

    def test_it_does_not_raises_error_when_user_is_already_blocked(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.blocks_user(user_2)

        user_1.blocks_user(user_2)

        assert (
            BlockedUser.query.filter_by(
                user_id=user_2.id,
                by_user_id=user_1.id,
            ).first()
            is not None
        )

    def test_user_can_not_block_itself(self, app: Flask, user_1: User) -> None:
        with pytest.raises(BlockUserException):
            user_1.blocks_user(user_1)

    def test_it_blocks_a_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)

        user_1.blocks_user(user_2)

        assert (
            BlockedUser.query.filter_by(
                user_id=user_2.id,
                by_user_id=user_1.id,
            ).first()
            is not None
        )
        serialized_user = user_2.serialize(current_user=user_1, light=False)
        assert serialized_user['blocked'] is True

    def test_it_deletes_follow_request_when_a_follow_request_exists(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.blocks_user(user_2)

        assert (
            FollowRequest.query.filter_by(
                follower_user_id=user_2.id,
                followed_user_id=user_1.id,
            ).first()
            is None
        )

    def test_it_deletes_follow_request_notification_when_a_follow_request_exists(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.blocks_user(user_2)

        assert (
            Notification.query.filter_by(
                from_user_id=user_2.id,
                to_user_id=user_1.id,
            ).first()
            is None
        )

    def test_it_deletes_follow_request_when_user_blocks_a_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)

        user_1.blocks_user(user_2)

        assert (
            FollowRequest.query.filter_by(
                follower_user_id=user_2.id,
                followed_user_id=user_1.id,
            ).first()
            is None
        )

    def test_it_deletes_follow_request_notification_when_user_blocks_a_follower(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)

        user_1.blocks_user(user_2)

        assert (
            Notification.query.filter_by(
                from_user_id=user_2.id,
                to_user_id=user_1.id,
            ).first()
            is None
        )


class TestUnBlocksUser:
    def test_it_unblocks_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.blocks_user(user_2)

        user_1.unblocks_user(user_2)

        assert (
            BlockedUser.query.filter_by(
                user_id=user_2.id,
                by_user_id=user_1.id,
            ).first()
            is None
        )
        serialized_user = user_2.serialize(current_user=user_1, light=False)
        assert serialized_user['blocked'] is False

    def test_it_does_not_raises_error_when_user_is_not_blocked(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.unblocks_user(user_2)

        assert (
            BlockedUser.query.filter_by(
                user_id=user_2.id,
                by_user_id=user_1.id,
            ).first()
            is None
        )


class TestIsBlockedBy:
    def test_it_returns_false_when_user_is_not_blocked(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        assert user_1.is_blocked_by(user_2) is False

    def test_it_returns_true_when_user_is_blocked(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_2.blocks_user(user_1)

        user_1.is_blocked_by(user_2)

        assert user_1.is_blocked_by(user_2) is True


class TestBlockedUsers:
    def test_it_returns_empty_list_when_no_user_blocked(
        self, app: Flask, user_1: User
    ) -> None:
        assert user_1.blocked_users.all() == []

    def test_it_returns_blocked_users(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
    ) -> None:
        user_1.blocks_user(user_2)
        user_1.blocks_user(user_4)

        assert set(user_1.get_blocked_user_ids()) == {user_2.id, user_4.id}


class TestBlockedByUsers:
    def test_it_returns_empty_list_when_not_blocked(
        self, app: Flask, user_1: User
    ) -> None:
        assert user_1.blocked_by_users.all() == []

    def test_it_returns_blocked_by_users_ids(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
    ) -> None:
        user_2.blocks_user(user_1)
        user_3.blocks_user(user_1)

        assert set(user_1.get_blocked_by_user_ids()) == {user_2.id, user_3.id}


class TestUsersWithSuspensions:
    def test_suspension_action_is_none_when_no_suspension_for_given_user(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="user_suspension",
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()

        assert user_3.suspension_action is None

    def test_suspension_action_is_last_suspension_action_when_user_is_suspended(  # noqa
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        for n in range(2):
            admin_action = AdminAction(
                admin_user_id=user_1_admin.id,
                action_type=(
                    "user_suspension" if n % 2 == 0 else "user_unsuspension"
                ),
                user_id=user_2.id,
            )
            db.session.add(admin_action)
        expected_admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="user_suspension",
            user_id=user_2.id,
        )
        user_2.suspended_at = datetime.utcnow()
        db.session.add(expected_admin_action)
        db.session.commit()

        assert user_2.suspension_action == expected_admin_action

    def test_suspension_action_is_none_when_user_is_unsuspended(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        for n in range(2):
            admin_action = AdminAction(
                admin_user_id=user_1_admin.id,
                action_type=(
                    "user_suspension" if n % 2 == 0 else "user_unsuspension"
                ),
                user_id=user_2.id,
            )
            db.session.add(admin_action)
        db.session.commit()

        assert user_2.suspension_action is None


class TestUserLightSerializer(UserModelAssertMixin):
    def test_it_returns_limited_user_infos_by_default(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1_admin)

        assert serialized_user == {
            'admin': user_2.admin,
            'blocked': user_2.is_blocked_by(user_1_admin),
            'created_at': user_2.created_at,
            'email': user_2.email,
            'followers': user_2.followers.count(),
            'following': user_2.following.count(),
            'follows': user_2.follows(user_1_admin),
            'is_active': True,
            'is_followed_by': user_2.is_followed_by(user_1_admin),
            'is_remote': user_2.is_remote,
            'nb_workouts': user_2.workouts_count,
            'picture': user_2.picture is not None,
            'suspended_at': None,
            'username': user_2.username,
        }

    def test_it_returns_limited_user_infos_as_admin(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=True
        )

        assert serialized_user == {
            'admin': user_2.admin,
            'blocked': user_2.is_blocked_by(user_1_admin),
            'created_at': user_2.created_at,
            'email': user_2.email,
            'followers': user_2.followers.count(),
            'following': user_2.following.count(),
            'follows': user_2.follows(user_1_admin),
            'is_active': True,
            'is_followed_by': user_2.is_followed_by(user_1_admin),
            'is_remote': user_2.is_remote,
            'nb_workouts': user_2.workouts_count,
            'picture': user_2.picture is not None,
            'suspended_at': None,
            'username': user_2.username,
        }

    def test_it_returns_limited_user_infos_as_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=True)

        assert serialized_user == {
            'admin': user_2.admin,
            'blocked': user_2.is_blocked_by(user_1),
            'created_at': user_2.created_at,
            'followers': user_2.followers.count(),
            'following': user_2.following.count(),
            'follows': user_2.follows(user_1),
            'is_followed_by': user_2.is_followed_by(user_1),
            'is_remote': user_2.is_remote,
            'nb_workouts': user_2.workouts_count,
            'picture': user_2.picture is not None,
            'username': user_2.username,
        }

    def test_it_returns_limited_user_infos_as_unauthenticated_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=None, light=True)

        assert serialized_user == {
            'admin': user_2.admin,
            'created_at': user_2.created_at,
            'followers': user_2.followers.count(),
            'following': user_2.following.count(),
            'is_remote': user_2.is_remote,
            'nb_workouts': user_2.workouts_count,
            'picture': user_2.picture is not None,
            'username': user_2.username,
        }
