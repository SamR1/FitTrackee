import json
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import List, Tuple
from unittest.mock import MagicMock, call, patch

import pytest
from flask import Flask
from sqlalchemy.dialects.postgresql import insert

from fittrackee import db
from fittrackee.dates import get_readable_duration
from fittrackee.equipments.models import Equipment
from fittrackee.reports.models import Report, ReportAction
from fittrackee.tests.comments.mixins import CommentMixin
from fittrackee.users.models import (
    FollowRequest,
    Notification,
    User,
    UserDataExport,
    UserSportPreference,
    UserSportPreferenceEquipment,
)
from fittrackee.users.roles import UserRole
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin, ReportMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


class TestGetUserAsAdmin(ApiTestCaseMixin):
    def test_it_returns_error_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/users/not_existing",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_entity(response, "user")

    def test_it_gets_single_user_without_workouts(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        assert data["data"]["users"][0] == jsonify_dict(
            user_2.serialize(current_user=user_1_admin, light=False)
        )

    def test_it_gets_single_user_with_workouts(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        assert data["data"]["users"][0] == jsonify_dict(
            user_2.serialize(current_user=user_1_admin, light=False)
        )

    def test_it_gets_authenticated_user(
        self,
        app: Flask,
        user_1_admin: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{user_1_admin.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        assert data["data"]["users"][0] == jsonify_dict(
            user_1_admin.serialize(current_user=user_1_admin, light=False)
        )

    def test_it_gets_inactive_user(
        self, app: Flask, user_1_admin: User, inactive_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{inactive_user.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        user = data["data"]["users"][0]
        assert user == jsonify_dict(
            inactive_user.serialize(current_user=user_1_admin, light=False)
        )

    def test_it_gets_hidden_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        user_2.hide_profile_in_users_directory = True
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        user = data["data"]["users"][0]
        assert user == jsonify_dict(
            user_2.serialize(current_user=user_1_admin, light=False)
        )

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "users:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.get(
            "/api/users/not_existing",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestGetUserAsUser(ApiTestCaseMixin):
    def test_it_returns_error_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/users/not_existing",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert "not found" in data["status"]
        assert "user does not exist" in data["message"]

    def test_it_does_not_get_inactive_user(
        self, app: Flask, user_1: User, inactive_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{inactive_user.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert "not found" in data["status"]
        assert "user does not exist" in data["message"]

    def test_it_gets_single_user_without_workouts(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        assert data["data"]["users"][0] == jsonify_dict(
            user_2.serialize(current_user=user_1, light=False)
        )

    def test_it_gets_single_user_with_workouts(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        assert data["data"]["users"][0] == jsonify_dict(
            user_2.serialize(current_user=user_1, light=False)
        )

    def test_it_gets_authenticated_user(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_1.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        assert data["data"]["users"][0] == jsonify_dict(
            user_1.serialize(current_user=user_1, light=False)
        )

    def test_it_gets_hidden_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_2.hide_profile_in_users_directory = True
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        user = data["data"]["users"][0]
        assert user == jsonify_dict(
            user_2.serialize(current_user=user_1, light=False)
        )


class TestGetUserAsSuspendedUser(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_suspended(
        self, app: Flask, user_1: User, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            f"/api/users/{user_1.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetUserAsUnauthenticatedUser(ApiTestCaseMixin):
    def test_it_returns_error_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            "/api/users/not_existing",
            content_type="application/json",
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert "not found" in data["status"]
        assert "user does not exist" in data["message"]

    def test_it_does_not_get_inactive_user(
        self, app: Flask, user_1_admin: User, inactive_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users/{inactive_user.username}",
            content_type="application/json",
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert "not found" in data["status"]
        assert "user does not exist" in data["message"]

    def test_it_gets_single_user_without_workouts(
        self, app: Flask, user_2: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            f"/api/users/{user_2.username}",
            content_type="application/json",
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        assert data["data"]["users"][0] == jsonify_dict(
            user_2.serialize(light=False)
        )

    def test_it_gets_single_user_with_workouts(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client = app.test_client()

        response = client.get(
            f"/api/users/{user_1.username}",
            content_type="application/json",
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        assert data["data"]["users"][0] == jsonify_dict(
            user_1.serialize(light=False)
        )

    def test_it_gets_hidden_user(self, app: Flask, user_1: User) -> None:
        user_1.hide_profile_in_users_directory = True
        client = app.test_client()

        response = client.get(
            f"/api/users/{user_1.username}",
            content_type="application/json",
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 1
        user = data["data"]["users"][0]
        assert user == jsonify_dict(user_1.serialize(light=False))


class TestGetUsersAsAdmin(ApiTestCaseMixin):
    def test_it_gets_users_list_without_inactive_hidden_and_suspended_users(
        self,
        app: Flask,
        user_1_admin: User,
        inactive_user: User,
        user_2: User,
        user_3: User,
        user_4: User,
    ) -> None:
        user_2.hide_profile_in_users_directory = True
        user_4.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 2
        assert data["data"]["users"][0] == jsonify_dict(
            user_1_admin.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][1] == jsonify_dict(
            user_3.serialize(current_user=user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_users_list_regardless_their_account_status(
        self, app: Flask, user_1_admin: User, inactive_user: User, user_3: User
    ) -> None:
        inactive_user.hide_profile_in_users_directory = False
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?with_inactive=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert data["data"]["users"][0] == jsonify_dict(
            user_1_admin.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][1] == jsonify_dict(
            inactive_user.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][2] == jsonify_dict(
            user_3.serialize(current_user=user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_regardless_their_hidden_profile_preference(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        user_2.hide_profile_in_users_directory = True
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?with_hidden=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert data["data"]["users"][0] == jsonify_dict(
            user_1_admin.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][1] == jsonify_dict(
            user_3.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][2] == jsonify_dict(
            user_2.serialize(current_user=user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_regardless_suspended_status(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        user_2.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?with_suspended=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert data["data"]["users"][0] == jsonify_dict(
            user_1_admin.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][1] == jsonify_dict(
            user_3.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][2] == jsonify_dict(
            user_2.serialize(current_user=user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_following_user_when_profile_is_hidden(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        user_2.hide_profile_in_users_directory = True
        user_3.hide_profile_in_users_directory = True
        user_1_admin.send_follow_request_to(user_2)
        user_2.approves_follow_request_from(user_1_admin)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?with_following=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 2
        assert data["data"]["users"][0] == jsonify_dict(
            user_1_admin.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][1] == jsonify_dict(
            user_2.serialize(current_user=user_1_admin)
        )

    def test_it_gets_all_users(
        self,
        app: Flask,
        user_1_admin: User,
        inactive_user: User,
        user_2: User,
        user_3: User,
    ) -> None:
        user_2.hide_profile_in_users_directory = True
        user_3.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?with_inactive=true"
            "&with_hidden=true&with_suspended=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 4
        assert data["data"]["users"][0] == jsonify_dict(
            user_1_admin.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][1] == jsonify_dict(
            inactive_user.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][2] == jsonify_dict(
            user_3.serialize(current_user=user_1_admin)
        )
        assert data["data"]["users"][3] == jsonify_dict(
            user_2.serialize(current_user=user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 4,
        }


class TestGetUsersPaginationAsAdmin(ApiTestCaseMixin):
    @patch("fittrackee.users.users.USERS_PER_PAGE", 2)
    def test_it_gets_first_page_on_users_list(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?page=1",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 2
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 3,
        }

    @patch("fittrackee.users.users.USERS_PER_PAGE", 2)
    def test_it_gets_next_page_on_users_list(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 3,
        }

    def test_it_gets_empty_next_page_on_users_list(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 0
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_user_list_with_2_per_page(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?per_page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 2
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 3,
        }

    def test_it_gets_next_page_on_user_list_with_2_per_page(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?page=2&per_page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_username(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=username",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "admin" in data["data"]["users"][0]["username"]
        assert "sam" in data["data"]["users"][1]["username"]
        assert "toto" in data["data"]["users"][2]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_username_ascending(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=username&order=asc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "admin" in data["data"]["users"][0]["username"]
        assert "sam" in data["data"]["users"][1]["username"]
        assert "toto" in data["data"]["users"][2]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_username_descending(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=username&order=desc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "toto" in data["data"]["users"][0]["username"]
        assert "sam" in data["data"]["users"][1]["username"]
        assert "admin" in data["data"]["users"][2]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_creation_date(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        user_2.created_at = datetime.now(timezone.utc) - timedelta(days=1)
        user_3.created_at = datetime.now(timezone.utc) - timedelta(hours=1)
        user_1_admin.created_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=created_at",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "toto" in data["data"]["users"][0]["username"]
        assert "sam" in data["data"]["users"][1]["username"]
        assert "admin" in data["data"]["users"][2]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_creation_date_ascending(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        user_2.created_at = datetime.now(timezone.utc) - timedelta(days=1)
        user_3.created_at = datetime.now(timezone.utc) - timedelta(hours=1)
        user_1_admin.created_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=created_at&order=asc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "toto" in data["data"]["users"][0]["username"]
        assert "sam" in data["data"]["users"][1]["username"]
        assert "admin" in data["data"]["users"][2]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_creation_date_descending(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        user_2.created_at = datetime.now(timezone.utc) - timedelta(days=1)
        user_3.created_at = datetime.now(timezone.utc) - timedelta(hours=1)
        user_1_admin.created_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=created_at&order=desc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "admin" in data["data"]["users"][0]["username"]
        assert "sam" in data["data"]["users"][1]["username"]
        assert "toto" in data["data"]["users"][2]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_role(
        self, app: Flask, user_2: User, user_1_admin: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=role",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "sam" in data["data"]["users"][0]["username"]
        assert "toto" in data["data"]["users"][1]["username"]
        assert "admin" in data["data"]["users"][2]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_role_ascending(
        self, app: Flask, user_2: User, user_1_admin: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=role&order=asc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "sam" in data["data"]["users"][0]["username"]
        assert "toto" in data["data"]["users"][1]["username"]
        assert "admin" in data["data"]["users"][2]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_role_descending(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=role&order=desc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "admin" in data["data"]["users"][0]["username"]
        assert "sam" in data["data"]["users"][1]["username"]
        assert "toto" in data["data"]["users"][2]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_workouts_count(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=workouts_count",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "admin" in data["data"]["users"][0]["username"]
        assert 0 == data["data"]["users"][0]["nb_workouts"]
        assert "sam" in data["data"]["users"][1]["username"]
        assert 0 == data["data"]["users"][1]["nb_workouts"]
        assert "toto" in data["data"]["users"][2]["username"]
        assert 1 == data["data"]["users"][2]["nb_workouts"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_workouts_count_ascending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=workouts_count&order=asc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "admin" in data["data"]["users"][0]["username"]
        assert 0 == data["data"]["users"][0]["nb_workouts"]
        assert "sam" in data["data"]["users"][1]["username"]
        assert 0 == data["data"]["users"][1]["nb_workouts"]
        assert "toto" in data["data"]["users"][2]["username"]
        assert 1 == data["data"]["users"][2]["nb_workouts"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_account_status(
        self,
        app: Flask,
        user_1_admin: User,
        inactive_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=is_active&"
            "with_inactive=true&with_hidden=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 2
        assert data["data"]["users"][0]["username"] == inactive_user.username
        assert not data["data"]["users"][0]["is_active"]
        assert data["data"]["users"][1]["username"] == user_1_admin.username
        assert data["data"]["users"][1]["is_active"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_users_list_ordered_by_account_status_ascending(
        self,
        app: Flask,
        user_1_admin: User,
        inactive_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=is_active&order=asc&"
            "with_inactive=true&with_hidden=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 2
        assert data["data"]["users"][0]["username"] == inactive_user.username
        assert not data["data"]["users"][0]["is_active"]
        assert data["data"]["users"][1]["username"] == user_1_admin.username
        assert data["data"]["users"][1]["is_active"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_users_list_ordered_by_account_status_descending(
        self,
        app: Flask,
        user_1_admin: User,
        inactive_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=is_active&order=desc&"
            "with_inactive=true&with_hidden=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 2
        assert data["data"]["users"][0]["username"] == user_1_admin.username
        assert data["data"]["users"][0]["is_active"]
        assert data["data"]["users"][1]["username"] == inactive_user.username
        assert not data["data"]["users"][1]["is_active"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_users_list_ordered_by_suspension_date_with_default_order(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        # default order is ascending
        user_2.suspended_at = datetime.now(timezone.utc) - timedelta(days=2)
        user_3.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=suspended_at&with_suspended=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert data["data"]["users"][0]["username"] == user_2.username
        assert data["data"]["users"][0]["suspended_at"] is not None
        assert data["data"]["users"][1]["username"] == user_3.username
        assert data["data"]["users"][1]["suspended_at"] is not None
        assert data["data"]["users"][2]["username"] == user_1_admin.username
        assert data["data"]["users"][2]["suspended_at"] is None
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_suspension_date_ascending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        user_2.suspended_at = datetime.now(timezone.utc) - timedelta(days=2)
        user_3.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=suspended_at&order=asc&with_suspended=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert data["data"]["users"][0]["username"] == user_2.username
        assert data["data"]["users"][0]["suspended_at"] is not None
        assert data["data"]["users"][1]["username"] == user_3.username
        assert data["data"]["users"][1]["suspended_at"] is not None
        assert data["data"]["users"][2]["username"] == user_1_admin.username
        assert data["data"]["users"][2]["suspended_at"] is None
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_suspension_date_descending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        user_2.suspended_at = datetime.now(timezone.utc) - timedelta(days=2)
        user_3.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=suspended_at&order=desc&with_suspended=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert data["data"]["users"][0]["username"] == user_3.username
        assert data["data"]["users"][0]["suspended_at"] is not None
        assert data["data"]["users"][1]["username"] == user_2.username
        assert data["data"]["users"][1]["suspended_at"] is not None
        assert data["data"]["users"][2]["username"] == user_1_admin.username
        assert data["data"]["users"][2]["suspended_at"] is None
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_ordered_by_workouts_count_descending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=workouts_count&order=desc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert "toto" in data["data"]["users"][0]["username"]
        assert 1 == data["data"]["users"][0]["nb_workouts"]
        assert "admin" in data["data"]["users"][1]["username"]
        assert 0 == data["data"]["users"][1]["nb_workouts"]
        assert "sam" in data["data"]["users"][2]["username"]
        assert 0 == data["data"]["users"][2]["nb_workouts"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_gets_users_list_filtering_on_username(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users?q={user_2.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        assert user_2.username in data["data"]["users"][0]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_returns_username_matching_query(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users?q={user_2.username[1:]}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        assert user_2.username in data["data"]["users"][0]["username"]

    def test_it_filtering_on_username_is_case_insensitive(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users?q={user_2.username.upper()}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        assert user_2.username in data["data"]["users"][0]["username"]

    def test_it_does_not_return_inactive_user_by_default(
        self, app: Flask, user_1_admin: User, user_2: User, inactive_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users?q={inactive_user.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 0
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_inactive_user(
        self, app: Flask, user_1_admin: User, user_2: User, inactive_user: User
    ) -> None:
        inactive_user.hide_profile_in_users_directory = False
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users?q={inactive_user.username}&with_inactive=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        assert "inactive" in data["data"]["users"][0]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    @pytest.mark.parametrize(
        "input_desc, input_username",
        [
            ("not existing user", "not_existing"),
            ("user account format", "@sam@example.com"),
        ],
    )
    def test_it_returns_empty_users_list_filtering_on_username(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        input_desc: str,
        input_username: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"/api/users?q={input_username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 0
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_users_list_with_complex_query(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/users?order_by=username&order=desc&page=2&per_page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        assert "admin" in data["data"]["users"][0]["username"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 3,
        }

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "users:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.get(
            "/api/users",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestGetUsersAsModerator(ApiTestCaseMixin):
    @pytest.mark.parametrize(
        "input_description, input_params",
        [
            ("without params", ""),
            ("with inactive users", "?with_inactive=true"),
            ("with hidden users", "?with_hidden=true"),
            ("with suspended users", "?with_suspended=true"),
            (
                "all params",
                "?with_hidden=true&with_inactive=true&with_suspended=true",
            ),
        ],
    )
    def test_it_gets_users_list_without_inactive_hidden_or_suspended_users(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        inactive_user: User,
        user_3: User,
        user_4: User,
        input_description: str,
        input_params: str,
    ) -> None:
        user_2.hide_profile_in_users_directory = True
        user_4.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.get(
            f"/api/users{input_params}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 2
        assert data["data"]["users"][0] == jsonify_dict(
            user_1_moderator.serialize(current_user=user_1_moderator)
        )
        assert data["data"]["users"][1] == jsonify_dict(
            user_3.serialize(current_user=user_1_moderator)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_following_user_when_profile_is_hidden(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
    ) -> None:
        user_2.hide_profile_in_users_directory = True
        user_3.hide_profile_in_users_directory = True
        user_1_moderator.send_follow_request_to(user_2)
        user_2.approves_follow_request_from(user_1_moderator)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.get(
            "/api/users?with_following=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 2
        assert data["data"]["users"][0] == jsonify_dict(
            user_1_moderator.serialize(current_user=user_1_moderator)
        )
        assert data["data"]["users"][1] == jsonify_dict(
            user_2.serialize(current_user=user_1_moderator)
        )


class TestGetUsersAsUser(ApiTestCaseMixin):
    @pytest.mark.parametrize(
        "input_description, input_params",
        [
            ("without params", ""),
            ("with inactive users", "?with_inactive=true"),
            ("with hidden users", "?with_hidden=true"),
            ("with suspended users", "?with_suspended=true"),
            (
                "all params",
                "?with_hidden=true&with_inactive=true&with_suspended=true",
            ),
        ],
    )
    def test_it_gets_users_list_without_inactive_hidden_or_suspended_users(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        inactive_user: User,
        user_3: User,
        user_4: User,
        input_description: str,
        input_params: str,
    ) -> None:
        user_2.hide_profile_in_users_directory = True
        user_4.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users{input_params}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 2
        assert data["data"]["users"][0] == jsonify_dict(
            user_3.serialize(current_user=user_1)
        )
        assert data["data"]["users"][1] == jsonify_dict(
            user_1.serialize(current_user=user_1)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_following_user_when_profile_is_hidden(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
    ) -> None:
        user_2.hide_profile_in_users_directory = True
        user_3.hide_profile_in_users_directory = True
        user_1.send_follow_request_to(user_2)
        user_2.approves_follow_request_from(user_1)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/users?with_following=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data["status"] == "success"
        assert len(data["data"]["users"]) == 2
        assert data["data"]["users"][0] == jsonify_dict(
            user_1.serialize(current_user=user_1)
        )
        assert data["data"]["users"][1] == jsonify_dict(
            user_2.serialize(current_user=user_1)
        )

    def test_it_gets_users_list_with_workouts(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/users",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 3
        assert data["data"]["users"][0] == jsonify_dict(
            user_3.serialize(current_user=user_1)
        )

        assert data["data"]["users"][1] == jsonify_dict(
            user_1.serialize(current_user=user_1)
        )
        assert data["data"]["users"][2] == jsonify_dict(
            user_2.serialize(current_user=user_1)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }


class TestGetUsersAsSuspendedUser(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            "/api/users",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetUsersAsUnauthenticatedUser(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            "/api/users",
            content_type="application/json",
        )

        self.assert_401(response)


class TestGetUserPicture(ApiTestCaseMixin):
    def test_it_return_error_if_user_has_no_picture(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(f"/api/users/{user_1.username}/picture")

        self.assert_404_with_message(response, "No picture.")

    def test_it_returns_error_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get("/api/users/not_existing/picture")

        self.assert_404_with_entity(response, "user")


class TestUpdateUser(ReportMixin, ApiTestCaseMixin):
    def test_it_returns_error_if_auth_user_has_no_admin_rights(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/users/{user_1.username}",
            content_type="application/json",
            data=json.dumps(dict(role="admin")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_error_if_payload_is_empty(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_returns_error_if_payload_for_role_is_invalid(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(role="")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid role")

    @pytest.mark.parametrize("input_role", ["admin", "moderator"])
    def test_it_updates_user_role(
        self, app: Flask, user_1_admin: User, user_2: User, input_role: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(role=input_role)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        user = data["data"]["users"][0]
        assert user["email"] == user_2.email
        assert user["role"] == UserRole[input_role.upper()].name.lower()

    def test_it_returns_error_when_setting_owner_role_to_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(role="owner")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "'owner' can not be set via API, please user CLI instead"
        )

    @pytest.mark.parametrize("input_role", ["admin", "user"])
    def test_it_updates_role_for_moderator(
        self,
        app: Flask,
        user_1_admin: User,
        user_2_moderator: User,
        input_role: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2_moderator.username}",
            content_type="application/json",
            data=json.dumps(dict(role=input_role)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        user = data["data"]["users"][0]
        assert user["email"] == user_2_moderator.email
        assert user["role"] == UserRole[input_role.upper()].name.lower()

    def test_it_returns_error_when_setting_owner_role_to_moderator(
        self, app: Flask, user_1_admin: User, user_2_moderator: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2_moderator.username}",
            content_type="application/json",
            data=json.dumps(dict(role="owner")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "'owner' can not be set via API, please user CLI instead"
        )

    @pytest.mark.parametrize("input_role", ["moderator", "user"])
    def test_it_updates_role_for_admin_user(
        self,
        app: Flask,
        user_1_admin: User,
        user_2_admin: User,
        input_role: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2_admin.username}",
            content_type="application/json",
            data=json.dumps(dict(role=input_role)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        user = data["data"]["users"][0]
        assert user["email"] == user_2_admin.email
        assert user["role"] == UserRole[input_role.upper()].name.lower()

    def test_it_returns_error_when_setting_owner_role_to_admin(
        self, app: Flask, user_1_admin: User, user_2_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2_admin.username}",
            content_type="application/json",
            data=json.dumps(dict(role="owner")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "'owner' can not be set via API, please user CLI instead"
        )

    def test_it_returns_error_when_modifying_owner_role(
        self, app: Flask, user_1_owner: User, user_2_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2_admin.email
        )

        response = client.patch(
            f"/api/users/{user_1_owner.username}",
            content_type="application/json",
            data=json.dumps(dict(role="admin")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "user with owner rights can not be modified")

    def test_it_does_not_send_email_when_only_role_update(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        users_send_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(role="moderator")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        users_send_email_mock.send.assert_not_called()

    def test_it_resets_user_password(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        users_send_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        user_2_password = user_2.password

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(reset_password=True)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        assert user_2.password != user_2_password

    def test_it_calls_send_email_when_password_reset_is_successful(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        users_send_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        with patch(
            "fittrackee.users.users.User.encode_password_reset_token",
            return_value="xxx",
        ):
            response = client.patch(
                f"/api/users/{user_2.username}",
                content_type="application/json",
                data=json.dumps(dict(reset_password=True)),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        users_send_email_mock.send.assert_has_calls(
            [
                call(
                    {
                        "language": "en",
                        "email": user_2.email,
                    },
                    email_data={
                        "username": user_2.username,
                        "fittrackee_url": app.config["UI_URL"],
                    },
                    template="password_change",
                )
            ],
            call(
                {
                    "language": "en",
                    "email": user_2.email,
                },
                {
                    "expiration_delay": get_readable_duration(
                        app.config["PASSWORD_TOKEN_EXPIRATION_SECONDS"],
                        "en",
                    ),
                    "username": user_2.username,
                    "password_reset_url": (
                        f"{app.config['UI_URL']}/password-reset?token=xxx"
                    ),
                    "fittrackee_url": app.config["UI_URL"],
                },
                template="user_reset_password",
            ),
        )

    def test_it_does_not_send_email_when_email_sending_is_disabled(
        self,
        app_wo_email_activation: Flask,
        user_1_admin: User,
        user_2: User,
        users_send_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(reset_password=True)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        users_send_email_mock.send.assert_not_called()

    def test_it_returns_error_when_updating_email_with_invalid_address(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(new_email=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "valid email must be provided")

    def test_it_returns_error_when_new_email_is_same_as_current_email(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(new_email=user_2.email)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "new email must be different than current email"
        )

    def test_it_does_not_send_email_when_error_on_updating_email(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        users_send_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(new_email=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        users_send_email_mock.send.assert_not_called()

    def test_it_updates_user_email_to_confirm_when_email_sending_is_enabled(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        new_email = "new." + user_2.email
        user_2_email = user_2.email
        user_2_confirmation_token = user_2.confirmation_token

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(new_email=new_email)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        assert user_2.email == user_2_email
        assert user_2.email_to_confirm == new_email
        assert user_2.confirmation_token != user_2_confirmation_token

    def test_it_updates_user_email_when_email_sending_is_disabled(
        self, app_wo_email_activation: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1_admin.email
        )
        new_email = "new." + user_2.email

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(new_email=new_email)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        assert user_2.email == new_email
        assert user_2.email_to_confirm is None
        assert user_2.confirmation_token is None

    def test_it_calls_email_updated_to_new_address_when_password_reset_is_successful(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        users_send_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        new_email = "new." + user_2.email
        expected_token = self.random_string()

        with patch("secrets.token_urlsafe", return_value=expected_token):
            response = client.patch(
                f"/api/users/{user_2.username}",
                content_type="application/json",
                data=json.dumps(dict(new_email=new_email)),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        users_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": new_email,
            },
            {
                "username": user_2.username,
                "fittrackee_url": app.config["UI_URL"],
                "email_confirmation_url": (
                    f"{app.config['UI_URL']}/email-update"
                    f"?token={expected_token}"
                ),
            },
            template="email_update_to_new_email",
        )

    def test_it_does_not_call_email_updated_to_new_address_when_email_sending_is_disabled(  # noqa
        self,
        app_wo_email_activation: Flask,
        user_1_admin: User,
        user_2: User,
        users_send_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1_admin.email
        )
        new_email = "new." + user_2.email

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(new_email=new_email)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        users_send_email_mock.send.assert_not_called()

    def test_it_activates_user_account(
        self, app: Flask, user_1_admin: User, inactive_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{inactive_user.username}",
            content_type="application/json",
            data=json.dumps(dict(activate=True)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        user = data["data"]["users"][0]
        assert user["email"] == inactive_user.email
        assert user["is_active"] is True
        assert inactive_user.confirmation_token is None

    def test_it_deactivates_user_account(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            data=json.dumps(dict(activate=False)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["users"]) == 1
        user = data["data"]["users"][0]
        assert user["email"] == user_2.email
        assert user["is_active"] is False

    def test_a_user_can_not_deactivate_his_own_user_account(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f"/api/users/{user_1_admin.username}",
            content_type="application/json",
            data=json.dumps(dict(activate=False)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "users:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.patch(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestDeleteUser(ReportMixin, ApiTestCaseMixin):
    def test_user_can_delete_its_own_account(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert User.query.first() is None

    def test_suspended_user_can_delete_its_own_account(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.delete(
            f"/api/users/{suspended_user.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204

    def test_user_with_workout_can_delete_its_own_account(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        response = client.delete(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert User.query.first() is None

    def test_user_with_equipment_can_delete_its_own_account(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_w_shoes_equipment: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert User.query.first() is None

    def test_user_with_preferences_can_delete_its_own_account(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert User.query.first() is None

    def test_user_with_default_equipment_can_delete_its_own_account(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert User.query.first() is None

    def test_user_with_picture_can_delete_its_own_account(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client.post(
            "/api/auth/picture",
            data=dict(file=(BytesIO(b"avatar"), "avatar.png")),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        response = client.delete(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert User.query.first() is None

    def test_user_with_export_request_can_delete_its_own_account(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        db.session.add(UserDataExport(user_id=user_1.id))
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client.post(
            "/api/auth/picture",
            data=dict(file=(BytesIO(b"avatar"), "avatar.png")),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        response = client.delete(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert User.query.first() is None

    def test_user_with_notifications_can_delete_its_own_account(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client.post(
            "/api/auth/picture",
            data=dict(file=(BytesIO(b"avatar"), "avatar.png")),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        response = client.delete(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert (
            FollowRequest.query.filter_by(followed_user_id=user_1.id).first()
            is None
        )
        assert Notification.query.first() is None

    def test_user_with_reports_can_delete_its_own_account(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        user_3: User,
        user_4: User,
    ) -> None:
        report_from_user_3 = self.create_report(
            reporter=user_3, reported_object=user_1
        )
        report_from_user_1 = self.create_report(
            reporter=user_1, reported_object=user_4
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client.post(
            "/api/auth/picture",
            data=dict(file=(BytesIO(b"avatar"), "avatar.png")),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        response = client.delete(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert (
            FollowRequest.query.filter_by(followed_user_id=user_1.id).first()
            is None
        )
        assert set(Report.query.all()) == {
            report_from_user_3,
            report_from_user_1,
        }
        assert (
            Notification.query.filter_by(to_user_id=user_2_admin.id).first()
            is not None
        )

    def test_user_can_not_delete_another_user_account(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/users/{user_2.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_moderator_can_not_delete_another_user_account(
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.delete(
            f"/api/users/{user_2.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_error_when_deleting_non_existing_user(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            "/api/users/not_existing",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_entity(response, "user")

    def test_admin_can_delete_another_user_account(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        deleted_user_id = user_2.id

        response = client.delete(
            f"/api/users/{user_2.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert User.query.filter_by(id=deleted_user_id).first() is None

    def test_admin_can_delete_its_own_account(
        self, app: Flask, user_1_admin: User, user_2_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        deleted_user_id = user_1_admin.id

        response = client.delete(
            f"/api/users/{user_1_admin.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert User.query.filter_by(id=deleted_user_id).first() is None

    def test_admin_can_not_delete_owner_account(
        self,
        app: Flask,
        user_1_owner: User,
        user_2_admin: User,
        user_3_admin: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2_admin.email
        )

        response = client.delete(
            f"/api/users/{user_1_owner.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(
            response,
            "you can not delete owner account",
        )

    def test_admin_can_not_delete_its_own_account_if_no_other_user_with_admin_rights(  # noqa
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.delete(
            f"/api/users/{user_1_admin.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(
            response,
            "you can not delete your account, no other user has admin rights",
        )

    def test_owner_can_delete_his_own_account(
        self, app: Flask, user_1_owner: User, user_2_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_owner.email
        )

        response = client.delete(
            f"/api/users/{user_1_owner.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert User.query.filter_by(id=user_1_owner.id).first() is None

    def test_owner_can_not_delete_his_own_account_if_no_other_user_with_admin_rights(  # noqa
        self, app: Flask, user_1_owner: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_owner.email
        )

        response = client.delete(
            f"/api/users/{user_1_owner.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(
            response,
            "you can not delete your account, no other user has admin rights",
        )

    def test_it_enables_registration_after_user_delete_when_users_count_is_below_limit(  # noqa
        self,
        app_with_3_users_max: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_3_users_max, user_1_admin.email
        )
        client.delete(
            f"/api/users/{user_2.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        response = client.post(
            "/api/auth/register",
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
                    accepted_policy=True,
                )
            ),
            content_type="application/json",
        )

        assert response.status_code == 200

    def test_it_does_not_enable_registration_on_user_delete_when_users_count_is_not_below_limit(  # noqa
        self,
        app_with_3_users_max: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_1_paris: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_3_users_max, user_1_admin.email
        )

        client.delete(
            f"/api/users/{user_2.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        response = client.post(
            "/api/auth/register",
            data=json.dumps(
                dict(
                    username="justatest",
                    email="test@test.com",
                    password="12345678",
                    password_conf="12345678",
                    accepted_policy=True,
                )
            ),
            content_type="application/json",
        )

        self.assert_403(response, "error, registration is disabled")

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "users:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.delete(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestBlockUser(ApiTestCaseMixin):
    route = "/api/users/{username}/block"

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route.format(username=user_1.username),
            content_type="application/json",
        )

        self.assert_401(response)

    def test_it_returns_error_when_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(username=self.random_string()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_entity(response, "user")

    def test_it_returns_error_when_user_is_suspended(
        self, app: Flask, user_1: User, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.post(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_blocks_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(username=user_2.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert user_2.is_blocked_by(user_1)

    def test_it_removes_follow_request_if_exists(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(username=user_2.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert user_1.is_followed_by(user_2) == "false"

    def test_user_can_not_block_itself(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "users:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.delete(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestUnBlockUser(ApiTestCaseMixin):
    route = "/api/users/{username}/unblock"

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route.format(username=user_1.username),
            content_type="application/json",
        )

        self.assert_401(response)

    def test_it_returns_error_when_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(username=self.random_string()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_entity(response, "user")

    def test_it_returns_error_when_user_is_suspended(
        self, app: Flask, user_1: User, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.post(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_unblocks_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.blocks_user(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(username=user_2.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert user_2.is_blocked_by(user_1) is False

    def test_it_does_not_return_error_if_user_is_not_block(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(username=user_2.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert user_2.is_blocked_by(user_1) is False

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "users:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.delete(
            f"/api/users/{user_2.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestGetUserSanctions(ApiTestCaseMixin, ReportMixin, CommentMixin):
    route = "/api/users/{username}/sanctions"

    def create_report_actions(
        self, *, admin: User, auth_user: User, workout: Workout
    ) -> Tuple[ReportAction, ReportAction, ReportAction]:
        user_action = self.create_report_user_action(
            admin, auth_user, action_type="user_warning"
        )
        workout_action = self.create_report_workout_action(
            admin, auth_user, workout
        )
        comment = self.create_comment(auth_user, workout)
        comment_action = self.create_report_comment_action(
            admin, auth_user, comment
        )
        return user_action, workout_action, comment_action

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            self.route.format(username=user_1.username),
            content_type="application/json",
        )

        self.assert_401(response)

    def test_it_returns_error_when_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=self.random_string()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_entity(response, "user")

    def test_it_returns_error_when_user_is_not_authenticated_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_2.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_empty_list_when_no_report_actions(
        self, app: Flask, user_1: User, user_2_admin: User, user_3: User
    ) -> None:
        self.create_report_user_action(
            user_2_admin, user_3, action_type="user_warning"
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["sanctions"]) == 0
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_error_when_user_is_suspended(
        self, app: Flask, user_1: User, user_2_admin: User
    ) -> None:
        self.create_report_user_action(user_2_admin, user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["sanctions"]) == 1
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    @patch("fittrackee.users.users.ACTIONS_PER_PAGE", 2)
    @pytest.mark.parametrize("input_params", ["", "?page=1"])
    def test_it_returns_report_actions_first_page(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_params: str,
    ) -> None:
        _, workout_action, comment_action = self.create_report_actions(
            admin=user_2_admin,
            auth_user=user_1,
            workout=workout_cycling_user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_1.username) + input_params,
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["sanctions"] == [
            jsonify_dict(
                comment_action.serialize(current_user=user_1, full=False)
            ),
            jsonify_dict(
                workout_action.serialize(current_user=user_1, full=False)
            ),
        ]
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 3,
        }

    @patch("fittrackee.users.users.ACTIONS_PER_PAGE", 2)
    def test_it_returns_report_actions_page_2(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        user_action, _, _ = self.create_report_actions(
            admin=user_2_admin,
            auth_user=user_1,
            workout=workout_cycling_user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_1.username) + "?page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["sanctions"] == [
            jsonify_dict(
                user_action.serialize(current_user=user_1, full=False)
            ),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 3,
        }

    def test_it_returns_report_actions_when_author_is_moderator(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
    ) -> None:
        action = self.create_report_user_action(user_1_moderator, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.get(
            self.route.format(username=user_2.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["sanctions"] == [
            jsonify_dict(
                action.serialize(current_user=user_1_moderator, full=False)
            ),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    @pytest.mark.parametrize(
        "input_action_type", ["report_reopening", "report_resolution"]
    )
    def test_it_does_not_return_report_related_action(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        input_action_type: str,
    ) -> None:
        report = self.create_report(
            reporter=user_2_admin, reported_object=user_1
        )
        self.create_report_action(
            moderator=user_2_admin,
            user=user_1,
            action_type=input_action_type,
            report_id=report.id,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["sanctions"]) == 0

    @pytest.mark.parametrize(
        "input_action_type", ["user_unsuspension", "user_warning_lifting"]
    )
    def test_it_does_not_return_user_report_action_that_is_not_a_sanction(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        input_action_type: str,
    ) -> None:
        self.create_report_user_action(
            user_2_admin, user_1, action_type=input_action_type
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["sanctions"]) == 0

    def test_it_does_not_return_workout_unsuspension(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.create_report_workout_action(
            user_2_admin,
            user_1,
            workout_cycling_user_1,
            "workout_unsuspension",
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["sanctions"]) == 0

    def test_it_does_not_return_comment_unsuspension(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)
        self.create_report_comment_action(
            user_2_admin, user_1, comment, "comment_unsuspension"
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["sanctions"]) == 0


class TestGetUserLatestWorkouts(ApiTestCaseMixin, ReportMixin, CommentMixin):
    route = "/api/users/{username}/workouts"

    def test_it_returns_error_when_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=self.random_string()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_entity(response, "user")

    def test_it_returns_empty_list_when_user_has_no_workout(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_2.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"] == []

    def test_it_returns_empty_list_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_2.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"] == []

    def test_it_returns_only_public_workout_when_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        seven_workouts_user_1[1].workout_visibility = VisibilityLevel.PUBLIC
        seven_workouts_user_1[4].workout_visibility = VisibilityLevel.FOLLOWERS
        db.session.commit()
        client = app.test_client()

        response = client.get(self.route.format(username=user_1.username))

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"] == [
            jsonify_dict(seven_workouts_user_1[1].serialize())
        ]

    def test_it_returns_workouts_visible_to_authenticated_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        workout_cycling_user_2: Workout,
    ) -> None:
        seven_workouts_user_1[1].workout_visibility = VisibilityLevel.PUBLIC
        seven_workouts_user_1[4].workout_visibility = VisibilityLevel.FOLLOWERS
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"] == [
            jsonify_dict(seven_workouts_user_1[1].serialize(user=user_2))
        ]

    def test_it_returns_workouts_visible_to_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        workout_cycling_user_2: Workout,
    ) -> None:
        seven_workouts_user_1[1].workout_visibility = VisibilityLevel.PUBLIC
        seven_workouts_user_1[4].workout_visibility = VisibilityLevel.FOLLOWERS
        user_2.send_follow_request_to(user_1)
        user_1.approves_follow_request_from(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"] == [
            jsonify_dict(seven_workouts_user_1[4].serialize(user=user_2)),
            jsonify_dict(seven_workouts_user_1[1].serialize(user=user_2)),
        ]

    def test_it_returns_last_five_workouts_visible_to_workout_owner(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        workout_cycling_user_2: Workout,
    ) -> None:
        seven_workouts_user_1[1].workout_visibility = VisibilityLevel.PUBLIC
        seven_workouts_user_1[4].workout_visibility = VisibilityLevel.FOLLOWERS
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"] == [
            jsonify_dict(seven_workouts_user_1[6].serialize(user=user_1)),
            jsonify_dict(seven_workouts_user_1[5].serialize(user=user_1)),
            jsonify_dict(seven_workouts_user_1[3].serialize(user=user_1)),
            jsonify_dict(seven_workouts_user_1[4].serialize(user=user_1)),
            jsonify_dict(seven_workouts_user_1[2].serialize(user=user_1)),
        ]

    def test_it_does_not_return_suspended_workouts(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(username=user_1.username),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"] == []

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        client_scope: str,
        can_access: bool,
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
            self.route.format(username=user_1.username),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)
