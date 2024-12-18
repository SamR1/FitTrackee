import json
from datetime import datetime
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.comments.models import CommentLike
from fittrackee.users.models import FollowRequest, Notification, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout, WorkoutLike

from ..comments.mixins import CommentMixin
from ..mixins import ApiTestCaseMixin, ReportMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


class TestUserNotifications(CommentMixin, ReportMixin, ApiTestCaseMixin):
    route = "/api/notifications"

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(self.route, content_type="application/json")

        self.assert_401(response)

    def test_it_returns_error_if_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_empty_list_when_no_notifications(
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

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_notifications_by_default_ordered_by_descending_creation_date(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_3_notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        follow_request_from_user_3_notification.marked_as_read = True
        db.session.commit()
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
        follow_request_from_user_2_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        assert data["status"] == "success"
        assert data["notifications"] == [
            jsonify_dict(follow_request_from_user_3_notification.serialize()),
            jsonify_dict(follow_request_from_user_2_notification.serialize()),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_returns_only_unread_notifications(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_3_notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        follow_request_from_user_3_notification.marked_as_read = True
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?status=unread",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        follow_request_from_user_2_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        assert data["status"] == "success"
        assert data["notifications"] == [
            jsonify_dict(follow_request_from_user_2_notification.serialize()),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_returns_only_read_notifications(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_3_notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        follow_request_from_user_3_notification.marked_as_read = True
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?status=read",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["notifications"] == [
            jsonify_dict(follow_request_from_user_3_notification.serialize()),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    @patch("fittrackee.users.notifications.DEFAULT_NOTIFICATION_PER_PAGE", 2)
    def test_it_returns_given_page(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?page=2",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        follow_request_from_user_2_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        assert data["notifications"] == [
            jsonify_dict(follow_request_from_user_2_notification.serialize()),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 3,
        }

    @patch("fittrackee.users.notifications.DEFAULT_NOTIFICATION_PER_PAGE", 2)
    def test_it_returns_notifications_in_given_order_page(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?order=asc",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        follow_request_from_user_2_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        follow_request_from_user_3_notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        assert data["notifications"] == [
            jsonify_dict(follow_request_from_user_2_notification.serialize()),
            jsonify_dict(follow_request_from_user_3_notification.serialize()),
        ]
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 3,
        }

    def test_it_returns_notifications_for_a_given_type(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        user_1.approves_follow_request_from(user_3)
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?type=follow_request",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        follow_request_from_user_2_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        assert data["notifications"] == [
            jsonify_dict(follow_request_from_user_2_notification.serialize()),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_does_not_return_workout_like_notification_from_blocked_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()
        user_1.blocks_user(user_2)
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_comment_like_notification_from_blocked_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        like = CommentLike(user_id=user_2.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()
        user_1.blocks_user(user_2)
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_comment_notification_from_blocked_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        user_1.blocks_user(user_2)
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_mention_notification_from_blocked_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_1.username}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=True,
        )
        user_1.blocks_user(user_2)
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_workout_like_notification_when_author_blocks_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()
        user_2.blocks_user(user_1)
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
        like_from_user_2_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
            event_type="workout_like",
        ).first()
        assert data["notifications"] == [
            jsonify_dict(like_from_user_2_notification.serialize()),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_returns_comment_like_notification_when_author_blocks_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        like = CommentLike(user_id=user_2.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()
        user_2.blocks_user(user_1)
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
        like_from_user_2_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
            event_type="comment_like",
        ).first()
        assert data["notifications"] == [
            jsonify_dict(like_from_user_2_notification.serialize()),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_does_not_return_comment_notification_when_author_blocks_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        user_2.blocks_user(user_1)
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_mention_notification_when_author_blocks_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_1.username}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=True,
        )
        user_2.blocks_user(user_1)
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_follow_request_from_suspended_user(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_accepted_follow_from_suspended_user(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_workout_like_notification_from_suspended_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_comment_like_notification_from_suspended_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        like = CommentLike(user_id=user_2.id, comment_id=comment.id)
        db.session.add(like)
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_comment_notification_from_suspended_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_mention_notification_from_suspended_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_1.username}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=True,
        )
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_does_not_return_comment_notification_when_user_does_not_follow_author_anymore(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        # comment without mention
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        user_1.unfollows(user_2)
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
        assert data["notifications"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_report_notification(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        self.create_user_report(user_2, user_3)
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
        report_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1_admin.id,
            event_type="report",
        ).first()
        assert data["notifications"] == [
            jsonify_dict(report_notification.serialize())
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_returns_report_notification_from_suspended_user(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        self.create_user_report(user_2, user_3)
        user_2.suspended_at = datetime.utcnow()
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
        report_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1_admin.id,
            event_type="report",
        ).first()
        assert data["notifications"] == [
            jsonify_dict(report_notification.serialize())
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_returns_suspension_appeal_notification(
        self,
        app: Flask,
        user_1_admin: User,
        user_2_admin: User,
        user_3: User,
    ) -> None:
        report_action = self.create_report_user_action(user_2_admin, user_3)
        self.create_action_appeal(report_action.id, user_3)
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
        appeal_notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=user_1_admin.id,
            event_type="suspension_appeal",
        ).first()
        assert (
            jsonify_dict(appeal_notification.serialize())
            in data["notifications"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'notifications:read': True}.items(),
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
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestUserNotificationPatch(ApiTestCaseMixin):
    route = "/api/notifications/{notification_id}"

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.patch(
            self.route.format(notification_id=self.random_short_id()),
            content_type="application/json",
            data=json.dumps(dict(read_status=True)),
        )

        self.assert_401(response)

    def test_it_returns_error_if_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.patch(
            self.route.format(notification_id=self.random_short_id()),
            content_type="application/json",
            data=json.dumps(dict(read_status=True)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_404_if_notification_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        notification_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(notification_id=notification_id),
            content_type="application/json",
            data=json.dumps(dict(read_status=True)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, f"notification not found (id: {notification_id})"
        )

    def test_it_returns_404_if_auth_user_is_not_notification_recipient(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        notification = Notification.query.first()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(notification_id=notification.short_id),
            content_type="application/json",
            data=json.dumps(dict(read_status=True)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, f"notification not found (id: {notification.short_id})"
        )

    @pytest.mark.parametrize('input_read_status', [True, False])
    def test_it_updates_notification_status(
        self,
        app: Flask,
        user_1: User,
        user_3: User,
        follow_request_from_user_3_to_user_1: FollowRequest,
        input_read_status: bool,
    ) -> None:
        notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        if not input_read_status:
            notification.marked_as_read = True
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(notification_id=notification.short_id),
            content_type="application/json",
            data=json.dumps(dict(read_status=input_read_status)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["notification"] == jsonify_dict(notification.serialize())
        assert notification.marked_as_read is input_read_status

    def test_it_return_error_when_read_status_is_invalid(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(notification_id=notification.short_id),
            content_type="application/json",
            data=json.dumps(dict(read_status=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response)

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'notifications:write': True}.items(),
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

        response = client.patch(
            self.route.format(notification_id=self.random_short_id()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestUserNotificationsStatus(CommentMixin, ReportMixin, ApiTestCaseMixin):
    route = "/api/notifications/unread"

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(self.route, content_type="application/json")

        self.assert_401(response)

    def test_it_returns_error_if_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_unread_as_false_when_no_notifications(
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

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["unread"] is False

    def test_it_returns_unread_as_true_when_user_has_unread_notifications(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
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
        assert data["unread"] is True

    def test_it_returns_unread_as_true_when_user_has_unread_report_notification(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        self.create_user_report(user_2, user_3)
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
        assert data["unread"] is True

    def test_it_returns_unread_as_true_when_user_has_unread_suspension_notification(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2_admin: User,
        user_3: User,
    ) -> None:
        report_action = self.create_report_user_action(user_2_admin, user_3)
        Notification.query.update({Notification.marked_as_read: True})
        db.session.commit()
        self.create_action_appeal(report_action.id, user_3)
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
        assert data["unread"] is True

    def test_it_returns_unread_as_false_when_all_notifications_has_been_read(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        notification = Notification.query.first()
        notification.marked_as_read = True
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
        assert data["unread"] is False

    def test_it_returns_unread_as_false_when_notification_is_from_blocked_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()
        user_1.blocks_user(user_2)

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
        assert data["unread"] is False

    def test_it_returns_unread_as_false_when_notification_is_from_suspended_user(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.flush()
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()

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
        assert data["unread"] is False

    def test_it_returns_unread_as_false_when_when_author_blocks_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        user_2.blocks_user(user_1)

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
        assert data["unread"] is False

    def test_it_returns_unread_as_false_when_user_does_not_follow_comment_author_anymore(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        # comment without mention
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        user_1.unfollows(user_2)
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
        assert data["unread"] is False

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'notifications:read': True}.items(),
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
            self.route,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestUserNotificationsMarkAllAsRead(ApiTestCaseMixin):
    route = "/api/notifications/mark-all-as-read"

    @staticmethod
    def assert_follow_notification_status(
        follow_request: FollowRequest, status: bool
    ) -> None:
        follow_request_notification = Notification.query.filter_by(
            from_user_id=follow_request.follower_user_id,
            to_user_id=follow_request.followed_user_id,
            event_type="follow_request",
        ).first()
        assert follow_request_notification.marked_as_read is status

    @staticmethod
    def assert_workout_like_notification_status(
        like: WorkoutLike, status: bool
    ) -> None:
        like_notification = Notification.query.filter_by(
            from_user_id=like.user_id,
            to_user_id=like.workout.user_id,
            event_type="workout_like",
        ).first()
        assert like_notification.marked_as_read is status

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.post(self.route, content_type="application/json")

        self.assert_401(response)

    def test_it_returns_error_if_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        self.assert_403(response)

    def test_it_does_not_return_error_when_no_notifications(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"

    def test_it_marks_all_user_notifications_as_read(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        follow_request_from_user_3_notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=user_1.id,
            event_type="follow_request",
        ).first()
        follow_request_from_user_3_notification.marked_as_read = True
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        self.assert_follow_notification_status(
            follow_request_from_user_2_to_user_1, status=True
        )
        self.assert_follow_notification_status(
            follow_request_from_user_1_to_user_2, status=False
        )
        self.assert_follow_notification_status(
            follow_request_from_user_3_to_user_1, status=True
        )
        self.assert_workout_like_notification_status(like, status=True)

    def test_it_marks_as_read_only_user_notifications_matching_provided_type(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(dict(type="workout_like")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        self.assert_follow_notification_status(
            follow_request_from_user_2_to_user_1, status=False
        )
        self.assert_workout_like_notification_status(like, status=True)

    @pytest.mark.parametrize('input_type', ['invalid_type', ''])
    def test_it_does_not_mark_as_read_when_provided_type_is_invalid(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
        input_type: str,
    ) -> None:
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            content_type="application/json",
            data=json.dumps(dict(type=input_type)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        self.assert_follow_notification_status(
            follow_request_from_user_2_to_user_1, status=False
        )
        self.assert_workout_like_notification_status(like, status=False)

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'notifications:write': True}.items(),
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

        response = client.post(
            self.route,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestUserNotificationTypes(CommentMixin, ReportMixin, ApiTestCaseMixin):
    route = "/api/notifications/types"

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(self.route, content_type="application/json")

        self.assert_401(response)

    def test_it_returns_error_if_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_empty_list_when_no_notifications(
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

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["notification_types"] == []

    @pytest.mark.parametrize('input_params', ['', '?status=all'])
    def test_it_returns_all_users_notifications_types(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_params: str,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_1.username}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=True,
        )
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        like_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
            event_type="workout_like",
        ).first()
        like_notification.marked_as_read = True
        db.session.commit()

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}{input_params}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert set(data["notification_types"]) == {
            "workout_comment",
            "workout_like",
        }

    def test_it_returns_only_unread_notifications(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_1.username}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=True,
        )
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        like_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
            event_type="workout_like",
        ).first()
        like_notification.marked_as_read = True
        db.session.commit()

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?status=unread",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["notification_types"] == [
            "workout_comment",
        ]

    def test_it_returns_only_read_notifications(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_1.username}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=True,
        )
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        like_notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
            event_type="workout_like",
        ).first()
        like_notification.marked_as_read = True
        db.session.commit()

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?status=read",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["notification_types"] == [
            "workout_like",
        ]
