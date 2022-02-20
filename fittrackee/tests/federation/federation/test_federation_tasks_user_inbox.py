from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.federation.exceptions import SenderNotFoundException
from fittrackee.federation.models import Actor
from fittrackee.federation.tasks.user_inbox import send_to_users_inbox
from fittrackee.users.models import FollowRequest

from ...utils import random_domain_with_scheme, random_string


class TestSendToUsersInbox:
    def test_it_raises_error_if_sender_does_not_exist(
        self,
        app_with_federation: Flask,
        follow_request_from_user_1_to_user_2: FollowRequest,
        remote_actor: Actor,
    ) -> None:
        with pytest.raises(SenderNotFoundException):
            send_to_users_inbox(
                sender_id=0,
                activity=follow_request_from_user_1_to_user_2.get_activity(),
                recipients=[remote_actor.inbox_url],
            )

    @patch('fittrackee.federation.tasks.user_inbox.send_to_remote_user_inbox')
    def test_it_calls_send_to_remote_user_inbox(
        self,
        send_to_remote_user_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
    ) -> None:
        activity = {'foo': 'bar'}
        send_to_users_inbox(
            sender_id=actor_1.id,
            activity=activity,
            recipients=[remote_actor.inbox_url],
        )

        send_to_remote_user_inbox_mock.assert_called_with(
            sender=actor_1,
            activity=activity,
            recipient_inbox_url=remote_actor.inbox_url,
        )

    @patch('fittrackee.federation.tasks.user_inbox.send_to_remote_user_inbox')
    def test_it_calls_send_to_remote_user_inbox_for_each_recipient(
        self,
        send_to_remote_user_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
    ) -> None:
        nb_recipients = 3
        recipients = [
            f'{random_domain_with_scheme}/{random_string()}/inbox'
            for _ in range(nb_recipients)
        ]

        send_to_users_inbox(
            sender_id=actor_1.id,
            activity={},
            recipients=recipients,
        )

        assert send_to_remote_user_inbox_mock.call_count == nb_recipients
