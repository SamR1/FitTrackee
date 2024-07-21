import json
from datetime import datetime, timedelta
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.administration.models import (
    AdminAction,
    AdminActionAppeal,
)
from fittrackee.comments.models import Comment
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.reports.models import Report, ReportComment
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..comments.mixins import CommentMixin
from ..mixins import ApiTestCaseMixin, BaseTestMixin, UserModerationMixin
from ..utils import OAUTH_SCOPES, jsonify_dict
from ..workouts.mixins import WorkoutMixin


class ReportTestCase(
    CommentMixin, UserModerationMixin, ApiTestCaseMixin, BaseTestMixin
):
    route = "/api/reports"

    def create_reports(
        self,
        user_2: User,
        user_3: User,
        user_4: User,
        workout_cycling_user_2: Workout,
    ) -> List[Report]:
        reports = [self.create_report(reporter=user_2, reported_object=user_4)]
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        reports.append(
            self.create_report(
                reporter=user_3, reported_object=workout_cycling_user_2
            )
        )
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        reports.append(
            self.create_report(reporter=user_2, reported_object=comment)
        )
        return reports


class TestPostReport(ReportTestCase):
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
        "client_scope, can_access",
        {**OAUTH_SCOPES, "reports:write": True}.items(),
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


class TestPostCommentReport(ReportTestCase):
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

    def test_it_returns_400_when_user_is_comment_author(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
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

        self.assert_400(response, "users can not report their own comments")

    def test_it_returns_400_when_comment_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        comment.suspended_at = datetime.utcnow()
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

        self.assert_400(response, "comment already suspended")

    def test_it_returns_400_when_report_already_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        self.create_report(user_1, comment)
        db.session.commit()
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

        self.assert_400(response, "a report already exists")

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
        report_note = self.random_string()

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=report_note,
                    object_id=comment.short_id,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 201
        assert response.json == {"status": "created"}
        new_report = Report.query.filter_by(reported_by=user_1.id).first()
        assert new_report.note == report_note
        assert new_report.object_type == self.object_type
        assert new_report.reported_by == user_1.id
        assert new_report.reported_comment_id == comment.id
        assert new_report.reported_user_id == user_2.id
        assert new_report.reported_workout_id is None
        assert new_report.resolved is False
        assert new_report.resolved_at is None
        assert new_report.resolved_by is None
        assert new_report.updated_at is None


class TestPostWorkoutReport(ReportTestCase):
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

    def test_it_returns_400_when_user_is_workout_owner(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
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
                    object_id=workout_cycling_user_1.short_id,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "users can not report their own workouts")

    def test_it_returns_400_when_workout_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        report_note = self.random_string()

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=report_note,
                    object_id=workout_cycling_user_2.short_id,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "workout already suspended")

    def test_it_returns_400_when_report_already_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        self.create_report(user_1, workout_cycling_user_2)
        db.session.commit()
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

        self.assert_400(response, "a report already exists")

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
        report_note = self.random_string()

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=report_note,
                    object_id=workout_cycling_user_2.short_id,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 201
        assert response.json == {"status": "created"}
        new_report = Report.query.filter_by(reported_by=user_1.id).first()
        assert new_report.note == report_note
        assert new_report.object_type == self.object_type
        assert new_report.reported_by == user_1.id
        assert new_report.reported_comment_id is None
        assert new_report.reported_user_id == user_2.id
        assert new_report.reported_workout_id == workout_cycling_user_2.id
        assert new_report.resolved is False
        assert new_report.resolved_at is None
        assert new_report.resolved_by is None
        assert new_report.updated_at is None


