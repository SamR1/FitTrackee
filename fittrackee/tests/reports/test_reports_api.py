import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.comments.models import Comment
from fittrackee.reports.models import (
    USER_ACTION_TYPES,
    Report,
    ReportAction,
    ReportActionAppeal,
    ReportComment,
)
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ..comments.mixins import CommentMixin
from ..mixins import ApiTestCaseMixin, BaseTestMixin, ReportMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


class ReportTestCase(
    CommentMixin, ReportMixin, ApiTestCaseMixin, BaseTestMixin
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
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        reports.append(
            self.create_report(
                reporter=user_3, reported_object=workout_cycling_user_2
            )
        )
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
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
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
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
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        comment.suspended_at = datetime.now(timezone.utc)
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
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        self.create_report(reporter=user_1, reported_object=comment)
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
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
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
        new_report = Report.query.filter_by(reported_by=user_1.id).one()
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

    def test_it_creates_report_for_comment_when_user_report_exists_for_same_user(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        self.create_report(reporter=user_1, reported_object=user_2)
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
        new_report = Report.query.filter_by(
            reported_by=user_1.id, object_type="comment"
        ).one()
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

    def test_it_creates_report_for_comment_when_workout_report_exists_for_same_user(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        self.create_report(
            reporter=user_1, reported_object=workout_cycling_user_2
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
        new_report = Report.query.filter_by(
            reported_by=user_1.id, object_type="comment"
        ).one()
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
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
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
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        self.create_report(
            reporter=user_1, reported_object=workout_cycling_user_2
        )
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
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
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
        new_report = Report.query.filter_by(reported_by=user_1.id).one()
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

    def test_it_creates_report_for_workout_when_user_report_exists_for_same_user(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        self.create_report(reporter=user_1, reported_object=user_2)
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
        new_report = Report.query.filter_by(
            reported_by=user_1.id, object_type="workout"
        ).one()
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

    def test_it_creates_report_for_workout_when_comment_report_exists_for_same_user(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        self.create_report(reporter=user_1, reported_object=comment)
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
        new_report = Report.query.filter_by(
            reported_by=user_1.id, object_type="workout"
        ).one()
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
        user_2.suspended_at = datetime.now(timezone.utc)
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

    def test_it_returns_400_when_user_report_already_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        self.create_report(reporter=user_1, reported_object=user_2)
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
        new_report = Report.query.filter_by(reported_by=user_1.id).one()
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

    def test_it_creates_report_for_user_when_content_report_exists_for_same_user(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.create_report(
            reporter=user_1, reported_object=workout_cycling_user_2
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
                    object_id=user_2.username,
                    object_type=self.object_type,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 201
        assert response.json == {"status": "created"}
        new_report = Report.query.filter_by(
            reported_by=user_1.id, object_type="user"
        ).one()
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


class TestGetReportsAsModerator(ReportTestCase):
    def test_it_returns_empty_list_when_no_reports(
        self, app: Flask, user_1_moderator: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
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
            app, user_1_moderator.email
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
            reports[2].serialize(user_1_moderator)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[1].serialize(user_1_moderator)
        )
        assert data["reports"][2] == jsonify_dict(
            reports[0].serialize(user_1_moderator)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_returns_reports_when_reported_object_not_visible_to_moderator(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PRIVATE
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            report.serialize(user_1_moderator)
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
        user_1_moderator: User,
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
            app, user_1_moderator.email
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
            reports[input_index].serialize(user_1_moderator)
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
        user_1_moderator: User,
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
            app, user_1_moderator.email
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
            reports[input_index].serialize(user_1_moderator)
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_returns_report_when_reporter_is_deleted(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        db.session.delete(user_2)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            report.serialize(user_1_moderator)
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
        user_1_moderator: User,
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
            app, user_1_moderator.email
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
            reports[2].serialize(user_1_moderator)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[0].serialize(user_1_moderator)
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
        user_1_moderator: User,
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
            app, user_1_moderator.email
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
            reports[1].serialize(user_1_moderator)
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
        user_1_moderator: User,
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
            app, user_1_moderator.email
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
            reports[2].serialize(user_1_moderator)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[1].serialize(user_1_moderator)
        )
        assert data["reports"][2] == jsonify_dict(
            reports[0].serialize(user_1_moderator)
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
        user_1_moderator: User,
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
            app, user_1_moderator.email
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
            reports[0].serialize(user_1_moderator)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[1].serialize(user_1_moderator)
        )
        assert data["reports"][2] == jsonify_dict(
            reports[2].serialize(user_1_moderator)
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
        user_1_moderator: User,
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
        now = datetime.now(timezone.utc)
        reports[1].updated_at = now
        reports[0].updated_at = now + timedelta(minutes=1)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            reports[0].serialize(user_1_moderator)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[1].serialize(user_1_moderator)
        )
        assert data["reports"][2] == jsonify_dict(
            reports[2].serialize(user_1_moderator)
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
        self, app: Flask, user_1_moderator: User, input_order_by: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        reports = self.create_reports(
            user_2, user_3, user_4, workout_cycling_user_2
        )
        now = datetime.now(timezone.utc)
        reports[1].updated_at = now
        reports[0].updated_at = now + timedelta(minutes=1)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            reports[1].serialize(user_1_moderator)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[0].serialize(user_1_moderator)
        )
        assert data["reports"][2] == jsonify_dict(
            reports[2].serialize(user_1_moderator)
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
        user_1_moderator: User,
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
            app, user_1_moderator.email
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
            reports[2].serialize(user_1_moderator)
        )
        assert data["reports"][1] == jsonify_dict(
            reports[1].serialize(user_1_moderator)
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
        user_1_moderator: User,
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
            app, user_1_moderator.email
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
            reports[0].serialize(user_1_moderator)
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
        user_1_moderator: User,
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
            app, user_1_moderator.email
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
            jsonify_dict(reports[1].serialize(user_1_moderator))
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }


class TestGetReportsAsAdmin(ReportTestCase):
    def test_it_returns_reports(
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


class TestGetReportsAsUser(ReportTestCase):
    def test_it_does_not_return_reports(
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
        self.create_report(
            reporter=user_1, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


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
        self,
        app: Flask,
        user_1_moderator: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_moderator, scope=client_scope
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


class TestGetReportAsModerator(GetReportTestCase):
    def test_it_returns_404_when_report_does_not_exist(
        self, app: Flask, user_1_moderator: User
    ) -> None:
        report_id = self.random_int()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        report = self.create_report(
            reporter=user_1_moderator, reported_object=user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            report.serialize(user_1_moderator, full=True)
        )

    def test_it_returns_report_from_another_user(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            report.serialize(user_1_moderator, full=True)
        )


class TestGetReportAsAdmin(GetReportTestCase):
    def test_it_returns_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
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
    def test_it_does_not_return_report(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        report = self.create_report(reporter=user_1, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(report_id=report.id),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetReportAsUnauthenticatedUser(GetReportTestCase):
    def test_it_returns_401_when_user_is_not_authenticated(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        report = self.create_report(reporter=user_1, reported_object=user_2)
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
        user_1_admin: User,
        user_2: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        report = self.create_report(
            reporter=user_1_admin, reported_object=user_2
        )
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
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

    def test_it_returns_error_if_user_has_no_moderation_rights(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        report = self.create_report(reporter=user_1, reported_object=user_2)
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
        self, app: Flask, user_1_moderator: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.patch(
            self.route.format(report_id=report.id),
            content_type="application/json",
            data='{}',
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_adds_a_comment(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        now = datetime.now(timezone.utc)
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
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        report_comment = ReportComment(
            comment=self.random_string(),
            report_id=report.id,
            user_id=user_1_moderator.id,
        )
        db.session.add(report_comment)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        now = datetime.now(timezone.utc)
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
            user_1_moderator.serialize(current_user=user_1_moderator)
        )
        assert data["report"]["updated_at"] == date_string
        assert len(data["report"]["comments"]) == 2
        assert data["report"]["comments"][1]["comment"] == comment

    def test_it_marks_a_report_as_unresolved(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        report.resolved = True
        report.resolved_at = datetime.now(timezone.utc)
        report.resolved_by = user_1_moderator.id
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        now = datetime.now(timezone.utc)
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
        self,
        app: Flask,
        user_1_moderator: User,
        user_2_admin: User,
        user_3: User,
    ) -> None:
        report = self.create_report(
            reporter=user_3, reported_object=user_2_admin
        )
        report.resolved = True
        resolved_time = datetime.now(timezone.utc)
        report.resolved_at = resolved_time
        report.resolved_by = user_2_admin.id
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        comment_time = datetime.now(timezone.utc)
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
            user_2_admin.serialize(current_user=user_1_moderator)
        )
        assert data["report"]["updated_at"] == self.get_date_string(
            date=comment_time
        )
        assert len(data["report"]["comments"]) == 1
        assert data["report"]["comments"][0]["comment"] == comment


class TestPostReportAction(ReportTestCase):
    route = "/api/reports/{report_id}/actions"

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

    def test_it_returns_403_if_user_has_no_moderation_rights(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        report = self.create_report(reporter=user_1, reported_object=user_2)
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
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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


class TestPostReportActionForUserAction(ReportTestCase):
    route = "/api/reports/{report_id}/actions"

    def test_it_returns_400_when_action_type_is_user_warning_lifting(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        """'user_warning_lifting' is created on appeal processing"""
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_warning_lifting",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid 'action_type'")

    def test_it_returns_400_when_username_is_missing_on_user_report_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={"action_type": "user_suspension"},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "'username' is missing")

    def test_it_returns_400_when_username_is_invalid_on_user_report_action(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        now = datetime.now(timezone.utc)

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
            User.query.filter_by(username=user_2.username).one().suspended_at
            == now
        )

    def test_it_returns_400_when_when_user_already_suspended(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        user_2.suspended_at = datetime.now(timezone.utc)
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

        self.assert_400(response, "user account already suspended")

    def test_it_returns_400_when_when_user_already_warned(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        self.create_report_action(
            user_1_moderator,
            user_2,
            action_type="user_warning",
            report_id=report.id,
        )
        db.session.commit()

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_warning",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "user already warned")

    def test_it_reactivates_user(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            User.query.filter_by(username=user_2.username).one().suspended_at
            is None
        )

    @pytest.mark.parametrize('input_action_type', USER_ACTION_TYPES)
    def test_it_creates_report_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        input_action_type: str,
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        if input_action_type == "user_unsuspension":
            user_2.suspended_at = datetime.now(timezone.utc)
            db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": input_action_type,
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        assert (
            ReportAction.query.filter_by(
                moderator_id=user_1_moderator.id,
                user_id=user_2.id,
                action_type=input_action_type,
            ).first()
            is not None
        )

    def test_it_returns_report(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        report_comment = ReportComment(
            comment=self.random_string(),
            report_id=report.id,
            user_id=user_1_moderator.id,
        )
        db.session.add(report_comment)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        updated_report = Report.query.filter_by(id=report.id).one()
        assert data["report"] == jsonify_dict(
            updated_report.serialize(user_1_moderator, full=True)
        )

    def test_it_does_not_enable_registration_on_user_suspension(
        self,
        app_with_3_users_max: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report = self.create_report(
            reporter=user_1_moderator, reported_object=user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_3_users_max, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        user_suspension_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        user_unsuspension_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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

    def test_it_sends_an_email_on_user_warning(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        user_warning_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={
                "action_type": "user_warning",
                "username": user_2.username,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        user_warning_email_mock.send.assert_called_once()

    def test_it_does_not_send_when_email_sending_is_disabled(
        self,
        app_wo_email_activation: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        user_suspension_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1_moderator.email
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


class TestPostReportActionForWorkoutAction(ReportTestCase):
    route = "/api/reports/{report_id}/actions"

    def test_it_returns_400_when_workout_id_is_missing_on_workout_report_action(  # noqa
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={"action_type": "workout_suspension"},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "'workout_id' is missing")

    def test_it_returns_400_when_workout_is_invalid_on_workout_report_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        now = datetime.now(timezone.utc)

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
            .one()
            .suspended_at
            == now
        )

    def test_it_returns_400_when_when_workout_already_suspended(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
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
            "workout already suspended",
        )

    def test_it_unsuspends_workout(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)

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
            .one()
            .suspended_at
            is None
        )

    def test_it_creates_report_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            ReportAction.query.filter_by(
                moderator_id=user_1_moderator.id, user_id=user_2.id
            ).first()
            is not None
        )

    def test_it_returns_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        updated_report = Report.query.filter_by(id=report.id).one()
        assert data["report"] == jsonify_dict(
            updated_report.serialize(user_1_moderator, full=True)
        )

    def test_it_sends_an_email_on_workout_suspension(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_suspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_unsuspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_suspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1_moderator.email
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


class TestPostReportActionForCommentAction(ReportTestCase):
    route = "/api/reports/{report_id}/actions"

    def test_it_returns_400_when_comment_id_is_missing_on_comment_report_action(  # noqa
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, VisibilityLevel.PUBLIC
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.post(
            self.route.format(report_id=report.id),
            content_type="application/json",
            json={"action_type": "comment_suspension"},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "'comment_id' is missing")

    def test_it_returns_400_when_comment_is_invalid_on_comment_report_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, VisibilityLevel.PUBLIC
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, VisibilityLevel.PUBLIC
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, VisibilityLevel.PUBLIC
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        now = datetime.now(timezone.utc)

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
        assert Comment.query.filter_by(id=comment.id).one().suspended_at == now

    def test_it_returns_400_when_when_comment_already_suspended(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, VisibilityLevel.PUBLIC
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        comment.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        now = datetime.now(timezone.utc)

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
            "comment already suspended",
        )

    def test_it_unsuspends_comment(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, VisibilityLevel.PUBLIC
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        comment.suspended_at = datetime.now(timezone.utc)

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
            Comment.query.filter_by(id=comment.id).one().suspended_at is None
        )

    def test_it_creates_report_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, VisibilityLevel.PUBLIC
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            ReportAction.query.filter_by(
                moderator_id=user_1_moderator.id, user_id=user_3.id
            ).first()
            is not None
        )

    def test_it_returns_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, VisibilityLevel.PUBLIC
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        now = datetime.now(timezone.utc)

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
        updated_report = Report.query.filter_by(id=report.id).one()
        assert data["report"] == jsonify_dict(
            updated_report.serialize(user_1_moderator, full=True)
        )

    def test_it_sends_an_email_on_comment_suspension(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        comment_suspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text=f"@{user_2.username}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=True,
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        comment_unsuspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text=f"@{user_2.username}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=True,
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        comment.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        comment_suspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text=f"@{user_2.username}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=True,
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1_moderator.email
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


class TestProcessReportActionAppeal(
    CommentMixin, ReportMixin, ApiTestCaseMixin
):
    route = '/api/appeals/{appeal_id}'

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

    def test_it_returns_403_when_user_has_no_moderation_rights(
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
        self, app: Flask, user_1_moderator: User
    ) -> None:
        appeal_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        input_data: Dict,
    ) -> None:
        suspension_action = self.create_report_user_action(
            user_1_moderator, user_2
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.patch(
            self.route.format(appeal_id=appeal.short_id),
            data=json.dumps(input_data),
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_400_when_user_already_unsuspended(
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        suspension_action = self.create_report_user_action(
            user_1_moderator, user_2
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        user_2.suspended_at = None
        db.session.commit()

        response = client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": True, "reason": "ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, "user account has already been reactivated")

    @pytest.mark.parametrize(
        "input_data",
        [
            {"approved": True, "reason": "ok"},
            {"approved": False, "reason": "not ok"},
        ],
    )
    def test_it_processes_user_suspension_appeal(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        input_data: Dict,
    ) -> None:
        suspension_action = self.create_report_user_action(
            user_1_moderator, user_2
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            "appeal": jsonify_dict(appeal.serialize(user_1_moderator)),
        }
        appeal = ReportActionAppeal.query.filter_by(id=appeal.id).one()
        assert appeal.approved is input_data["approved"]
        assert appeal.reason == input_data["reason"]

    def test_it_sends_an_email_when_appeal_on_user_suspension_is_approved(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_unsuspension_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(
            reporter=user_1_moderator, reported_object=user_2
        )
        suspension_action = self.create_report_user_action(
            user_1_moderator, user_2, report_id=report.id
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": True, "reason": "ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        user_unsuspension_email_mock.send.assert_called_once()

    def test_it_sends_an_email_when_appeal_on_user_suspension_is_rejected(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        appeal_rejected_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(
            reporter=user_1_moderator, reported_object=user_2
        )
        suspension_action = self.create_report_user_action(
            user_1_moderator, user_2, report_id=report.id
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": False, "reason": "not ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        appeal_rejected_email_mock.send.assert_called_once()

    @pytest.mark.parametrize(
        "input_data",
        [
            {"approved": True, "reason": "ok"},
            {"approved": False, "reason": "not ok"},
        ],
    )
    def test_it_processes_user_warning_appeal(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        input_data: Dict,
    ) -> None:
        report = self.create_report(
            reporter=user_1_moderator, reported_object=user_2
        )
        warning_action = self.create_report_user_action(
            user_1_moderator, user_2, "user_warning", report.id
        )
        appeal = self.create_action_appeal(warning_action.id, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            "appeal": jsonify_dict(appeal.serialize(user_1_moderator)),
        }
        appeal = ReportActionAppeal.query.filter_by(id=appeal.id).one()
        assert appeal.approved is input_data["approved"]
        assert appeal.reason == input_data["reason"]

    def test_it_sends_an_email_when_appeal_on_user_warning_is_approved(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_warning_lifting_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(
            reporter=user_1_moderator, reported_object=user_2
        )
        warning_action = self.create_report_user_action(
            user_1_moderator, user_2, "user_warning", report.id
        )
        appeal = self.create_action_appeal(warning_action.id, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": True, "reason": "ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        user_warning_lifting_email_mock.send.assert_called_once()

    def test_it_sends_an_email_when_appeal_on_user_warning_is_rejected(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        appeal_rejected_email_mock: MagicMock,
    ) -> None:
        report = self.create_report(
            reporter=user_1_moderator, reported_object=user_2
        )
        warning_action = self.create_report_user_action(
            user_1_moderator, user_2, "user_warning", report.id
        )
        appeal = self.create_action_appeal(warning_action.id, user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": False, "reason": "not ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        appeal_rejected_email_mock.send.assert_called_once()

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
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_data: Dict,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        suspension_action = self.create_report_comment_action(
            user_1_moderator, user_3, comment
        )
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_3)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
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
            "appeal": jsonify_dict(appeal.serialize(user_1_moderator)),
        }
        appeal = ReportActionAppeal.query.filter_by(id=appeal.id).one()
        assert appeal.approved is input_data["approved"]
        assert appeal.reason == input_data["reason"]

    def test_it_sends_an_email_when_appeal_on_comment_suspension_is_approved(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        comment_unsuspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        suspension_action = self.create_report_comment_action(
            user_1_moderator, user_3, comment
        )
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_3)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": True, "reason": "ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        comment_unsuspension_email_mock.send.assert_called_once()

    def test_it_sends_an_email_when_appeal_on_comment_suspension_is_rejected(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        appeal_rejected_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        suspension_action = self.create_report_comment_action(
            user_1_moderator, user_3, comment
        )
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_3)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": False, "reason": "not ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        appeal_rejected_email_mock.send.assert_called_once()

    def test_it_returns_400_when_comment_already_unsuspended(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        suspension_action = self.create_report_comment_action(
            user_1_moderator, user_3, comment
        )
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_3)
        db.session.flush()
        comment.suspended_at = None
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": True, "reason": "ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, "comment already reactivated")

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
        user_1_moderator: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_data: Dict,
    ) -> None:
        suspension_action = self.create_report_workout_action(
            user_1_moderator, user_2, workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )
        now = datetime.now(timezone.utc)

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
            "appeal": jsonify_dict(appeal.serialize(user_1_moderator)),
        }
        appeal = ReportActionAppeal.query.filter_by(id=appeal.id).one()
        assert appeal.approved is input_data["approved"]
        assert appeal.reason == input_data["reason"]

    def test_it_sends_an_email_when_appeal_on_workout_suspension_is_approved(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_unsuspension_email_mock: MagicMock,
    ) -> None:
        suspension_action = self.create_report_workout_action(
            user_1_moderator, user_2, workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": True, "reason": "ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        workout_unsuspension_email_mock.send.assert_called_once()

    def test_it_sends_an_email_when_appeal_on_workout_suspension_is_rejected(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        appeal_rejected_email_mock: MagicMock,
    ) -> None:
        suspension_action = self.create_report_workout_action(
            user_1_moderator, user_2, workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": False, "reason": "not ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        appeal_rejected_email_mock.send.assert_called_once()

    def test_it_returns_400_when_workout_already_unsuspended(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        suspension_action = self.create_report_workout_action(
            user_1_moderator, user_2, workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        db.session.commit()
        workout_cycling_user_2.suspended_at = None
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.patch(
            self.route.format(appeal_id=appeal.short_id),
            json={"approved": True, "reason": "ok"},
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, "workout already reactivated")

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "users:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_moderator: User,
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
            app, user_1_moderator, scope=client_scope
        )

        response = client.patch(
            self.route.format(appeal_id=appeal_id),
            data=json.dumps(dict(approved=False, reason="OK")),
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestGetReportsUnresolved(ReportTestCase):
    route = "/api/reports/unresolved"

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(self.route, content_type="application/json")

        self.assert_401(response)

    def test_it_returns_error_if_user_has_no_moderation_rights(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_false_when_no_reports(
        self, app: Flask, user_1_moderator: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["unresolved"] is False

    def test_it_returns_false_when_reports_are_resolved(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
    ) -> None:
        for reported_user in [user_2, user_3]:
            report = self.create_report(
                reporter=user_1_moderator, reported_object=reported_user
            )
            report.resolved = True
            db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["unresolved"] is False

    def test_it_returns_true_when_unresolved_reports_exist(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
    ) -> None:
        for reported_user in [user_2, user_3]:
            report = self.create_report(
                reporter=user_1_moderator, reported_object=reported_user
            )
            if reported_user.id == user_3.id:
                report.resolved = True
            db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_moderator.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["unresolved"] is True

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "reports:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_moderator: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_moderator, scope=client_scope
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)
