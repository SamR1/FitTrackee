import json
from unittest.mock import Mock, patch

from flask import Flask

from fittrackee import db
from fittrackee.comments.models import CommentLike
from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ...comments.mixins import CommentMixin
from ...mixins import ApiTestCaseMixin, BaseTestMixin


@patch("fittrackee.federation.utils.user.update_remote_user")
@patch("fittrackee.comments.comments.send_to_remote_inbox")
class TestCommentLikePost(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    route = "/api/comments/{comment_uuid}/like"

    def test_it_creates_workout_like(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            remote_user,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.FOLLOWERS_AND_REMOTE,
            with_federation=True,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["comment"]["id"] == comment.short_id
        assert (
            CommentLike.query.filter_by(
                user_id=user_1.id, comment_id=comment.id
            ).first()
            is not None
        )
        assert comment.likes.all() == [user_1]

    def test_it_does_not_call_sent_to_inbox_if_comment_is_local(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
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
            with_federation=True,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        send_to_remote_inbox_mock.send.assert_not_called()

    def test_it_calls_sent_to_inbox_if_comment_is_remote(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            remote_user,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            with_federation=True,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        like_activity = CommentLike.query.one().get_activity()
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=like_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )


@patch("fittrackee.federation.utils.user.update_remote_user")
@patch("fittrackee.comments.comments.send_to_remote_inbox")
class TestCommentUndoLikePost(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    route = "/api/comments/{comment_uuid}/like/undo"

    def test_it_removes_comment_like(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )
        comment = self.create_comment(
            remote_user,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.FOLLOWERS_AND_REMOTE,
            with_federation=True,
        )
        like = CommentLike(user_id=user_1.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["comment"]["id"] == comment.short_id
        assert (
            CommentLike.query.filter_by(
                user_id=user_1.id, comment_id=comment.id
            ).first()
            is None
        )
        assert workout_cycling_user_2.likes.all() == []

    def test_it_does_not_call_sent_to_inbox_if_comment_is_local(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
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
            with_federation=True,
        )
        like = CommentLike(user_id=user_1.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        send_to_remote_inbox_mock.send.assert_not_called()

    def test_it_calls_sent_to_inbox_if_like_is_remote(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            remote_user,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            with_federation=True,
        )
        like = CommentLike(user_id=user_1.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )
        undo_activity = CommentLike.query.one().get_activity(is_undo=True)

        client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=undo_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )
