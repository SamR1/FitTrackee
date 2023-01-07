import pytest
from flask import Flask

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.tests.workouts.test_workouts_comments_models import (
    WorkoutCommentModelTestCase,
)
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.exceptions import CommentForbiddenException
from fittrackee.workouts.models import Sport, Workout, WorkoutComment

from ...mixins import RandomMixin


class TestWorkoutCommentModel(RandomMixin):
    @pytest.mark.parametrize(
        'input_workout_visibility, input_text_visibility',
        [
            (PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.FOLLOWERS),
            (
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
            ),
            (PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS_AND_REMOTE),
        ],
    )
    def test_it_initializes_text_visibility_when_workout_visibility_is_not_stricter(  # noqa
        self,
        input_workout_visibility: PrivacyLevel,
        input_text_visibility: PrivacyLevel,
        app_with_federation: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        comment = WorkoutComment(
            user_id=user_1.id,
            workout_id=workout_cycling_user_1.id,
            workout_visibility=workout_cycling_user_1.workout_visibility,
            text=self.random_string(),
            text_visibility=input_text_visibility,
        )

        assert comment.text_visibility == input_text_visibility

    @pytest.mark.parametrize(
        'input_workout_visibility, input_text_visibility',
        [
            (PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS_AND_REMOTE),
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.FOLLOWERS_AND_REMOTE),
        ],
    )
    def test_it_raises_when_workout_visibility_is_stricter(
        self,
        input_workout_visibility: PrivacyLevel,
        input_text_visibility: PrivacyLevel,
        app_with_federation: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        with pytest.raises(
            InvalidVisibilityException,
            match=(
                f'invalid visibility: {input_text_visibility} '
                f'\\(workout visibility: {input_workout_visibility}\\)'
            ),
        ):
            WorkoutComment(
                user_id=user_1.id,
                workout_id=workout_cycling_user_1.id,
                workout_visibility=workout_cycling_user_1.workout_visibility,
                text=self.random_string(),
                text_visibility=input_text_visibility,
            )


class TestWorkoutCommentModelSerializeForCommentOwner(
    WorkoutCommentModelTestCase
):
    def test_it_serializes_owner_comment(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'user_id': user_1.id,
            'workout_id': workout_cycling_user_1.id,
            'text': comment.text,
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
        }


class TestWorkoutCommentModelSerializeForRemoteFollower(
    WorkoutCommentModelTestCase
):
    def test_it_raises_error_when_user_does_not_follow_comment_user(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        user_1: User,
    ) -> None:
        remote_cycling_workout.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment = self.create_comment(
            user=remote_user,
            workout=remote_cycling_workout,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_1)

    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_serializes_comment_for_follower_when_privacy_allows_it(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
        input_visibility: PrivacyLevel,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        remote_cycling_workout.workout_visibility = input_visibility
        comment = self.create_comment(
            user=remote_user,
            workout=remote_cycling_workout,
            text_visibility=input_visibility,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'user_id': remote_user.id,
            'workout_id': remote_cycling_workout.id,
            'text': comment.text,
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
        }


class TestWorkoutCommentModelSerializeForUser(WorkoutCommentModelTestCase):
    def test_it_raises_error_when_comment_is_visible_to_remote_follower(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=remote_user,
            workout=remote_cycling_workout,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_1)


class TestWorkoutCommentModelSerializeForUnauthenticatedUser(
    WorkoutCommentModelTestCase
):
    def test_it_raises_error_when_comment_is_visible_to_remote_follower(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=remote_cycling_workout,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize()
