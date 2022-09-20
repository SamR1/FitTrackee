from flask import Flask

from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.enums import ActivityType
from fittrackee.federation.objects.follow_request import FollowRequestObject
from fittrackee.users.models import User


class TestFollowRequestObject:
    def test_it_generates_follow_activity(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        follow_request = FollowRequestObject(
            from_actor=user_1.actor,
            to_actor=user_2.actor,
            activity_type=ActivityType.FOLLOW,
        )

        serialized_follow_request = follow_request.serialize()

        assert serialized_follow_request == {
            '@context': AP_CTX,
            'id': (
                f'{user_1.actor.activitypub_id}#follows/'
                f'{user_2.actor.fullname}'
            ),
            'type': 'Follow',
            'actor': user_1.actor.activitypub_id,
            'object': user_2.actor.activitypub_id,
        }

    def test_it_generates_accept_activity(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        follow_request = FollowRequestObject(
            from_actor=user_1.actor,
            to_actor=user_2.actor,
            activity_type=ActivityType.ACCEPT,
        )

        serialized_follow_request = follow_request.serialize()

        assert serialized_follow_request == {
            '@context': AP_CTX,
            'id': (
                f'{user_2.actor.activitypub_id}#accepts/'
                f'follow/{user_1.actor.fullname}'
            ),
            'type': 'Accept',
            'actor': user_2.actor.activitypub_id,
            'object': {
                'id': (
                    f'{user_1.actor.activitypub_id}#follows/'
                    f'{user_2.actor.fullname}'
                ),
                'type': 'Follow',
                'actor': user_1.actor.activitypub_id,
                'object': user_2.actor.activitypub_id,
            },
        }

    def test_it_generates_reject_activity(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        follow_request = FollowRequestObject(
            from_actor=user_1.actor,
            to_actor=user_2.actor,
            activity_type=ActivityType.REJECT,
        )

        serialized_follow_request = follow_request.serialize()

        assert serialized_follow_request == {
            '@context': AP_CTX,
            'id': (
                f'{user_2.actor.activitypub_id}#rejects/'
                f'follow/{user_1.actor.fullname}'
            ),
            'type': 'Reject',
            'actor': user_2.actor.activitypub_id,
            'object': {
                'id': (
                    f'{user_1.actor.activitypub_id}#follows/'
                    f'{user_2.actor.fullname}'
                ),
                'type': 'Follow',
                'actor': user_1.actor.activitypub_id,
                'object': user_2.actor.activitypub_id,
            },
        }

    def test_it_generates_undo_activity(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        follow_request = FollowRequestObject(
            from_actor=user_1.actor,
            to_actor=user_2.actor,
            activity_type=ActivityType.UNDO,
        )

        serialized_follow_request = follow_request.serialize()

        assert serialized_follow_request == {
            '@context': AP_CTX,
            'id': (
                f'{user_1.actor.activitypub_id}#undoes/'
                f'{user_2.actor.fullname}'
            ),
            'type': 'Undo',
            'actor': user_1.actor.activitypub_id,
            'object': {
                'id': (
                    f'{user_1.actor.activitypub_id}#follows/'
                    f'{user_2.actor.fullname}'
                ),
                'type': 'Follow',
                'actor': user_1.actor.activitypub_id,
                'object': user_2.actor.activitypub_id,
            },
        }
