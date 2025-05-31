import json
from typing import Dict, Tuple
from unittest.mock import Mock, patch

import pytest
import requests
from flask import Flask
from werkzeug.test import TestResponse

from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.enums import ActivityType
from fittrackee.federation.models import Actor
from fittrackee.federation.signature import (
    VALID_SIG_DATE_FORMAT,
    generate_digest,
    generate_signature_header,
)
from fittrackee.users.models import User

from ...mixins import ApiTestCaseMixin, RandomMixin
from ...utils import generate_response


class TestSharedInbox(ApiTestCaseMixin, RandomMixin):
    route = "/federation/inbox"

    def post_to_shared_inbox(
        self, app_with_federation: Flask, actor: Actor
    ) -> Tuple[Dict, TestResponse]:
        actor.generate_keys()
        date_str = self.get_date_string(date_format=VALID_SIG_DATE_FORMAT)
        client = app_with_federation.test_client()
        note_activity: Dict = {
            "@context": AP_CTX,
            "id": self.random_string(),
            "type": ActivityType.CREATE.value,
            "actor": actor.activitypub_id,
            "object": {
                "type": "Note",
                "content": self.random_string(),
            },
        }
        digest = generate_digest(note_activity)

        with patch.object(requests, "get") as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor.serialize(),
            )
            requests_mock.path = self.route
            response = client.post(
                self.route,
                content_type="application/json",
                headers={
                    "Host": actor.domain.name,
                    "Date": date_str,
                    "Digest": digest,
                    "Signature": generate_signature_header(
                        host=actor.domain.name,
                        path=self.route,
                        date_str=date_str,
                        actor=actor,
                        digest=digest,
                    ),
                    "Content-Type": "application/ld+json",
                },
                data=json.dumps(note_activity),
            )

        return note_activity, response

    def test_it_returns_403_when_federation_is_disabled(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps({}),
        )

        self.assert_403(
            response, "error, federation is disabled for this instance"
        )

    def test_it_returns_401_if_headers_are_missing(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        client = app_with_federation.test_client()
        note_activity = {
            "@context": AP_CTX,
            "id": self.random_string(),
            "type": ActivityType.CREATE.value,
            "actor": self.random_string(),
            "object": {
                "type": "Note",
                "content": self.random_string(),
            },
        }

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(note_activity),
        )

        assert response.status_code == 401
        data = json.loads(response.data.decode())
        assert "error" in data["status"]
        assert "Invalid signature." in data["message"]

    @pytest.mark.disable_autouse_generate_keys
    def test_it_returns_401_if_signature_is_invalid(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        client = app_with_federation.test_client()
        note_activity = {
            "@context": AP_CTX,
            "id": self.random_string(),
            "type": ActivityType.CREATE.value,
            "actor": self.random_string(),
            "object": {
                "type": "Note",
                "content": self.random_string(),
            },
        }

        response = client.post(
            self.route,
            content_type="application/json",
            headers={
                "Host": self.random_string(),
                "Date": self.random_string(),
                "Signature": self.random_string(),
            },
            data=json.dumps(note_activity),
        )

        assert response.status_code == 401
        data = json.loads(response.data.decode())
        assert "error" in data["status"]
        assert "Invalid signature." in data["message"]

    @pytest.mark.disable_autouse_generate_keys
    @patch("fittrackee.federation.inbox.handle_activity")
    def test_it_returns_200_if_activity_and_signature_are_valid(
        self,
        handle_activity: Mock,
        app_with_federation: Flask,
        remote_user: User,
    ) -> None:
        _, response = self.post_to_shared_inbox(
            app_with_federation, remote_user.actor
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]

    @pytest.mark.disable_autouse_generate_keys
    @patch("fittrackee.federation.inbox.handle_activity")
    def test_it_calls_handle_activity_task(
        self,
        handle_activity: Mock,
        app_with_federation: Flask,
        remote_user: User,
    ) -> None:
        activity_dict, _ = self.post_to_shared_inbox(
            app_with_federation, remote_user.actor
        )

        handle_activity.send.assert_called_with(activity=activity_dict)
