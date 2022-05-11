from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.federation.exceptions import SenderNotFoundException
from fittrackee.federation.tasks.inbox import send_to_remote_inbox
from fittrackee.users.models import FollowRequest, User

from ...utils import random_domain_with_scheme, random_string


class TestSendToUsersInbox:
    def test_it_raises_error_if_sender_does_not_exist(
        self,
        app_with_federation: Flask,
        follow_request_from_user_1_to_user_2: FollowRequest,
        remote_user: User,
    ) -> None:
        with pytest.raises(SenderNotFoundException):
            send_to_remote_inbox(
                sender_id=0,
                activity=follow_request_from_user_1_to_user_2.get_activity(),
                recipients=[remote_user.actor.inbox_url],
            )

    @patch('fittrackee.federation.tasks.inbox.send_to_inbox')
    def test_it_calls_send_to_inbox(
        self,
        send_to_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        activity = {'foo': 'bar'}
        send_to_remote_inbox(
            sender_id=user_1.actor.id,
            activity=activity,
            recipients=[remote_user.actor.inbox_url],
        )

        send_to_inbox_mock.assert_called_with(
            sender=user_1.actor,
            activity=activity,
            inbox_url=remote_user.actor.inbox_url,
        )

    @patch('fittrackee.federation.tasks.inbox.send_to_inbox')
    def test_it_calls_send_to_inbox_for_each_recipient(
        self,
        send_to_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
    ) -> None:
        nb_recipients = 3
        recipients = [
            f'{random_domain_with_scheme}/{random_string()}/inbox'
            for _ in range(nb_recipients)
        ]

        send_to_remote_inbox(
            sender_id=user_1.actor.id,
            activity={},
            recipients=recipients,
        )

        assert send_to_inbox_mock.call_count == nb_recipients
