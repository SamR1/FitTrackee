import json
from datetime import datetime, timezone
from typing import List
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.users.models import FollowRequest, User

from ..mixins import ApiTestCaseMixin
from ..utils import OAUTH_SCOPES, random_string


class FollowersAsUserTestCase(ApiTestCaseMixin):
    @staticmethod
    def approves_follow_requests(
        follows_requests: List[FollowRequest],
    ) -> None:
        for follows_request in follows_requests:
            follows_request.is_approved = True
            follows_request.updated_at = datetime.now(timezone.utc)


class TestFollowersAsUnauthenticatedUser(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            f"/api/users/{user_1.username}/followers",
            content_type="application/json",
        )

        self.assert_401(response)


class TestFollowersAsSuspendedUser(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestFollowersAsUser(FollowersAsUserTestCase):
    def test_it_returns_404_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{random_string()}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data["status"] == "not found"
        assert data["message"] == "user does not exist"

    def test_it_returns_empty_list_if_no_followers(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_1.username}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["data"]["followers"] == []

    def test_it_returns_followers(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_2_to_user_1,
                follow_request_from_user_3_to_user_1,
            ]
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_1.username}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["followers"]) == 2
        assert data["data"]["followers"][0]["username"] == user_3.username
        assert data["data"]["followers"][1]["username"] == user_2.username
        assert "email" not in data["data"]["followers"][0]
        assert "email" not in data["data"]["followers"][1]

    def test_it_does_not_return_suspended_followers(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.approves_follow_requests([follow_request_from_user_2_to_user_1])
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_1.username}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["followers"]) == 0

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "follow:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self, app: Flask, user_1: User, client_scope: str, can_access: bool
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.get(
            f"/api/users/{user_1.username}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestFollowersAsAdmin(FollowersAsUserTestCase):
    def test_it_returns_404_if_user_does_not_exist(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{random_string()}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data["status"] == "not found"
        assert data["message"] == "user does not exist"

    def test_it_returns_empty_list_if_no_followers(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{user_1_admin.username}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["data"]["followers"] == []

    def test_it_returns_followers(
        self,
        app: Flask,
        user_1_admin: User,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_1_to_user_2,
                follow_request_from_user_3_to_user_2,
            ]
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{user_2.username}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["followers"]) == 2
        assert data["data"]["followers"][0]["email"] == user_3.email
        assert data["data"]["followers"][1]["email"] == user_1.email

    def test_it_does_not_return_suspended_followers(
        self,
        app: Flask,
        user_1_admin: User,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_1_to_user_2,
                follow_request_from_user_3_to_user_2,
            ]
        )
        user_3.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{user_2.username}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["followers"]) == 1
        assert data["data"]["followers"][0]["email"] == user_1.email


class TestFollowersPagination(FollowersAsUserTestCase):
    def test_it_returns_pagination_info(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    @patch("fittrackee.users.users.USERS_PER_PAGE", 1)
    def test_it_returns_first_page_on_followers_list(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_1_to_user_2,
                follow_request_from_user_3_to_user_2,
            ]
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}/followers",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 2,
        }

    @patch("fittrackee.users.users.USERS_PER_PAGE", 1)
    def test_it_returns_page_2_on_followers_list(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_1_to_user_2,
                follow_request_from_user_3_to_user_2,
            ]
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}/followers?page=2",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 2,
        }


class TestFollowingAsUnauthenticatedUser(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            f"/api/users/{user_1.username}/following",
            content_type="application/json",
        )

        self.assert_401(response)


class TestFollowingAsSuspendedUser(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestFollowingAsUser(FollowersAsUserTestCase):
    def test_it_returns_404_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{random_string()}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data["status"] == "not found"
        assert data["message"] == "user does not exist"

    def test_it_returns_empty_list_if_no_following_users(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_1.username}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["data"]["following"] == []

    def test_it_returns_following_users(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_3_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_3_to_user_2,
                follow_request_from_user_3_to_user_1,
            ]
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_3.username}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["following"]) == 2
        assert data["data"]["following"][0]["username"] == user_1.username
        assert data["data"]["following"][1]["username"] == user_2.username
        assert "email" in data["data"]["following"][0]
        assert "email" not in data["data"]["following"][1]

    def test_it_does_not_return_suspended_following(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_3_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_3_to_user_2,
                follow_request_from_user_3_to_user_1,
            ]
        )
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_3.username}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["following"]) == 1
        assert data["data"]["following"][0]["username"] == user_1.username

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "follow:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self, app: Flask, user_1: User, client_scope: str, can_access: bool
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.get(
            f"/api/users/{user_1.username}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestFollowingAsAdmin(FollowersAsUserTestCase):
    def test_it_returns_404_if_user_does_not_exist(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{random_string()}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data["status"] == "not found"
        assert data["message"] == "user does not exist"

    def test_it_returns_empty_list_if_no_following_users(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{user_1_admin.username}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["data"]["following"] == []

    def test_it_returns_following_users(
        self,
        app: Flask,
        user_1_admin: User,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_3_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_3_to_user_2,
                follow_request_from_user_3_to_user_1,
            ]
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{user_3.username}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["following"]) == 2
        assert data["data"]["following"][0]["email"] == user_1.email
        assert data["data"]["following"][1]["email"] == user_2.email

    def test_it_does_not_return_suspended_following(
        self,
        app: Flask,
        user_1_admin: User,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_3_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_3_to_user_2,
                follow_request_from_user_3_to_user_1,
            ]
        )
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{user_3.username}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["following"]) == 1
        assert data["data"]["following"][0]["email"] == user_1.email


class TestFollowingPagination(FollowersAsUserTestCase):
    def test_it_returns_pagination_info(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    @patch("fittrackee.users.users.USERS_PER_PAGE", 1)
    def test_it_returns_first_page_on_following_list(
        self,
        app: Flask,
        user_1: User,
        user_3: User,
        follow_request_from_user_3_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_3_to_user_1,
                follow_request_from_user_3_to_user_2,
            ]
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_3.username}/following",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 2,
        }

    @patch("fittrackee.users.users.USERS_PER_PAGE", 1)
    def test_it_returns_page_2_on_followers_list(
        self,
        app: Flask,
        user_1: User,
        user_3: User,
        follow_request_from_user_3_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        self.approves_follow_requests(
            [
                follow_request_from_user_3_to_user_1,
                follow_request_from_user_3_to_user_2,
            ]
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_3.username}/following?page=2",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 2,
        }
