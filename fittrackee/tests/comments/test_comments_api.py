import json
from typing import List

import pytest
from flask import Flask
from werkzeug import Response

from fittrackee.comments.models import Mention, WorkoutComment
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin, BaseTestMixin
from ..utils import jsonify_dict
from ..workouts.utils import WorkoutCommentMixin


class TestPostWorkoutComment(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
):
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
        workout_cycling_user_2.workout_visibility = PrivacyLevel.FOLLOWERS
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
        assert WorkoutComment.query.all() == []

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
        new_comment = WorkoutComment.query.filter_by(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        ).first()
        assert data['comment'] == jsonify_dict(new_comment.serialize(user_1))

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
        new_comment = WorkoutComment.query.filter_by(
            user_id=user_1.id, workout_id=workout_cycling_user_1.id
        ).first()
        assert new_comment.text == " Hello"

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
        workout_comment = self.create_comment(
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
                    reply_to=workout_comment.short_id,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert data['comment']['reply_to'] == workout_comment.short_id

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

        new_comment = WorkoutComment.query.filter_by(
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
        [
            ('application:write', False),
            ('follow:read', False),
            ('follow:write', False),
            ('profile:read', False),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', False),
            ('workouts:write', True),
        ],
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


class TestGetWorkoutCommentAsUser(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
):
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
            f"/api/workouts/{workout_short_id}/"
            f"comments/{self.random_short_id()}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_short_id})",
        )

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
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment_short_id}",
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
        workout_comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {workout_comment.short_id})",
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
        workout_comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(
            workout_comment.serialize(user_1)
        )


class TestGetWorkoutCommentAsFollower(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
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
        workout_comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {workout_comment.short_id})",
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
        workout_comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(
            workout_comment.serialize(user_1)
        )


class TestGetWorkoutCommentAsOwner(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
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
        workout_comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(
            workout_comment.serialize(user_1)
        )


class TestGetWorkoutCommentAsUnauthenticatedUser(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
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
        workout_comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )
        client = app.test_client()

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {workout_comment.short_id})",
        )

    def test_it_returns_comment_when_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client = app.test_client()

        response = client.get(
            f"/api/workouts/{workout_cycling_user_1.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(workout_comment.serialize())

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', False),
            ('follow:read', False),
            ('follow:write', False),
            ('profile:read', False),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', True),
            ('workouts:write', False),
        ],
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
        workout_comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {access_token}",
            ),
        )

        self.assert_response_scope(response, can_access)


class TestGetWorkoutCommentWithReplies(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_gets_reply(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        reply = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
            parent_comment=workout_comment,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_1.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment']['replies'] == [
            jsonify_dict(reply.serialize(user_1))
        ]


class GetWorkoutCommentsTestCase(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
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
        workout_comment = self.create_comment(
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
            expected_comments=[
                jsonify_dict(workout_comment.serialize(user_1))
            ],
        )

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', False),
            ('follow:read', False),
            ('follow:write', False),
            ('profile:read', False),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', True),
            ('workouts:write', False),
        ],
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
        workout_comment = self.create_comment(
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
            expected_comments=[
                jsonify_dict(workout_comment.serialize(user_1))
            ],
        )


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
        workout_comment = self.create_comment(
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
            expected_comments=[
                jsonify_dict(workout_comment.serialize(user_1))
            ],
        )


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
        workout_comment = self.create_comment(
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
            expected_comments=[
                jsonify_dict(workout_comment.serialize(user_1))
            ],
        )


class TestGetWorkoutComments(GetWorkoutCommentsTestCase):
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
        for privacy_levels in [
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ]:
            self.create_comment(
                user_3,
                workout_cycling_user_2,
                text_visibility=privacy_levels,
            )
        # user 2 followed by user 1
        for privacy_levels in [
            PrivacyLevel.PUBLIC,
            PrivacyLevel.FOLLOWERS,
        ]:
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
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_gets_reply(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        reply = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
            parent_comment=workout_comment,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_1.short_id}/comments",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['comments']) == 1
        assert data['data']['comments'][0]['id'] == workout_comment.short_id
        assert data['data']['comments'][0]['replies'] == [
            jsonify_dict(reply.serialize(user_1))
        ]


class TestDeleteWorkoutComment(
    ApiTestCaseMixin, BaseTestMixin, WorkoutCommentMixin
):
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
            content_type="application/json",
        )

        self.assert_401(response)

    def test_it_returns_404_if_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        workout_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/workouts/{workout_short_id}"
            f"/comments/{self.random_short_id()}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_short_id})",
        )

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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment_short_id}",
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204
        assert WorkoutComment.query.first() is None

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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
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
            f"/api/workouts/{workout_cycling_user_2.short_id}"
            f"/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert Mention.query.filter_by(comment_id=comment_id).all() == []

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', False),
            ('follow:read', False),
            ('follow:write', False),
            ('profile:read', False),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', False),
            ('workouts:write', True),
        ],
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestPatchWorkoutComment(
    ApiTestCaseMixin, BaseTestMixin, WorkoutCommentMixin
):
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
        )

        self.assert_401(response)

    def test_it_returns_404_if_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        workout_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_short_id}"
            f"/comments/{self.random_short_id()}",
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
            f"workout not found (id: {workout_short_id})",
        )

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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment_short_id}",
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps({}),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
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
            f"/api/workouts/{workout_cycling_user_2.short_id}"
            f"/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        new_comment = WorkoutComment.query.filter_by(
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
            f"/api/workouts/{workout_cycling_user_2.short_id}"
            f"/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=f"@{user_3.username}")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        new_comment = WorkoutComment.query.filter_by(
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
        [
            ('application:write', False),
            ('follow:read', False),
            ('follow:write', False),
            ('profile:read', False),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', False),
            ('workouts:write', True),
        ],
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
            f"/api/workouts/{workout_cycling_user_1.short_id}"
            f"/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)
