from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.federation.exceptions import FederationDisabledException
from fittrackee.users.exceptions import (
    FollowRequestAlreadyProcessedError,
    NotExistingFollowRequestError,
)
from fittrackee.users.models import FollowRequest, User, UserSportPreference
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
        assert serialized_user['imperial_units'] is False
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
            match='Can not create activity, federation is disabled.',
        ):
            follow_request_from_user_1_to_user_2.get_activity()


class TestUserFollowingModel:
    def test_user_2_sends_follow_requests_to_user_1(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        follow_request = user_2.send_follow_request_to(user_1)

        assert follow_request in user_2.sent_follow_requests.all()

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_does_not_call_send_to_user_inbox_when_federation_is_disabled(
        self,
        send_to_users_inbox_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_2.send_follow_request_to(user_1)

        send_to_users_inbox_mock.send.assert_not_called()

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
        follow_request_from_user_2_to_user_1.updated_at = datetime.now()
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
        follow_request_from_user_2_to_user_1.updated_at = datetime.now()

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
        follow_request_from_user_2_to_user_1.updated_at = datetime.now()

        assert user_1.followers.all() == [user_2]


class TestUserFollowing:
    def test_it_returns_empty_list_if_no_followers(
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

    def test_it_returns_follower_if_follow_request_is_approved(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = True
        follow_request_from_user_1_to_user_2.updated_at = datetime.now()

        assert user_1.following.all() == [user_2]
