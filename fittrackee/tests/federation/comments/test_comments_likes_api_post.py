import json

from flask import Flask

from fittrackee import db
from fittrackee.comments.models import CommentLike
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from ...comments.utils import CommentMixin
from ...mixins import ApiTestCaseMixin, BaseTestMixin


class TestCommentLikePost(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    route = '/api/workouts/{workout_uuid}/comments/{comment_uuid}/like'

    def test_it_creates_workout_like(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            remote_user,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            self.route.format(
                workout_uuid=workout_cycling_user_2.short_id,
                comment_uuid=comment.short_id,
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['comment']['id'] == comment.short_id
        assert (
            CommentLike.query.filter_by(
                user_id=user_1.id, comment_id=comment.id
            ).first()
            is not None
        )
        assert comment.likes.all() == [user_1]


class TestCommentUndoLikePost(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    route = '/api/workouts/{workout_uuid}/comments/{comment_uuid}/like/undo'

    def test_it_removes_comment_like(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )
        comment = self.create_comment(
            remote_user,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        like = CommentLike(user_id=user_1.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()

        response = client.post(
            self.route.format(
                workout_uuid=workout_cycling_user_2.short_id,
                comment_uuid=comment.short_id,
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['comment']['id'] == comment.short_id
        assert (
            CommentLike.query.filter_by(
                user_id=user_1.id, comment_id=comment.id
            ).first()
            is None
        )
        assert workout_cycling_user_2.likes.all() == []
