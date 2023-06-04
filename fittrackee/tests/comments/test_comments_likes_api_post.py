import json

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.comments.models import CommentLike
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin, BaseTestMixin
from ..utils import OAUTH_SCOPES
from .utils import CommentMixin


class TestCommentLikePost(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    route = '/api/comments/{comment_uuid}/like'

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client = app.test_client()
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )

        response = client.post(
            self.route.format(comment_uuid=comment.short_id)
        )

        self.assert_401(response)

    def test_it_returns_404_when_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(comment_uuid=self.random_short_id()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    def test_it_returns_404_when_comment_does_not_exist(
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

        response = client.post(
            self.route.format(comment_uuid=self.random_short_id()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    def test_it_returns_404_when_comment_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        user_2.approves_follow_request_from(user_1)
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    def test_it_returns_404_when_user_is_not_follower(
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
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    @pytest.mark.parametrize(
        'input_desc,input_workout_level',
        [
            ('workout visibility: follower', PrivacyLevel.FOLLOWERS),
            ('workout visibility: public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_creates_workout_like(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_desc: str,
        input_workout_level: PrivacyLevel,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_1.send_follow_request_to(user_3)
        user_3.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
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

    def test_it_does_not_return_error_when_like_already_exists(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        user_1.send_follow_request_to(user_3)
        user_3.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        like = CommentLike(user_id=user_1.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
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

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        client_scope: str,
        can_access: bool,
    ) -> None:
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestCommentUndoLikePost(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    route = '/api/comments/{comment_uuid}/like/undo'

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        client = app.test_client()

        response = client.post(
            self.route.format(comment_uuid=comment.short_id)
        )

        self.assert_401(response)

    def test_it_returns_404_when_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(
                workout_uuid=self.random_short_id(),
                comment_uuid=self.random_short_id(),
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    def test_it_returns_404_when_comment_does_not_exist(
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

        response = client.post(
            self.route.format(comment_uuid=self.random_short_id()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    def test_it_returns_404_when_comment_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        user_2.approves_follow_request_from(user_1)
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    def test_it_returns_404_when_user_is_not_follower(
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
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    @pytest.mark.parametrize(
        'input_desc,input_workout_level',
        [
            ('workout visibility: follower', PrivacyLevel.FOLLOWERS),
            ('workout visibility: public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_removes_comment_like(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_desc: str,
        input_workout_level: PrivacyLevel,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_1.send_follow_request_to(user_3)
        user_3.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        like = CommentLike(user_id=user_1.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
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

    def test_it_does_not_return_error_when_no_existing_like(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_1.send_follow_request_to(user_3)
        user_3.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
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
        assert comment.likes.all() == []

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        client_scope: str,
        can_access: bool,
    ) -> None:
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            self.route.format(comment_uuid=comment.short_id),
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)
