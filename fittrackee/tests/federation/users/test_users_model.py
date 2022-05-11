from datetime import datetime
from unittest.mock import Mock, patch

from flask import Flask

from fittrackee.federation.constants import AP_CTX
from fittrackee.tests.utils import generate_follow_request
from fittrackee.users.models import FollowRequest, User


class TestUserModel:
    def test_user_is_not_remote_when_actor_is_local(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        assert user_1.is_remote is False
        assert user_1.serialize()['is_remote'] is False
        assert 'fullname' not in user_1.serialize()

    def test_user_is_remote_when_actor_is_remote(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        assert remote_user.is_remote is True
        assert remote_user.serialize()['is_remote'] is True
        assert (
            remote_user.serialize()['fullname']
            == f'@{remote_user.actor.fullname}'
        )
        assert (
            remote_user.serialize()['profile_link']
            == remote_user.actor.profile_url
        )

    def test_it_returns_remote_actor_stats_when_user_is_remote(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        expected_followers = 10
        expected_following = 23
        remote_user.actor.stats.followers = expected_followers
        remote_user.actor.stats.following = expected_following

        serialized_user = remote_user.serialize()
        assert serialized_user['followers'] == expected_followers
        assert serialized_user['following'] == expected_following


class TestFollowRequestModelWithFederation:
    def test_follow_request_model(
        self,
        app_with_federation: Flask,
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

    def test_it_returns_follow_activity_object(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        actor_1 = user_1.actor
        actor_2 = user_2.actor
        activity_object = follow_request_from_user_1_to_user_2.get_activity()

        assert activity_object == {
            '@context': AP_CTX,
            'id': f'{actor_1.activitypub_id}#follows/{actor_2.fullname}',
            'type': 'Follow',
            'actor': actor_1.activitypub_id,
            'object': actor_2.activitypub_id,
        }

    def test_it_returns_accept_activity_object_when_follow_request_is_accepted(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        actor_1 = user_1.actor
        actor_2 = user_2.actor
        follow_request_from_user_1_to_user_2.is_approved = True
        follow_request_from_user_1_to_user_2.updated_at = datetime.utcnow()
        activity_object = follow_request_from_user_1_to_user_2.get_activity()

        assert activity_object == {
            '@context': AP_CTX,
            'id': (
                f'{actor_2.activitypub_id}#accepts/follow/{actor_1.fullname}'
            ),
            'type': 'Accept',
            'actor': actor_2.activitypub_id,
            'object': {
                'id': f'{actor_1.activitypub_id}#follows/{actor_2.fullname}',
                'type': 'Follow',
                'actor': actor_1.activitypub_id,
                'object': actor_2.activitypub_id,
            },
        }

    def test_it_returns_reject_activity_object_when_follow_request_is_rejected(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        actor_1 = user_1.actor
        actor_2 = user_2.actor
        follow_request_from_user_1_to_user_2.is_approved = False
        follow_request_from_user_1_to_user_2.updated_at = datetime.utcnow()
        activity_object = follow_request_from_user_1_to_user_2.get_activity()

        assert activity_object == {
            '@context': AP_CTX,
            'id': (
                f'{actor_2.activitypub_id}#rejects/follow/{actor_1.fullname}'
            ),
            'type': 'Reject',
            'actor': actor_2.activitypub_id,
            'object': {
                'id': f'{actor_1.activitypub_id}#follows/{actor_2.fullname}',
                'type': 'Follow',
                'actor': actor_1.activitypub_id,
                'object': actor_2.activitypub_id,
            },
        }


class TestUserFollowingModelWithFederation:
    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_local_actor_sends_follow_requests_to_remote_actor(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        actor_1 = user_1.actor
        remote_actor = remote_user.actor
        follow_request = actor_1.user.send_follow_request_to(remote_actor.user)

        assert follow_request in actor_1.user.sent_follow_requests.all()
        assert follow_request.is_approved is False
        assert follow_request.updated_at is None
        send_to_remote_inbox_mock.send.assert_called_with(
            sender_id=actor_1.id,
            activity=follow_request.get_activity(),
            recipients=[remote_actor.inbox_url],
        )

    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_follow_request_is_automatically_accepted_if_manually_approved_if_false(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        actor_1 = user_1.actor
        actor_1.user.manually_approves_followers = False
        remote_actor = remote_user.actor
        follow_request = remote_actor.user.send_follow_request_to(actor_1.user)

        assert follow_request in remote_actor.user.sent_follow_requests.all()
        assert follow_request.is_approved is True
        assert follow_request.updated_at is not None
        send_to_remote_inbox_mock.send.assert_called_with(
            sender_id=actor_1.id,
            activity=follow_request.get_activity(),
            recipients=[remote_actor.inbox_url],
        )


class TestUserUnfollowModelWithFederation:
    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_local_actor_sends_undo_activity_to_remote_actor(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_remote_user.is_approved = True
        follow_request_from_user_1_to_remote_user.updated_at = (
            datetime.utcnow()
        )
        expected_activity = (
            follow_request_from_user_1_to_remote_user.get_activity(undo=True)
        )

        user_1.unfollows(remote_user)

        send_to_remote_inbox_mock.send.assert_called_with(
            sender_id=user_1.actor.id,
            activity=expected_activity,
            recipients=[remote_user.actor.inbox_url],
        )


class TestUserGetRecipientsSharedInbox:
    def test_it_returns_empty_set_if_not_followers(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        inboxes = user_1.get_followers_shared_inboxes()

        assert inboxes == {
            'fittrackee': set(),
            'others': set(),
        }

    def test_it_returns_empty_set_if_only_local_followers(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)

        inboxes = user_1.get_followers_shared_inboxes()

        assert inboxes == {
            'fittrackee': set(),
            'others': set(),
        }

    def test_it_returns_shared_inbox_when_remote_followers_from_fittrackee_instance(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)

        inboxes = user_1.get_followers_shared_inboxes()

        assert inboxes == {
            'fittrackee': {remote_user.actor.shared_inbox_url},
            'others': set(),
        }

    def test_it_returns_shared_inbox_when_remote_followers_from_not_fittrackee_instance(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user_2: User,
    ) -> None:
        generate_follow_request(remote_user_2, user_1)
        user_1.approves_follow_request_from(remote_user_2)

        inboxes = user_1.get_followers_shared_inboxes()

        assert inboxes == {
            'fittrackee': set(),
            'others': {remote_user_2.actor.shared_inbox_url},
        }

    def test_it_returns_shared_inbox_from_several_remote_users(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        remote_user_2: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        generate_follow_request(remote_user_2, user_1)
        user_1.approves_follow_request_from(remote_user_2)

        inboxes = user_1.get_followers_shared_inboxes()

        assert inboxes == {
            'fittrackee': {remote_user.actor.shared_inbox_url},
            'others': {remote_user_2.actor.shared_inbox_url},
        }
