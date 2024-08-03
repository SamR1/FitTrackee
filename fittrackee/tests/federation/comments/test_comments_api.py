import json
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.comments.models import Comment, Mention
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from ...comments.mixins import CommentMixin
from ...comments.test_comments_api import GetWorkoutCommentsTestCase
from ...mixins import ApiTestCaseMixin, BaseTestMixin
from ...utils import jsonify_dict


@patch('fittrackee.federation.utils.user.update_remote_user')
@patch('fittrackee.comments.comments.send_to_remote_inbox')
class TestPostWorkoutComment(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    @pytest.mark.parametrize(
        'input_workout_visibility',
        [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_returns_404_when_user_can_not_access_workout(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        # user_1 does not follow remote_user
        remote_cycling_workout.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f"/api/workouts/{remote_cycling_workout.short_id}/comments",
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
            f"workout not found (id: {remote_cycling_workout.short_id})",
        )

    def test_it_returns_404_when_follower_can_not_access_workout(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        # user_1 follows remote_user but the workout is private
        remote_user.approves_follow_request_from(user_1)
        remote_cycling_workout.workout_visibility = PrivacyLevel.PRIVATE
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f"/api/workouts/{remote_cycling_workout.short_id}/comments",
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

        self.assert_404_with_message(
            response,
            f"workout not found (id: {remote_cycling_workout.short_id})",
        )

    def test_it_returns_201_when_comment_is_created(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        remote_cycling_workout.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment_text = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f"/api/workouts/{remote_cycling_workout.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=comment_text,
                    text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        new_comment = Comment.query.filter_by(
            user_id=user_1.id, workout_id=remote_cycling_workout.id
        ).first()
        assert data['comment'] == jsonify_dict(new_comment.serialize(user_1))
        assert new_comment.ap_id == (
            f'{user_1.actor.activitypub_id}/'
            f'workouts/{remote_cycling_workout.short_id}/'
            f'comments/{new_comment.short_id}'
        )
        assert new_comment.remote_url == (
            f'https://{user_1.actor.domain.name}/'
            f'workouts/{remote_cycling_workout.short_id}/'
            f'comments/{new_comment.short_id}'
        )
        assert new_comment.reply_to is None

    def test_it_returns_201_when_user_replies_to_a_remote_comment(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            remote_user,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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

    @pytest.mark.parametrize(
        'input_workout_visibility',
        [
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_does_not_call_sent_to_inbox_if_privacy_is_private_or_local_followers_only_and_no_mentions(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        follow_request_from_user_2_to_user_1: FollowRequest,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        user_1.approves_follow_request_from(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=input_workout_visibility,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        send_to_remote_inbox_mock.send.assert_not_called()

    def test_it_does_not_call_sent_to_inbox_if_user_has_no_remote_followers(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
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

        send_to_remote_inbox_mock.send.assert_not_called()

    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE]
    )
    def test_it_calls_sent_to_inbox_if_comment_has_mention(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        # remote_user is mentioned but does not follow user_1
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=f"@{remote_user.fullname} {self.random_string()}",
                    text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        note_activity = Comment.query.first().get_activity(
            activity_type='Create'
        )
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=note_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_calls_sent_to_inbox_if_user_has_follower_from_remote_fittrackee_instance(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        input_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
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

        note_activity = Comment.query.first().get_activity(
            activity_type='Create'
        )
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=note_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_calls_sent_to_inbox_if_user_has_follower_from_remote_other_instance(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        remote_user_2.send_follow_request_to(user_1)
        user_1.approves_follow_request_from(remote_user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
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

        note_activity = Comment.query.first().get_activity(
            activity_type='Create'
        )
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=note_activity,
            recipients=[remote_user_2.actor.shared_inbox_url],
        )

    def test_it_creates_mention(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        remote_user.send_follow_request_to(user_1)
        user_1.approves_follow_request_from(remote_user)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=f"@{remote_user.fullname}",
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
                comment_id=new_comment.id, user_id=remote_user.id
            ).first()
            is not None
        )


class TestGetWorkoutCommentAsUser(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_404_when_comment_visibility_does_not_allow_access(
        self,
        app_with_federation: Flask,
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
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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


class TestGetWorkoutCommentAsFollower(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app_with_federation: Flask,
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
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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


class TestGetWorkoutCommentAsRemoteFollower(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        user_1.send_follow_request_to(remote_user)
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


class TestGetWorkoutCommentAsOwner(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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
    def test_it_returns_404_when_comment_visibility_does_not_allow_access(
        self,
        app_with_federation: Flask,
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
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client = app_with_federation.test_client()

        response = client.get(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment.short_id})",
        )


class TestGetWorkoutCommentWithReplies(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_gets_reply(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        reply = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
            parent_comment=comment,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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


class TestGetWorkoutCommentsAsUser(GetWorkoutCommentsTestCase):
    def test_it_does_not_return_comment_when_for_followers_and_remote(
        self,
        app_with_federation: Flask,
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
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_comments_response(response, expected_comments=[])


class TestGetWorkoutCommentsAsFollower(GetWorkoutCommentsTestCase):
    def test_it_does_not_return_comment_when_visibility_does_not_allow_it(
        self,
        app_with_federation: Flask,
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
            app_with_federation, user_1.email
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
        'input_text_visibility',
        [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PUBLIC,
        ],
    )
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app_with_federation: Flask,
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
            app_with_federation, user_1.email
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


class TestGetWorkoutCommentsAsOwner(GetWorkoutCommentsTestCase):
    def test_it_returns_comment_when_for_followers_and_remote(
        self,
        app_with_federation: Flask,
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
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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


class TestGetWorkoutCommentsAsUnauthenticatedUser(GetWorkoutCommentsTestCase):
    def test_it_does_not_return_comment_when_for_followers_and_remote(
        self,
        app_with_federation: Flask,
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
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client = app_with_federation.test_client()

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
            content_type="application/json",
        )

        self.assert_comments_response(response, expected_comments=[])


class TestGetWorkoutComments(GetWorkoutCommentsTestCase):
    def test_it_returns_only_comments_user_can_access(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        remote_user: User,
        remote_user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        # remote user 2
        visible_comments = [
            self.create_comment(
                remote_user_2,
                workout_cycling_user_2,
                text_visibility=PrivacyLevel.PUBLIC,
            )
        ]

        for privacy_levels in [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ]:
            # user_1 is not mentioned
            self.create_comment(
                remote_user_2,
                workout_cycling_user_2,
                text_visibility=privacy_levels,
            )

        for privacy_levels in [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ]:
            # user_1 is mentioned
            visible_comments.append(
                self.create_comment(
                    remote_user_2,
                    workout_cycling_user_2,
                    text=f"@{user_1.username}",
                    text_visibility=privacy_levels,
                )
            )

        # remote user followed by user 1
        for privacy_levels in [
            PrivacyLevel.PUBLIC,
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
        ]:
            visible_comments.append(
                self.create_comment(
                    remote_user,
                    workout_cycling_user_2,
                    text_visibility=privacy_levels,
                )
            )
        self.create_comment(
            remote_user,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PRIVATE,
        )
        # user 3
        visible_comments.append(
            self.create_comment(
                user_3,
                workout_cycling_user_2,
                text_visibility=PrivacyLevel.PUBLIC,
            )
        )
        for privacy_levels in [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
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
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
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
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
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
            app_with_federation, user_1.email
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


class TestGetWorkoutCommentWithMention(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    @pytest.mark.parametrize(
        'input_workout_visibility',
        [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_user_can_access_comment_when_mentioned(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text=f"@{user_1.username} {self.random_string()}",
            text_visibility=input_workout_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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


class TestGetWorkoutsCommentsWithReplies(
    CommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_gets_reply(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        reply = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
            parent_comment=comment,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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
        assert data['data']['comments'][0]['id'] == comment.short_id
        assert data['data']['comments'][0]['replies'] == [
            jsonify_dict(reply.serialize(user_1))
        ]


@patch('fittrackee.federation.utils.user.update_remote_user')
@patch('fittrackee.comments.comments.send_to_remote_inbox')
class TestDeleteWorkoutComment(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    def test_it_returns_404_if_comment_is_not_visible_to_user(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {comment.short_id})",
        )

    def test_it_does_not_call_sent_to_inbox_if_privacy_is_local_followers_only(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_not_called()

    def test_it_does_not_call_sent_to_inbox_if_user_has_no_remote_followers(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_not_called()

    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE]
    )
    def test_it_calls_sent_to_inbox_if_comment_has_mention(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text=f"@{remote_user.fullname} {self.random_string()}",
            text_visibility=input_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )
        note_activity = comment.get_activity(activity_type='Delete')

        client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=note_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_calls_sent_to_inbox_if_user_has_follower_from_remote_fittrackee_instance(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        input_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        note_activity = comment.get_activity(activity_type='Delete')
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=note_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_calls_sent_to_inbox_if_user_has_follower_from_remote_other_instance(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        remote_user_2.send_follow_request_to(user_1)
        user_1.approves_follow_request_from(remote_user_2)
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        note_activity = comment.get_activity(activity_type='Delete')
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=note_activity,
            recipients=[remote_user_2.actor.shared_inbox_url],
        )

    def test_it_deletes_mentions(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        user_1.approves_follow_request_from(remote_user)
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text=f"@{remote_user.fullname}",
            text_visibility=PrivacyLevel.PUBLIC,
        )
        comment_id = comment.id
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.delete(
            f"/api/comments/{comment.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert Mention.query.filter_by(comment_id=comment_id).all() == []


@patch('fittrackee.federation.utils.user.update_remote_user')
@patch('fittrackee.comments.comments.send_to_remote_inbox')
class TestPatchWorkoutComment(CommentMixin, ApiTestCaseMixin, BaseTestMixin):
    def test_it_does_not_call_sent_to_inbox_when_comment_is_local_with_no_mentions(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        send_to_remote_inbox_mock.send.assert_not_called()

    @pytest.mark.parametrize(
        'input_visibility',
        [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_calls_sent_to_inbox_with_update_when_comment_has_mention(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text=f"@{remote_user.fullname} foo",
            text_visibility=input_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=f"@{remote_user.fullname} bar")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        update_comment_activity = comment.get_activity(activity_type='Update')
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=update_comment_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    @pytest.mark.parametrize(
        'input_visibility',
        [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_calls_sent_to_inbox_with_update_when_mention_is_removed(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text=f"@{remote_user.fullname} foo",
            text_visibility=input_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        update_comment_activity = comment.get_activity(activity_type='Update')
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=update_comment_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    @pytest.mark.parametrize(
        'text_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_calls_sent_to_inbox_if_user_has_follower_from_remote_instance(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        text_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=text_visibility,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        update_comment_activity = comment.get_activity(activity_type='Update')
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=update_comment_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    def test_it_updates_mentions_to_remove_mention(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        remote_user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        user_1.approves_follow_request_from(remote_user)
        remote_user_2.send_follow_request_to(user_1)
        user_1.approves_follow_request_from(remote_user_2)
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text=f"@{remote_user.fullname} @{remote_user_2.fullname}",
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(dict(text=f"@{remote_user.fullname}")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        new_comment = Comment.query.filter_by(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        ).first()
        mentions = Mention.query.filter_by(comment_id=new_comment.id).all()
        assert len(mentions) == 1
        assert mentions[0] == (
            Mention.query.filter_by(
                comment_id=new_comment.id, user_id=remote_user.id
            ).first()
        )

    def test_it_updates_mentions_to_add_mention(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        remote_user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        user_1.approves_follow_request_from(remote_user)
        remote_user_2.send_follow_request_to(user_1)
        user_1.approves_follow_request_from(remote_user_2)
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text=f"@{remote_user.fullname}",
            text_visibility=PrivacyLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.patch(
            f"/api/comments/{comment.short_id}",
            content_type="application/json",
            data=json.dumps(
                dict(text=f"@{remote_user.fullname} @{remote_user_2.fullname}")
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        new_comment = Comment.query.filter_by(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        ).first()
        mentions = Mention.query.filter_by(comment_id=new_comment.id).all()
        assert len(mentions) == 2