class TestPostUserReport(ReportTestCase):
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

    def test_it_returns_400_when_user_is_reported_user(
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
                    object_id=user_1.username,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "users can not report their own profile")

    def test_it_returns_400_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        report_note = self.random_string()

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=report_note,
                    object_id=user_2.username,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "user already suspended")

    def test_it_returns_400_when_report_already_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        self.create_report(user_1, user_2)
        db.session.commit()
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

        self.assert_400(response, "a report already exists")

    def test_it_creates_report_for_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        report_note = self.random_string()

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(
                dict(
                    note=report_note,
                    object_id=user_2.username,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 201
        assert response.json == {"status": "created"}
        new_report = Report.query.filter_by(reported_by=user_1.id).first()
        assert new_report.note == report_note
        assert new_report.object_type == self.object_type
        assert new_report.reported_by == user_1.id
        assert new_report.reported_comment_id is None
        assert new_report.reported_user_id == user_2.id
        assert new_report.reported_workout_id is None
        assert new_report.resolved is False
        assert new_report.resolved_at is None
        assert new_report.resolved_by is None
        assert new_report.updated_at is None


class TestGetReportsAsAdmin(ReportTestCase):
    def test_it_returns_empty_list_when_no_reports(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["reports"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_all_reports(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 3
        assert data["reports"][0] == jsonify_dict(
            reports[2].serialize(user_1_admin)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[1].serialize(user_1_admin)
        )
        assert data["reports"][2] == jsonify_dict(
            reports[0].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_returns_reports_when_not_visible(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PRIVATE
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 1
        assert data["reports"][0] == jsonify_dict(
            report.serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    @pytest.mark.parametrize(
        "input_object_type, input_index",
        [("comment", 2), ("user", 0), ("workout", 1)],
    )
    def test_it_returns_reports_for_a_given_type(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_object_type: str,
        input_index: int,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?object_type={input_object_type}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 1
        assert data["reports"][0] == jsonify_dict(
            reports[input_index].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    @pytest.mark.parametrize(
        "input_object_type, input_index",
        [("comment", 2), ("user", 0), ("workout", 1)],
    )
    def test_it_returns_report_when_reported_object_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_object_type: str,
        input_index: int,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        db.session.delete(reports[input_index].reported_object)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?object_type={input_object_type}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 1
        assert data["reports"][0] == jsonify_dict(
            reports[input_index].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_returns_report_when_reporter_is_deleted(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        db.session.delete(user_2)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 1
        assert data["reports"][0] == jsonify_dict(
            report.serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_returns_only_unresolved_reports(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        reports[1].resolved = True
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?resolved=false",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 2
        assert data["reports"][0] == jsonify_dict(
            reports[2].serialize(user_1_admin)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[0].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_returns_only_resolved_reports(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        reports[1].resolved = True
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?resolved=true",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 1
        assert data["reports"][0] == jsonify_dict(
            reports[1].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    @pytest.mark.parametrize(
        "input_params",
        [
            "order_by=created_at",
            "order_by=created_at&order=desc",
        ],
    )
    def test_it_returns_reports_ordered_by_created_at_descending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_params: str,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?{input_params}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 3
        assert data["reports"][0] == jsonify_dict(
            reports[2].serialize(user_1_admin)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[1].serialize(user_1_admin)
        )
        assert data["reports"][2] == jsonify_dict(
            reports[0].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_returns_reports_ordered_by_created_at_ascending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?order_by=created_at&order=asc",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 3
        assert data["reports"][0] == jsonify_dict(
            reports[0].serialize(user_1_admin)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[1].serialize(user_1_admin)
        )
        assert data["reports"][2] == jsonify_dict(
            reports[2].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    @pytest.mark.parametrize(
        "input_params",
        ["order_by=updated_at", "order_by=updated_at&order=desc"],
    )
    def test_it_returns_reports_ordered_by_updated_at_descending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_params: str,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        now = datetime.utcnow()
        reports[1].updated_at = now
        reports[0].updated_at = now + timedelta(minutes=1)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?{input_params}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 3
        assert data["reports"][0] == jsonify_dict(
            reports[0].serialize(user_1_admin)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[1].serialize(user_1_admin)
        )
        assert data["reports"][2] == jsonify_dict(
            reports[2].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    @pytest.mark.parametrize(
        "input_order_by",
        [
            "id",
            "reported_comment_id",
            "reported_user_id",
            "reported_workout_id",
            "note",
            "invalid",
        ],
    )
    def test_it_returns_error_if_order_by_is_invalid(
        self, app: Flask, user_1_admin: User, input_order_by: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?order_by={input_order_by}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid 'order_by'")

    def test_it_returns_reports_ordered_by_update_at_ascending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        now = datetime.utcnow()
        reports[1].updated_at = now
        reports[0].updated_at = now + timedelta(minutes=1)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?order_by=updated_at&order=asc",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 3
        assert data["reports"][0] == jsonify_dict(
            reports[1].serialize(user_1_admin)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[0].serialize(user_1_admin)
        )
        assert data["reports"][2] == jsonify_dict(
            reports[2].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    @patch("fittrackee.reports.reports.REPORTS_PER_PAGE", 2)
    def test_it_returns_first_page(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?page=1",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 2
        assert data["reports"][0] == jsonify_dict(
            reports[2].serialize(user_1_admin)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[1].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 3,
        }

    @patch("fittrackee.reports.reports.REPORTS_PER_PAGE", 2)
    def test_it_returns_last_page(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?page=2",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["reports"]) == 1
        assert data["reports"][0] == jsonify_dict(
            reports[0].serialize(user_1_admin)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 3,
        }

    def test_it_returns_reports_for_a_given_reporter(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route}?reporter={user_3.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["reports"] == [
            jsonify_dict(reports[1].serialize(user_1_admin))
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }


class TestGetReportsAsUser(ReportTestCase):
    def test_it_returns_only_reports_created_by_authenticated_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.create_reports(user_2, user_3, user_4, workout_cycling_user_2)
        report = self.create_report(user_1, workout_cycling_user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["reports"] == [jsonify_dict(report.serialize(user_1))]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_ignores_reporter_parameter(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.create_reports(user_2, user_3, user_4, workout_cycling_user_2)
        report = self.create_report(user_1, workout_cycling_user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?reporter={user_3.username}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["reports"] == [jsonify_dict(report.serialize(user_1))]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }


class TestGetReportsAsUnauthenticatedUser(ReportTestCase):
    def test_it_returns_401_when_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(self.route, content_type="application/json")

        self.assert_401(response)


class TestGetReportsOAuth2Scopes(ReportTestCase):
    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "reports:read": True}.items(),
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
            self.route,
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {access_token}",
            ),
        )

        self.assert_response_scope(response, can_access)


class GetReportTestCase(ReportTestCase):
    route = "/api/reports/{report_id}"


class TestGetReportAsAdmin(GetReportTestCase):
    def test_it_returns_404_when_report_does_not_exist(
        self, app: Flask, user_1_admin: User
    ) -> None:
        report_id = self.random_int()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route.format(report_id=report_id),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, f"report not found (id: {report_id})"
        )

    def test_it_returns_report_from_authenticated_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        report = self.create_report(user_1_admin, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route.format(report_id=report.id),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["report"] == jsonify_dict(
            report.serialize(user_1_admin, full=True)
        )

    def test_it_returns_report_from_another_user(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_2, reported_object=user_3)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route.format(report_id=report.id),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["report"] == jsonify_dict(
            report.serialize(user_1_admin, full=True)
        )


class TestGetReportAsUser(GetReportTestCase):
    def test_it_returns_report_from_authenticated_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        report = self.create_report(user_1, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(report_id=report.id),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["report"] == jsonify_dict(report.serialize(user_1))

    def test_it_does_not_return_report_from_another_user(
        self, app: Flask, user_1: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_2, reported_object=user_3)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(report_id=report.id),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        self.assert_404_with_message(
            response, f"report not found (id: {report.id})"
        )


class TestGetReportAsUnauthenticatedUser(GetReportTestCase):
    def test_it_returns_401_when_user_is_not_authenticated(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        report = self.create_report(user_1, reported_object=user_2)
        client = app.test_client()

        response = client.get(
            self.route.format(report_id=report.id),
            content_type="application/json",
        )

        self.assert_401(response)


class TestGetReportOAuth2Scopes(GetReportTestCase):
    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "reports:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        report = self.create_report(user_1, reported_object=user_2)
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.get(
            self.route.format(report_id=report.id),
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {access_token}",
            ),
        )

        self.assert_response_scope(response, can_access)


class TestPatchReport(ReportTestCase):
    route = "/api/reports/{report_id}"

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.patch(
            self.route.format(report_id=self.random_int()),
            content_type="application/json",
            data=json.dumps(
                dict(
                    comment=self.random_string(),
                )
            ),
        )

        self.assert_401(response)

    def test_it_returns_error_if_user_has_no_admin_rights(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        report = self.create_report(user_1, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(report_id=report.id),
            content_type="application/json",
            data=json.dumps(
                dict(
                    comment=self.random_string(),
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_404_when_no_report(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        report_id = self.random_int()

        response = client.patch(
            self.route.format(report_id=report_id),
            content_type="application/json",
            data=json.dumps(dict(comment=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, f"report not found (id: {report_id})"
        )

    def test_it_returns_400_when_comment_is_missing(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            self.route.format(report_id=report.id),
            content_type="application/json",
            data='{}',
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_adds_a_comment(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        now = datetime.utcnow()
        comment = self.random_string()

        with travel(now, tick=False):
            response = client.patch(
                self.route.format(report_id=report.id),
                content_type="application/json",
                data=json.dumps(dict(comment=comment)),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["report"]["resolved"] is False
        assert data["report"]["resolved_at"] is None
        assert data["report"]["updated_at"] == self.get_date_string(date=now)
        assert len(data["report"]["comments"]) == 1
        assert data["report"]["comments"][0]["comment"] == comment

    def test_it_resolves_a_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        report_comment = ReportComment(
            comment=self.random_string(),
            report_id=report.id,
            user_id=user_1_admin.id,
        )
        db.session.add(report_comment)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        now = datetime.utcnow()
        comment = self.random_string()

        with travel(now, tick=False):
            response = client.patch(
                self.route.format(report_id=report.id),
                content_type="application/json",
                data=json.dumps(dict(comment=comment, resolved=True)),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["report"]["resolved"] is True
        date_string = self.get_date_string(date=now)
        assert data["report"]["resolved_at"] == date_string
        assert data["report"]["resolved_by"] == jsonify_dict(
            user_1_admin.serialize(user_1_admin)
        )
        assert data["report"]["updated_at"] == date_string
        assert len(data["report"]["comments"]) == 2
        assert data["report"]["comments"][1]["comment"] == comment

    def test_it_marks_a_report_as_unresolved(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        report.resolved = True
        report.resolved_at = datetime.utcnow()
        report.resolved_by = user_1_admin.id
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        now = datetime.utcnow()
        comment = self.random_string()

        with travel(now, tick=False):
            response = client.patch(
                self.route.format(report_id=report.id),
                content_type="application/json",
                data=json.dumps(dict(comment=comment, resolved=False)),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["report"]["resolved"] is False
        assert data["report"]["resolved_at"] is None
        assert data["report"]["resolved_by"] is None
        assert data["report"]["updated_at"] == self.get_date_string(date=now)
        assert len(data["report"]["comments"]) == 1
        assert data["report"]["comments"][0]["comment"] == comment

    def test_it_adds_comment_one_resolved_report(
        self, app: Flask, user_1_admin: User, user_2_admin: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2_admin)
        report.resolved = True
        resolved_time = datetime.utcnow()
        report.resolved_at = resolved_time
        report.resolved_by = user_2_admin.id
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        comment_time = datetime.utcnow()
        comment = self.random_string()

        with travel(comment_time, tick=False):
            response = client.patch(
                self.route.format(report_id=report.id),
                content_type="application/json",
                data=json.dumps(dict(comment=comment)),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["report"]["resolved"] is True
        assert data["report"]["resolved_at"] == self.get_date_string(
            date=resolved_time
        )
        assert data["report"]["resolved_by"] == jsonify_dict(
            user_2_admin.serialize(user_1_admin)
        )
        assert data["report"]["updated_at"] == self.get_date_string(
            date=comment_time
        )
        assert len(data["report"]["comments"]) == 1
        assert data["report"]["comments"][0]["comment"] == comment


class TestPostReportAdminAction(ReportTestCase):
    route = "/api/reports/{report_id}/admin-actions"

    def test_it_returns_401_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route.format(report_id=self.random_int()),
            content_type="application/json",
            json={
                "action_type": "user_suspension",
                "username": user_1.username,
            },
        )

        self.assert_401(response)

    def test_it_returns_403_if_user_has_no_admin_rights(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        report = self.create_report(user_1, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_suspension",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_404_when_no_report(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        report_id = self.random_int()

        response = client.post(
            self.route.format(report_id=report_id),
            content_type="application/json",
            json={
                "action_type": "user_suspension",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, f"report not found (id: {report_id})"
        )

    def test_it_returns_400_when_action_type_is_missing(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_returns_400_when_action_type_is_invalid(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": self.random_string(),
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid 'action_type'")


class TestPostReportAdminActionForUserAction(ReportTestCase):
    route = "/api/reports/{report_id}/admin-actions"

    def test_it_returns_400_when_username_is_missing_on_user_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={"action_type": "user_suspension"},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "'username' is missing")

    def test_it_returns_400_when_username_is_invalid_on_user_admin_action(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_suspension",
                "username": self.random_string(),
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid 'username'")

    def test_it_returns_400_when_user_is_deleted(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        username = user_2.username
        db.session.delete(user_2)
        db.session.commit()

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={"action_type": "user_suspension", "username": username},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid 'username'")

    def test_it_suspends_user(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            response = client.post(
                self.route.format(report_id=report.id),
                content_type="application/json",
                json={
                    "action_type": "user_suspension",
                    "username": user_2.username,
                },
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        assert (
            User.query.filter_by(username=user_2.username).first().suspended_at
            == now
        )

    def test_it_returns_400_when_when_user_already_suspended(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_suspension",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, f"user '{user_2.username}' already suspended"
        )

    def test_it_reactivates_user(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_unsuspension",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        assert (
            User.query.filter_by(username=user_2.username).first().suspended_at
            is None
        )

    def test_it_creates_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_suspension",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        assert (
            AdminAction.query.filter_by(
                admin_user_id=user_1_admin.id, user_id=user_2.id
            ).first()
            is not None
        )

    def test_it_returns_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        report_comment = ReportComment(
            comment=self.random_string(),
            report_id=report.id,
            user_id=user_1_admin.id,
        )
        db.session.add(report_comment)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_suspension",
                "username": user_2.username,
                "reason": self.random_string(),
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        updated_report = Report.query.filter_by(id=report.id).first()
        assert data["report"] == jsonify_dict(
            updated_report.serialize(user_1_admin, full=True)
        )

    def test_it_does_not_enable_registration_on_user_suspension(
        self,
        app_with_3_users_max: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report = self.create_report(user_1_admin, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_3_users_max, user_1_admin.email
        )

        client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_suspension",
                "username": user_2.username,
                "reason": self.random_string(),
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
                    password_conf=self.random_string(),
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
        )

        self.assert_403(response, 'error, registration is disabled')

    def test_it_sends_an_email_on_user_suspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_suspension_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_suspension",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        user_suspension_email_mock.send.assert_called_once()

    def test_it_sends_an_email_on_user_reactivation(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_unsuspension_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_unsuspension",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        user_unsuspension_email_mock.send.assert_called_once()

    def test_it_does_not_send_when_email_sending_is_disabled(
        self,
        app_wo_email_activation: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_suspension_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_suspension",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        user_suspension_email_mock.send.assert_not_called()


class TestPostReportAdminActionForWorkoutAction(ReportTestCase):
    route = "/api/reports/{report_id}/admin-actions"

    def test_it_returns_400_when_workout_id_is_missing_on_workout_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={"action_type": "workout_suspension"},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "'workout_id' is missing")

    def test_it_returns_400_when_workout_is_invalid_on_workout_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "workout_suspension",
                "workout_id": self.random_short_id(),
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid 'workout_id'")

    def test_it_returns_400_when_workout_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        short_id = workout_cycling_user_2.short_id
        db.session.delete(workout_cycling_user_2)
        db.session.commit()

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={"action_type": "workout_suspension", "workout_id": short_id},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid 'workout_id'")

    def test_it_suspends_workout_by_setting_moderation_date(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            response = client.post(
                self.route.format(report_id=report.id),
                content_type="application/json",
                json={
                    "action_type": "workout_suspension",
                    "workout_id": workout_cycling_user_2.short_id,
                },
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        assert (
            Workout.query.filter_by(id=workout_cycling_user_2.id)
            .first()
            .suspended_at
            == now
        )

    def test_it_returns_400_when_when_workout_already_suspended(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        db.session.commit()

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "workout_suspension",
                "workout_id": workout_cycling_user_2.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            f"workout '{workout_cycling_user_2.short_id}' already suspended",
        )

    def test_it_unsuspends_workout(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "workout_unsuspension",
                "workout_id": workout_cycling_user_2.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        assert (
            Workout.query.filter_by(id=workout_cycling_user_2.id)
            .first()
            .suspended_at
            is None
        )

    def test_it_creates_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "workout_suspension",
                "workout_id": workout_cycling_user_2.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        assert (
            AdminAction.query.filter_by(
                admin_user_id=user_1_admin.id, user_id=user_2.id
            ).first()
            is not None
        )

    def test_it_returns_report(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "workout_suspension",
                "workout_id": workout_cycling_user_2.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        updated_report = Report.query.filter_by(id=report.id).first()
        assert data["report"] == jsonify_dict(
            updated_report.serialize(user_1_admin, full=True)
        )

    def test_it_sends_an_email_on_workout_suspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_suspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "workout_suspension",
                "workout_id": workout_cycling_user_2.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        workout_suspension_email_mock.send.assert_called_once()

    def test_it_sends_an_email_on_workout_unsuspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_unsuspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "workout_unsuspension",
                "workout_id": workout_cycling_user_2.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        workout_unsuspension_email_mock.send.assert_called_once()

    def test_it_does_not_send_an_email_when_email_sending_is_disabled(
        self,
        app_wo_email_activation: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_suspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report = self.create_report(
            user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "workout_suspension",
                "workout_id": workout_cycling_user_2.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        workout_suspension_email_mock.send.assert_not_called()


class TestPostReportAdminActionForCommentAction(ReportTestCase):
    route = "/api/reports/{report_id}/admin-actions"

    def test_it_returns_400_when_comment_id_is_missing_on_comment_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, PrivacyLevel.PUBLIC
        )
        report = self.create_report(user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={"action_type": "comment_suspension"},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "'comment_id' is missing")

    def test_it_returns_400_when_comment_is_invalid_on_comment_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, PrivacyLevel.PUBLIC
        )
        report = self.create_report(user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "comment_suspension",
                "comment_id": self.random_short_id(),
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid 'comment_id'")

    def test_it_returns_400_when_comment_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, PrivacyLevel.PUBLIC
        )
        report = self.create_report(user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        short_id = comment.short_id
        db.session.delete(comment)
        db.session.commit()

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={"action_type": "comment_suspension", "comment_id": short_id},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid 'comment_id'")

    def test_it_suspends_comment_by_setting_moderation_date(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, PrivacyLevel.PUBLIC
        )
        report = self.create_report(user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            response = client.post(
                self.route.format(report_id=report.id),
                content_type="application/json",
                json={
                    "action_type": "comment_suspension",
                    "comment_id": comment.short_id,
                },
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        assert (
            Comment.query.filter_by(id=comment.id).first().suspended_at == now
        )

    def test_it_returns_400_when_when_comment_already_suspended(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, PrivacyLevel.PUBLIC
        )
        report = self.create_report(user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        comment.suspended_at = datetime.utcnow()
        db.session.commit()
        now = datetime.utcnow()

        with travel(now, tick=False):
            response = client.post(
                self.route.format(report_id=report.id),
                content_type="application/json",
                json={
                    "action_type": "comment_suspension",
                    "comment_id": comment.short_id,
                },
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_400(
            response,
            f"comment '{comment.short_id}' already suspended",
        )

    def test_it_unsuspends_comment(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, PrivacyLevel.PUBLIC
        )
        report = self.create_report(user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "comment_unsuspension",
                "comment_id": comment.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        assert (
            Comment.query.filter_by(id=comment.id).first().suspended_at is None
        )

    def test_it_creates_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, PrivacyLevel.PUBLIC
        )
        report = self.create_report(user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "comment_suspension",
                "comment_id": comment.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        assert (
            AdminAction.query.filter_by(
                admin_user_id=user_1_admin.id, user_id=user_3.id
            ).first()
            is not None
        )

    def test_it_returns_report(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, PrivacyLevel.PUBLIC
        )
        report = self.create_report(user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            response = client.post(
                self.route.format(report_id=report.id),
                content_type="application/json",
                json={
                    "action_type": "comment_suspension",
                    "comment_id": comment.short_id,
                },
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        updated_report = Report.query.filter_by(id=report.id).first()
        assert data["report"] == jsonify_dict(
            updated_report.serialize(user_1_admin, full=True)
        )

    def test_it_sends_an_email_on_comment_suspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        comment_suspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text=f"@{user_2.username}",
            text_visibility=PrivacyLevel.PUBLIC,
            with_mentions=True,
        )
        report = self.create_report(user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "comment_suspension",
                "comment_id": comment.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        comment_suspension_email_mock.send.assert_called_once()

    def test_it_sends_an_email_on_comment_unsuspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        comment_unsuspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text=f"@{user_2.username}",
            text_visibility=PrivacyLevel.PUBLIC,
            with_mentions=True,
        )
        report = self.create_report(user_2, reported_object=comment)
        comment.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "comment_unsuspension",
                "comment_id": comment.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        comment_unsuspension_email_mock.send.assert_called_once()

    def test_it_does_not_send_email_when_email_sending_id_disabled(
        self,
        app_wo_email_activation: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        comment_suspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text=f"@{user_2.username}",
            text_visibility=PrivacyLevel.PUBLIC,
            with_mentions=True,
        )
        report = self.create_report(user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1_admin.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "comment_suspension",
                "comment_id": comment.short_id,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        comment_suspension_email_mock.send.assert_not_called()


class TestProcessAdminActionAppeal(
    CommentMixin, WorkoutMixin, UserModerationMixin, ApiTestCaseMixin
):
    route = '/api/suspensions/appeals/{appeal_id}'

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.patch(
            self.route.format(appeal_id=self.random_short_id()),
            data=json.dumps(dict(approved=False)),
            content_type="application/json",
        )

        self.assert_401(response)

    def test_it_returns_403_when_user_has_no_admin_rights(
        self, app: Flask, user_1: User
    ) -> None:
        appeal_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(appeal_id=appeal_id),
            data=json.dumps(dict(approved=False)),
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_404_if_appeal_does_not_exist(
        self, app: Flask, user_1_admin: User
    ) -> None:
        appeal_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            self.route.format(appeal_id=appeal_id),
            data=json.dumps(dict(approved=False)),
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response,
            f"appeal not found (id: {appeal_id})",
        )

    @pytest.mark.parametrize(
        "input_data", [{"approved": True}, {"reason": "foo"}, {}]
    )
    def test_it_returns_error_when_data_are_missing(
        self, app: Flask, user_1_admin: User, user_2: User, input_data: Dict
    ) -> None:
        suspension_action = self.create_user_suspension_action(
            user_1_admin, user_2
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            self.route.format(appeal_id=appeal.short_id),
            data=json.dumps(input_data),
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    @pytest.mark.parametrize(
        "input_data",
        [
            {"approved": True, "reason": "ok"},
            {"approved": False, "reason": "not ok"},
        ],
    )
    def test_it_processes_user_suspension_appeal(
        self, app: Flask, user_1_admin: User, user_2: User, input_data: Dict
    ) -> None:
        suspension_action = self.create_user_suspension_action(
            user_1_admin, user_2
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            self.route.format(appeal_id=appeal.short_id),
            data=json.dumps(input_data),
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        assert response.json == {
            "status": "success",
            "appeal": jsonify_dict(appeal.serialize(user_1_admin)),
        }
        appeal = AdminActionAppeal.query.filter_by(id=appeal.id).first()
        assert appeal.approved is input_data["approved"]
        assert appeal.reason == input_data["reason"]

    @pytest.mark.parametrize(
        "input_data",
        [
            {"approved": True, "reason": "ok"},
            {"approved": False, "reason": "not ok"},
        ],
    )
    def test_it_processes_comment_suspension_appeal(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_data: Dict,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        suspension_action = self.create_admin_comment_suspension_action(
            user_1_admin, user_3, comment
        )
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_3)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            self.route.format(appeal_id=appeal.short_id),
            data=json.dumps(input_data),
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        assert response.json == {
            "status": "success",
            "appeal": jsonify_dict(appeal.serialize(user_1_admin)),
        }
        appeal = AdminActionAppeal.query.filter_by(id=appeal.id).first()
        assert appeal.approved is input_data["approved"]
        assert appeal.reason == input_data["reason"]

    @pytest.mark.parametrize(
        "input_data",
        [
            {"approved": True, "reason": "ok"},
            {"approved": False, "reason": "not ok"},
        ],
    )
    def test_it_processes_workout_suspension_appeal(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_data: Dict,
    ) -> None:
        suspension_action = self.create_admin_workout_suspension_action(
            user_1_admin, user_2, workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            response = client.patch(
                self.route.format(appeal_id=appeal.short_id),
                data=json.dumps(input_data),
                content_type="application/json",
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        assert response.json == {
            "status": "success",
            "appeal": jsonify_dict(appeal.serialize(user_1_admin)),
        }
        appeal = AdminActionAppeal.query.filter_by(id=appeal.id).first()
        assert appeal.approved is input_data["approved"]
        assert appeal.reason == input_data["reason"]

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
        appeal_id = self.random_short_id()
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.patch(
            self.route.format(appeal_id=appeal_id),
            data=json.dumps(dict(approved=False, reason="OK")),
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)
