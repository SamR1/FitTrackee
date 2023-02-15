from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from ...workouts.utils import WorkoutCommentMixin


class TestCommentWithMentionSerializeVisibility(WorkoutCommentMixin):
    def test_public_comment_is_visible_to_all_users(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text=f"@{user_2.username} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
        )

        comment.serialize(user_1)  # author
        comment.serialize(user_2)  # mentioned user
        comment.serialize(user_3)  # user
        comment.serialize()  # unauthenticated user

    @pytest.mark.parametrize(
        'text_visibility',
        [PrivacyLevel.FOLLOWERS, PrivacyLevel.FOLLOWERS_AND_REMOTE],
    )
    @patch('fittrackee.federation.utils.user.update_remote_user')
    def test_comment_for_followers_is_visible_to_followers_and_mentioned_users(
        self,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
        text_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text=(
                f"@{user_3.username} {remote_user.fullname} "
                f"{self.random_string()}"
            ),
            text_visibility=text_visibility,
        )

        assert comment.serialize(user_1)  # author
        assert comment.serialize(user_2)  # follower
        assert comment.serialize(user_3)  # mentioned user
        with pytest.raises(CommentForbiddenException):
            assert comment.serialize(user_4)  # user
            assert comment.serialize()  # unauthenticated user

    def test_private_comment_is_only_visible_to_author_and_mentioned_user(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text=f"@{user_3.username} {self.random_string()}",
            text_visibility=PrivacyLevel.FOLLOWERS,
        )

        assert comment.serialize(user_1)  # author
        assert comment.serialize(user_3)  # mentioned user
        with pytest.raises(CommentForbiddenException):
            assert comment.serialize(user_2)  # follower
            assert comment.serialize(user_4)  # user
            assert comment.serialize()  # unauthenticated user

    @patch('fittrackee.federation.utils.user.update_remote_user')
    def test_private_comment_with_remote_mention_is_only_visible_to_author(
        self,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text=f"@{remote_user.fullname} {self.random_string()}",
            text_visibility=PrivacyLevel.PRIVATE,
        )

        assert comment.serialize(user_1)  # author
        with pytest.raises(CommentForbiddenException):
            assert comment.serialize(user_2)  # follower
            assert comment.serialize(user_3)  # user
            assert comment.serialize()  # unauthenticated user


class TestWorkoutCommentRemoteMentions(WorkoutCommentMixin):
    def test_it_gets_remote_followers_count(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=(
                f"@{user_3.username} {self.random_string()} "
                f"@{remote_user.fullname}"
            ),
            text_visibility=PrivacyLevel.PUBLIC,
        )

        assert comment.remote_mentions.count() == 1

    def test_has_remote_mentions_returns_false_when_no_remote_mentions(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"@{user_3.username} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
        )

        assert comment.has_remote_mentions is False

    def test_has_remote_mentions_returns_true_when_remote_mentions(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"@{remote_user.fullname} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
        )

        assert comment.has_remote_mentions is True
