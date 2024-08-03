import json
from datetime import datetime
from typing import Dict, List

import pytest
from flask import Flask
from time_machine import travel
from werkzeug import Response

from fittrackee import db
from fittrackee.administration.models import AdminActionAppeal
from fittrackee.comments.models import Comment, Mention
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin, BaseTestMixin
from ..utils import OAUTH_SCOPES, jsonify_dict
from .mixins import CommentMixin


class TestPostWorkoutComment(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client = app.test_client()

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
        )

        self.assert_401(response)

    def test_it_returns_400_when_text_is_missing(
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
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response)

    def test_it_returns_400_when_visibility_is_missing(
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
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_domain(),
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response)

    def test_it_returns_404_when_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        workout_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_short_id})",
        )

    @pytest.mark.parametrize(
        'input_workout_visibility',
        [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE],
    )
    def test_it_returns_404_when_user_can_not_access_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )

    def test_it_returns_404_when_blocked_user_comments_a_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        user_2.blocks_user(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.PUBLIC,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )

    def test_it_returns_400_when_comment_visibility_is_invalid(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(
            response,
            "invalid visibility: followers_and_remote_only, "
            "federation is disabled.",
        )

    def test_it_returns_500_when_data_is_invalid(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.FOLLOWERS
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=self.random_string(),
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_500(response, 'Error during comment save.', 'fail')
        assert Comment.query.all() == []

    def test_it_returns_201_when_comment_is_created(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment_text = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=comment_text,
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        new_comment = Comment.query.filter_by(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        ).first()
        assert data['comment'] == jsonify_dict(new_comment.serialize(user_1))

    def test_it_returns_403_when_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment_text = self.random_string()
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=comment_text,
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_sanitizes_text_before_storing_in_database(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment_text = "<script>alert('evil!')</script> Hello"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=comment_text,
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 201
        new_comment = Comment.query.filter_by(
            user_id=user_1.id, workout_id=workout_cycling_user_1.id
        ).first()
        assert new_comment.text == " Hello"

    def test_it_creates_mention(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=f"@{user_3.username}",
                    text_visibility=PrivacyLevel.PUBLIC,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        new_comment = Comment.query.filter_by(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        ).first()
        assert (
            Mention.query.filter_by(
                comment_id=new_comment.id, user_id=user_3.id
            ).first()
            is not None
        )

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        client_scope: str,
        can_access: bool,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                    workout_id=workout_cycling_user_2.short_id,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {access_token}",
            ),
        )

        self.assert_response_scope(response, can_access)


class TestPostWorkoutCommentReply(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    @pytest.mark.parametrize(
        'input_comment_visibility',
        [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE],
    )
    def test_it_returns_404_when_user_can_not_access_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_comment_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=input_comment_visibility,
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                    reply_to=comment.short_id,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response, "'reply_to' is invalid")

    def test_it_returns_404_when_user_blocked_by_workout_owner_replies(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2, workout_cycling_user_2, text_visibility=PrivacyLevel.PUBLIC
        )
        user_2.blocks_user(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.PUBLIC,
                    reply_to=comment.short_id,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )

    def test_it_returns_404_when_user_blocked_by_comment_author_replies(
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
            user_3, workout_cycling_user_2, text_visibility=PrivacyLevel.PUBLIC
        )
        user_3.blocks_user(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.PUBLIC,
                    reply_to=comment.short_id,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response, "'reply_to' is invalid")

    def test_it_returns_400_when_user_replies_to_not_existing_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.PUBLIC,
                    reply_to=self.random_short_id(),
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response, "'reply_to' is invalid")

    def test_it_returns_201_when_user_replies_to_a_comment(
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.PUBLIC,
                    reply_to=comment.short_id,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert data['comment']['reply_to'] == comment.short_id

    def test_it_returns_403_when_user_is_suspended(
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
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.PUBLIC,
                    reply_to=comment.short_id,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

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
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.PUBLIC,
                    reply_to=comment.short_id,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "'reply_to' is invalid")


class TestGetWorkoutCommentAsUser(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_404_when_workout_comment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_comment_short_id = self.random_short_id()
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{workout_comment_short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {workout_comment_short_id})",
        )

    @pytest.mark.parametrize(
        'input_text_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE]
    )
    def test_it_returns_404_when_comment_visibility_does_not_allow_access(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_text_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment.short_id})",
        )

    def test_it_returns_comment_when_visibility_is_public(
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
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(comment.serialize(user_1))

    def test_it_returns_404_when_comment_author_is_blocked(
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
            text_visibility=PrivacyLevel.PUBLIC,
        )
        user_1.blocks_user(user_3)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment.short_id})",
        )

    def test_it_returns_404_when_user_is_blocked(
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
            text_visibility=PrivacyLevel.PUBLIC,
        )
        user_3.blocks_user(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment.short_id})",
        )

    def test_it_returns_comment_when_workout_is_deleted(
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
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        db.session.delete(workout_cycling_user_2)
        db.session.commit()

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(comment.serialize(user_1))

    def test_it_returns_comment_when_workout_is_suspended(
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
            text_visibility=PrivacyLevel.PUBLIC,
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(comment.serialize(user_1))

    def test_it_returns_403_when_user_is_suspended(
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
            text_visibility=PrivacyLevel.PUBLIC,
        )
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_403(response)

    def test_it_returns_suspended_comment(
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
            text_visibility=PrivacyLevel.PUBLIC,
        )
        comment.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(comment.serialize())


class TestGetWorkoutCommentAsFollower(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_404_when_comment_visibility_does_not_allow_access(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        user_2.approves_follow_request_from(user_3)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.FOLLOWERS
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment.short_id})",
        )

    @pytest.mark.parametrize(
        'input_text_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC]
    )
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_text_visibility: PrivacyLevel,
    ) -> None:
        user_1.send_follow_request_to(user_3)
        user_3.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(comment.serialize(user_1))

    def test_it_returns_403_when_user_is_suspended(
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
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_403(response)

    def test_it_returns_404_when_comment_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        user_2.approves_follow_request_from(user_3)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.FOLLOWERS
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        comment.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment.short_id})",
        )


