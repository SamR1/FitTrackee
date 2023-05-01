import json
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.users.models import FollowRequest, Notification, User
from fittrackee.workouts.models import Sport, Workout, WorkoutLike

from ..mixins import ApiTestCaseMixin
from ..utils import jsonify_dict


class TestUserNotifications(ApiTestCaseMixin):
    route = "/api/notifications"

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(self.route, content_type="application/json")

        self.assert_401(response)

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
            f"{self.route}?read_status=false",
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
            f"{self.route}?read_status=true",
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

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', False),
            ('follow:read', False),
            ('follow:write', False),
            ('notifications:read', True),
            ('notifications:write', False),
            ('profile:read', False),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', False),
            ('workouts:write', False),
        ],
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
            self.route.format(notification_id=self.random_int()),
            content_type="application/json",
            data=json.dumps(dict(read_status=True)),
        )

        self.assert_401(response)

    def test_it_returns_404_if_notification_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        notification_id = self.random_int()
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
            self.route.format(notification_id=notification.id),
            content_type="application/json",
            data=json.dumps(dict(read_status=True)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, f"notification not found (id: {notification.id})"
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
            self.route.format(notification_id=notification.id),
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
            self.route.format(notification_id=notification.id),
            content_type="application/json",
            data=json.dumps(dict(read_status=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response)

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', False),
            ('follow:read', False),
            ('follow:write', False),
            ('notifications:read', False),
            ('notifications:write', True),
            ('profile:read', False),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', False),
            ('workouts:write', False),
        ],
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
            self.route.format(notification_id=self.random_int()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestUserNotificationsStatus(ApiTestCaseMixin):
    route = "/api/notifications/unread"

    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(self.route, content_type="application/json")

        self.assert_401(response)

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

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', False),
            ('follow:read', False),
            ('follow:write', False),
            ('notifications:read', True),
            ('notifications:write', False),
            ('profile:read', False),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', False),
            ('workouts:write', False),
        ],
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
