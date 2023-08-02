import json

import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.reports.models import Report
from fittrackee.tests.comments.utils import CommentMixin
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin, BaseTestMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


class PostReportTestCase(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    route = "/api/reports"


class TestPostReport(PostReportTestCase):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=self.random_short_id(),
                    object_type="comment",
                )
            ),
        )

        self.assert_401(response)

    def test_it_returns_400_when_object_type_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=self.random_short_id(),
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_returns_400_when_object_type_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=self.random_short_id(),
                    object_type=self.random_string(),
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_returns_400_when_note_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    object_id=self.random_short_id(),
                    object_type="comment",
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_returns_400_when_object_id_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_type="comment",
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'reports:write': True}.items(),
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

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=self.random_short_id(),
                    object_type="comment",
                )
            ),
            headers=dict(
                Authorization=f"Bearer {access_token}",
            ),
        )

        self.assert_response_scope(response, can_access)


class TestPostCommentReport(PostReportTestCase):
    object_type = "comment"

    def test_it_returns_404_when_comment_is_not_found(
        self, app: Flask, user_1: User
    ) -> None:
        comment_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=comment_id,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"comment not found (id: {comment_id})",
        )

    def test_it_returns_404_when_comment_is_not_visible_to_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=comment.short_id,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"comment not found (id: {comment.short_id})",
        )

    def test_it_creates_report_for_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=comment.short_id,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        new_report = Report.query.filter_by(reported_by=user_1.id).first()
        assert data["status"] == "created"
        assert data["report"] == jsonify_dict(new_report.serialize(user_1))


class TestPostWorkoutReport(PostReportTestCase):
    object_type = "workout"

    def test_it_returns_404_when_workout_is_not_found(
        self, app: Flask, user_1: User
    ) -> None:
        workout_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=workout_id,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_id})",
        )

    def test_it_returns_404_when_workout_is_not_visible_to_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PRIVATE
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=workout_cycling_user_2.short_id,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )

    def test_it_creates_report_for_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=workout_cycling_user_2.short_id,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        new_report = Report.query.filter_by(reported_by=user_1.id).first()
        assert data["status"] == "created"
        assert data['report'] == jsonify_dict(new_report.serialize(user_1))


class TestPostUserReport(PostReportTestCase):
    object_type = "user"

    def test_it_returns_404_when_user_is_not_found(
        self, app: Flask, user_1: User
    ) -> None:
        username = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=username,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"user not found (username: {username})",
        )

    def test_it_returns_404_when_user_is_inactive(
        self, app: Flask, user_1: User, inactive_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=inactive_user.username,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"user not found (username: {inactive_user.username})",
        )

    def test_it_creates_report_for_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=self.random_string(),
                    object_id=user_2.username,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        new_report = Report.query.filter_by(reported_by=user_1.id).first()
        assert data["status"] == "created"
        assert data['report'] == jsonify_dict(new_report.serialize(user_1))