class TestGetWorkoutCommentAsOwner(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    @pytest.mark.parametrize(
        'input_text_visibility',
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC],
    )
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        input_text_visibility: PrivacyLevel,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(comment.serialize(user_1))

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_403(response)

    def test_it_returns_suspended_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        comment.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(comment.serialize(user_1))


class TestGetWorkoutCommentAsUnauthenticatedUser(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    @pytest.mark.parametrize(
        'input_text_visibility',
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS],
    )
    def test_it_returns_404_when_comment_visibility_does_not_allow_access(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        input_text_visibility: PrivacyLevel,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client = app.test_client()

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment.short_id})",
        )

    def test_it_returns_suspended_comment(
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
        db.session.commit()
        client = app.test_client()

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(comment.serialize())

    def test_it_returns_comment_when_visibility_is_public(
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
        client = app.test_client()

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(comment.serialize())

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:read': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        client_scope: str,
        can_access: bool,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {access_token}",
            ),
        )

        self.assert_response_scope(response, can_access)


class TestGetWorkoutCommentWithReplies(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_gets_comment_with_replies(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        reply = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
            parent_comment=comment,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment']['replies'] == [
            jsonify_dict(reply.serialize(user_1))
        ]

    def test_it_does_not_return_reply_from_blocked_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
            parent_comment=comment,
        )
        user_1.blocks_user(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment']['replies'] == []

    def test_it_does_not_return_reply_when_user_is_blocked(
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
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
            parent_comment=comment,
        )
        user_3.blocks_user(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment']['replies'] == []

    def test_it_returns_suspended_reply(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        reply = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
            parent_comment=comment,
        )
        reply.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment']['replies'] == [
            jsonify_dict(reply.serialize(user_1))
        ]

    def test_it_gets_comment_when_reply_is_not_visible(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        # not visible reply
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PRIVATE,
            parent_comment=comment,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment']['replies'] == []

    def test_it_gets_reply(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        reply = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
            parent_comment=comment,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/comments/{reply.short_id}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment']['reply_to'] == jsonify_dict(
            comment.serialize(user_1, with_replies=False)
        )
        assert data['comment']['replies'] == []

    def test_it_gets_reply_when_parent_is_not_visible_anymore(
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
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        reply = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
            parent_comment=comment,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        comment.text_visibility = PrivacyLevel.PRIVATE

        response = client.get(
            f"/api/comments/{reply.short_id}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment']['reply_to'] is None
        assert data['comment']['replies'] == []


class GetWorkoutCommentsTestCase(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    @staticmethod
    def assert_comments_response(
        response: Response, expected_comments: List
    ) -> None:
        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['comments'] == expected_comments


class TestGetWorkoutCommentsAsUser(GetWorkoutCommentsTestCase):
    def test_it_returns_404_when_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
    ) -> None:
        workout_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_short_id})",
        )

    def test_it_returns_empty_list_when_no_comments(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_comments_response(response, expected_comments=[])

    @pytest.mark.parametrize(
        'input_text_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE]
    )
    def test_it_does_not_return_comment_when_visibility_does_not_allow_it(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_text_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_comments_response(response, expected_comments=[])

    def test_it_returns_comment_when_visibility_is_public(
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
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_comments_response(
            response,
            expected_comments=[jsonify_dict(comment.serialize(user_1))],
        )

    def test_it_does_not_return_comment_when_author_is_blocked(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        user_1.blocks_user(user_3)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_comments_response(response, expected_comments=[])

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_403(response)

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:read': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        client_scope: str,
        can_access: bool,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {access_token}",
            ),
        )

        self.assert_response_scope(response, can_access)


class TestGetWorkoutCommentsAsFollower(GetWorkoutCommentsTestCase):
    def test_it_does_not_return_comment_when_visibility_does_not_allow_it(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        user_2.approves_follow_request_from(user_3)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.FOLLOWERS
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_comments_response(response, expected_comments=[])

    @pytest.mark.parametrize(
        'input_text_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC]
    )
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_text_visibility: PrivacyLevel,
    ) -> None:
        user_1.send_follow_request_to(user_3)
        user_3.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_comments_response(
            response,
            expected_comments=[jsonify_dict(comment.serialize(user_1))],
        )

    def test_it_returns_403_when_user_is_suspended(
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
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_403(response)


class TestGetWorkoutCommentsAsOwner(GetWorkoutCommentsTestCase):
    @pytest.mark.parametrize(
        'input_text_visibility',
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC],
    )
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        input_text_visibility: PrivacyLevel,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_comments_response(
            response,
            expected_comments=[jsonify_dict(comment.serialize(user_1))],
        )

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_403(response)


class TestGetWorkoutCommentsAsUnauthenticatedUser(GetWorkoutCommentsTestCase):
    @pytest.mark.parametrize(
        'input_text_visibility',
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS],
    )
    def test_it_does_not_return_comment_when_visibility_does_not_allow_it(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        input_text_visibility: PrivacyLevel,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client = app.test_client()

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
        )

        self.assert_comments_response(response, expected_comments=[])

    def test_it_returns_comment_when_visibility_is_public(
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
        client = app.test_client()

        response = client.get(
            f"/api/workouts/{workout_cycling_user_1.short_id}/comments",
            content_type="application/json",
        )

        self.assert_comments_response(
            response,
            expected_comments=[jsonify_dict(comment.serialize(user_1))],
        )


class TestGetWorkoutComments(GetWorkoutCommentsTestCase):
    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        for _ in range(7):
            self.create_comment(
                user_3,
                workout_cycling_user_2,
                text_visibility=PrivacyLevel.PUBLIC,
            )
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_403(response)

    def test_it_returns_all_comments(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        for _ in range(7):
            self.create_comment(
                user_3,
                workout_cycling_user_2,
                text_visibility=PrivacyLevel.PUBLIC,
            )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        data = json.loads(response.data.decode())
        assert len(data['data']['comments']) == 7

    def test_it_returns_only_comments_user_can_access(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        # user 3
        visible_comments = [
            self.create_comment(
                user_3,
                workout_cycling_user_2,
                text_visibility=PrivacyLevel.PUBLIC,
            )
        ]
        for privacy_levels in [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE]:
            self.create_comment(
                user_3,
                workout_cycling_user_2,
                text_visibility=privacy_levels,
            )
        for privacy_levels in [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE]:
            # user_1 is mentioned in private comment
            visible_comments.append(
                self.create_comment(
                    user_3,
                    workout_cycling_user_2,
                    text=f"@{user_1.username}",
                    text_visibility=privacy_levels,
                )
            )
        # user 2 followed by user 1
        for privacy_levels in [PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS]:
            visible_comments.append(
                self.create_comment(
                    user_2,
                    workout_cycling_user_2,
                    text_visibility=privacy_levels,
                )
            )
        self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        # user 1
        for privacy_levels in [
            PrivacyLevel.PUBLIC,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PUBLIC,
        ]:
            visible_comments.append(
                self.create_comment(
                    user_1,
                    workout_cycling_user_2,
                    text_visibility=privacy_levels,
                )
            )
        # user_4 blocks user_1
        self.create_comment(
            user_4,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        user_4.blocks_user(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['data']['comments'] == [
            jsonify_dict(comment.serialize(user_1))
            for comment in visible_comments
        ]


class TestGetWorkoutsCommentWithReplies(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_gets_replies_a_user_can_access(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        visible_replies = [
            # owned comment
            self.create_comment(
                user_1,
                workout_cycling_user_2,
                text_visibility=PrivacyLevel.PRIVATE,
                parent_comment=comment,
            ),
            # public reply
            self.create_comment(
                user_3,
                workout_cycling_user_2,
                text_visibility=PrivacyLevel.PUBLIC,
                parent_comment=comment,
            ),
            # reply from following user
            self.create_comment(
                user_2,
                workout_cycling_user_2,
                text_visibility=PrivacyLevel.FOLLOWERS,
                parent_comment=comment,
            ),
        ]
        # user_4 blocks user_1
        self.create_comment(
            user_4,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
            parent_comment=comment,
        )
        user_4.blocks_user(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['comments']) == 1
        assert data['data']['comments'][0]['id'] == comment.short_id
        assert data['data']['comments'][0]['replies'] == [
            jsonify_dict(reply.serialize(user_1)) for reply in visible_replies
        ]


class TestDeleteWorkoutComment(ApiTestCaseMixin, BaseTestMixin, CommentMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        client = app.test_client()

        response = client.delete(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
        )

        self.assert_401(response)

    def test_it_returns_404_if_comment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment_short_id = self.random_short_id()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/comments/{comment_short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment_short_id})",
        )

    @pytest.mark.parametrize(
        'input_visibility',
        [
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_returns_404_if_comment_is_not_visible_to_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=input_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment.short_id})",
        )

    def test_it_returns_403_if_user_is_not_comment_owner(
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_deletes_workout_comment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204
        assert Comment.query.first() is None

    def test_it_deletes_workout_comment_having_reply(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        reply = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
            parent_comment=comment,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204
        assert reply.reply_to is None

    def test_it_deletes_mentions(
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
            user_1,
            workout_cycling_user_2,
            text=f"@{user_3.username}",
            text_visibility=PrivacyLevel.PUBLIC,
        )
        comment_id = comment.id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert Mention.query.filter_by(comment_id=comment_id).all() == []

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
            text_visibility=PrivacyLevel.PRIVATE,
        )
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestPatchWorkoutComment(ApiTestCaseMixin, BaseTestMixin, CommentMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        client = app.test_client()

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
        )

        self.assert_401(response)

    def test_it_returns_404_if_comment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment_short_id = self.random_short_id()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/comments/{comment_short_id}",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment_short_id})",
        )

    @pytest.mark.parametrize(
        'input_visibility',
        [
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_returns_404_if_comment_is_not_visible_to_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=input_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment.short_id})",
        )

    def test_it_returns_403_if_user_is_not_comment_owner(
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_400_when_text_is_missing(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps({}),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_493_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_updates_workout_comment_text(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        updated_text = self.random_string()

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=updated_text)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        assert comment.text == updated_text
        assert comment.text_visibility == PrivacyLevel.PUBLIC
        assert comment.modification_date is not None

    def test_it_sanitizes_text_before_storing_in_database(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        updated_text = "<script>alert('evil!')</script> Hello"

        client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=updated_text)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert comment.text == " Hello"

    def test_it_updates_mentions_to_remove_mention(
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
            user_1,
            workout_cycling_user_2,
            text=f"@{user_3.username}",
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        new_comment = Comment.query.filter_by(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        ).first()
        assert Mention.query.filter_by(comment_id=new_comment.id).all() == []

    def test_it_updates_mentions_to_add_mention(
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
            user_1,
            workout_cycling_user_2,
            text=self.random_string(),
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=f"@{user_3.username}")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        new_comment = Comment.query.filter_by(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        ).first()
        assert (
            Mention.query.filter_by(
                comment_id=new_comment.id, user_id=user_3.id
            ).first()
            is not None
        )

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
            text_visibility=PrivacyLevel.PRIVATE,
        )
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestPostWorkoutCommentSuspensionAppeal(
    ApiTestCaseMixin, BaseTestMixin, CommentMixin
):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)
        client = app.test_client()

        response = client.post(
            f"/api/comments/{comment.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
        )

        self.assert_401(response)

    def test_it_returns_404_if_comment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        comment_short_id = self.random_short_id()
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/comments/{comment_short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment_short_id})",
        )

    def test_it_returns_403_if_user_is_not_comment_owner(
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/comments/{comment.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_400_if_comment_is_not_suspended(
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
            f"/api/comments/{comment.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response, error_message="workout comment is not suspended"
        )

    def test_it_returns_400_if_suspended_comment_has_no_admin_action(
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
        comment.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/comments/{comment.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response, error_message="workout comment has no suspension"
        )

    @pytest.mark.parametrize(
        'input_data', [{}, {"text": ""}, {"comment": "some text"}]
    )
    def test_it_returns_400_when_appeal_text_is_missing(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_data: Dict,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        comment.suspended_at = datetime.utcnow()
        self.create_admin_comment_suspension_action(
            user_2_admin, user_1, comment
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/comments/{comment.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(input_data),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, 'no text provided')

    def test_user_can_appeal_comment_suspension(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        comment.suspended_at = datetime.utcnow()
        action = self.create_admin_comment_suspension_action(
            user_2_admin, user_1, comment
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        text = self.random_string()
        now = datetime.utcnow()

        with travel(now, tick=False):
            response = client.post(
                f"/api/comments/{comment.short_id}/suspension/appeal",
                content_type='application/json',
                data=json.dumps(dict(text=text)),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 201
        assert response.json == {"status": "success"}
        appeal = AdminActionAppeal.query.filter_by(action_id=action.id).first()
        assert appeal.admin_user_id is None
        assert appeal.approved is None
        assert appeal.created_at == now
        assert appeal.user_id == user_1.id
        assert appeal.updated_at is None

    def test_user_can_appeal_comment_suspension_only_once(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        comment.suspended_at = datetime.utcnow()
        action = self.create_admin_comment_suspension_action(
            user_2_admin, user_1, comment
        )
        db.session.flush()
        appeal = AdminActionAppeal(
            action_id=action.id,
            user_id=user_1.id,
            text=self.random_string(),
        )
        db.session.add(appeal)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/comments/{comment.short_id}/suspension/appeal",
            content_type='application/json',
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, error_message='you can appeal only once')

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
            text_visibility=PrivacyLevel.PRIVATE,
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
            f"/api/comments/{comment.short_id}/suspension/appeal",
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)
