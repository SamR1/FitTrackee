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

from ...mixins import ApiTestCaseMixin
from ...utils import generate_response, get_date_string, random_string


class TestUserInbox(ApiTestCaseMixin):
    @staticmethod
    def post_to_user_inbox(
        app_with_federation: Flask, remote_actor: Actor, local_actor: Actor
    ) -> Tuple[Dict, TestResponse]:
        remote_actor.generate_keys()
        date_str = get_date_string(date_format=VALID_SIG_DATE_FORMAT)
        client = app_with_federation.test_client()
        inbox_path = f"/federation/user/{local_actor.preferred_username}/inbox"
        follow_activity: Dict = {
            "@context": AP_CTX,
            "id": random_string(),
            "type": ActivityType.FOLLOW.value,
            "actor": remote_actor.activitypub_id,
            "object": local_actor.activitypub_id,
        }
        digest = generate_digest(follow_activity)

        with patch.object(requests, "get") as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=remote_actor.serialize(),
            )
            requests_mock.path = inbox_path
            response = client.post(
                inbox_path,
                content_type="application/json",
                headers={
                    "Host": remote_actor.domain.name,
                    "Date": date_str,
                    "Digest": digest,
                    "Signature": generate_signature_header(
                        host=remote_actor.domain.name,
                        path=inbox_path,
                        date_str=date_str,
                        actor=remote_actor,
                        digest=digest,
                    ),
                    "Content-Type": "application/ld+json",
                },
                data=json.dumps(follow_activity),
            )

        return follow_activity, response

    def test_it_returns_404_if_user_does_not_exist(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        client = app_with_federation.test_client()

        response = client.post(
            f"/federation/user/{random_string()}/inbox",
            content_type="application/json",
            data=json.dumps({}),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert "not found" in data["status"]
        assert "user does not exist" in data["message"]

    @pytest.mark.parametrize(
        "input_description, input_activity",
        [
            ("empty dict", {}),
            (
                "missing object",
                {"type": ActivityType.FOLLOW.value},
            ),
            ("missing type", {"object": random_string()}),
            (
                "invalid type",
                {"type": random_string(), "object": random_string()},
            ),
        ],
    )
    def test_it_returns_400_if_activity_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        input_description: str,
        input_activity: Dict,
    ) -> None:
        client = app_with_federation.test_client()

        response = client.post(
            f"/federation/user/{user_1.actor.preferred_username}/inbox",
            content_type="application/json",
            data=json.dumps(input_activity),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert "error" in data["status"]
        assert "invalid payload" in data["message"]

    def test_it_returns_401_if_headers_are_missing(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        client = app_with_federation.test_client()
        follow_activity = {
            "@context": AP_CTX,
            "id": random_string(),
            "type": ActivityType.FOLLOW.value,
            "actor": random_string(),
            "object": random_string(),
        }

        response = client.post(
            f"/federation/user/{user_1.actor.preferred_username}/inbox",
            content_type="application/json",
            data=json.dumps(follow_activity),
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
        follow_activity = {
            "@context": AP_CTX,
            "id": random_string(),
            "type": ActivityType.FOLLOW.value,
            "actor": random_string(),
            "object": random_string(),
        }

        response = client.post(
            f"/federation/user/{user_1.actor.preferred_username}/inbox",
            content_type="application/json",
            headers={
                "Host": random_string(),
                "Date": random_string(),
                "Signature": random_string(),
            },
            data=json.dumps(follow_activity),
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
        user_1: User,
    ) -> None:
        _, response = self.post_to_user_inbox(
            app_with_federation, remote_user.actor, user_1.actor
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
        user_1: User,
    ) -> None:
        activity_dict, _ = self.post_to_user_inbox(
            app_with_federation, remote_user.actor, user_1.actor
        )

        handle_activity.send.assert_called_with(activity=activity_dict)
