from datetime import datetime, timezone
from json import dumps
from unittest.mock import Mock, patch
from urllib.parse import urlparse

from _pytest.logging import LogCaptureFixture
from flask import Flask
from time_machine import travel

from fittrackee.federation.inbox import send_to_inbox
from fittrackee.federation.signature import VALID_SIG_DATE_FORMAT
from fittrackee.users.models import User

from ...mixins import BaseTestMixin, RandomMixin
from ...utils import generate_response


class TestSendToRemoteInbox(BaseTestMixin, RandomMixin):
    @patch("fittrackee.federation.inbox.generate_digest")
    @patch("fittrackee.federation.inbox.generate_signature_header")
    @patch("fittrackee.federation.inbox.requests")
    def test_it_calls_generate_signature_header(
        self,
        requests_mock: Mock,
        generate_signature_header_mock: Mock,
        generate_digest_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        actor_1 = user_1.actor
        remote_actor = remote_user.actor
        now = datetime.now(timezone.utc)
        parsed_inbox_url = urlparse(remote_actor.inbox_url)
        requests_mock.post.return_value = generate_response(status_code=200)
        digest = self.random_string()
        generate_digest_mock.return_value = digest

        with travel(now, tick=False):
            send_to_inbox(
                sender=actor_1,
                activity={"foo": "bar"},
                inbox_url=remote_actor.inbox_url,
            )

        generate_signature_header_mock.assert_called_with(
            host=parsed_inbox_url.netloc,
            path=parsed_inbox_url.path,
            date_str=self.get_date_string(
                date_format=VALID_SIG_DATE_FORMAT, date=now
            ),
            actor=actor_1,
            digest=digest,
        )

    @patch("fittrackee.federation.inbox.generate_digest")
    @patch("fittrackee.federation.inbox.generate_signature_header")
    @patch("fittrackee.federation.inbox.requests")
    def test_it_calls_requests_post(
        self,
        requests_mock: Mock,
        generate_signature_header_mock: Mock,
        generate_digest_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        actor_1 = user_1.actor
        remote_actor = remote_user.actor
        activity = {"foo": "bar"}
        now = datetime.now(timezone.utc)
        parsed_inbox_url = urlparse(remote_actor.inbox_url)
        requests_mock.post.return_value = generate_response(status_code=200)
        signed_header = self.random_string()
        generate_signature_header_mock.return_value = signed_header
        digest = self.random_string()
        generate_digest_mock.return_value = digest

        with travel(now, tick=False):
            send_to_inbox(
                sender=actor_1,
                activity=activity,
                inbox_url=remote_actor.inbox_url,
            )

        requests_mock.post.assert_called_with(
            remote_actor.inbox_url,
            data=dumps(activity),
            headers={
                "Host": parsed_inbox_url.netloc,
                "Date": self.get_date_string(
                    date_format=VALID_SIG_DATE_FORMAT, date=now
                ),
                "Digest": digest,
                "Signature": signed_header,
                "Content-Type": "application/ld+json",
            },
            timeout=30,
        )

    @patch("fittrackee.federation.inbox.generate_signature_header")
    @patch("fittrackee.federation.inbox.requests")
    def test_it_logs_error_if_remote_inbox_returns_error(
        self,
        requests_mock: Mock,
        generate_signature_header_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        caplog: LogCaptureFixture,
    ) -> None:
        actor_1 = user_1.actor
        remote_actor = remote_user.actor
        status_code = 404
        content = "error"
        requests_mock.post.return_value = generate_response(
            status_code=status_code, content=content
        )

        send_to_inbox(
            sender=actor_1,
            activity={"foo": "bar"},
            inbox_url=remote_actor.inbox_url,
        )

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].message == (
            f"Error when send to inbox '{remote_actor.inbox_url}', "
            f"status code: {status_code}, "
            f"content: {content}"
        )
