import pytest
from flask import Flask

from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.models import WorkoutComment
from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.tests.workouts.utils import WorkoutCommentMixin
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

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


class TestWorkoutCommentModelSerializeForCommentOwner(WorkoutCommentMixin):
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
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
        }


class TestWorkoutCommentModelSerializeForRemoteFollower(WorkoutCommentMixin):
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

    def test_it_raises_error_when_privacy_does_not_allows_it(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        user_1: User,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        remote_cycling_workout.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment = self.create_comment(
            user=remote_user,
            workout=remote_cycling_workout,
            text_visibility=PrivacyLevel.FOLLOWERS,
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
            'id': comment.short_id,
            'user': remote_user.serialize(),
            'workout_id': remote_cycling_workout.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
        }


class TestWorkoutCommentModelSerializeForUser(WorkoutCommentMixin):
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
    WorkoutCommentMixin
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


class TestWorkoutCommentModelGetCreateActivity(WorkoutCommentMixin):
    activity_type = 'Create'
    expected_object_type = 'Note'

    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]
    )
    def test_it_raises_error_if_visibility_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_cycling_workout: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=remote_cycling_workout,
            text_visibility=input_visibility,
        )
        with pytest.raises(InvalidVisibilityException):
            comment.get_activity(activity_type=self.activity_type)

    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_returns_activities_when_visibility_is_valid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_cycling_workout: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=remote_cycling_workout,
            text_visibility=input_visibility,
        )

        note_activity = comment.get_activity(activity_type=self.activity_type)

        assert note_activity['type'] == self.activity_type
        assert note_activity['object']['type'] == self.expected_object_type
        assert note_activity['object']['id'] == comment.ap_id


class TestWorkoutCommentModelGetDeleteActivity(
    TestWorkoutCommentModelGetCreateActivity
):
    activity_type = 'Delete'
    expected_object_type = 'Tombstone'


class TestWorkoutCommentModelSerializeForMentions(WorkoutCommentMixin):
    def test_it_serializes_comment_with_mentions_as_link(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"@{remote_user.fullname} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment["text"] == comment.text
        assert serialized_comment["text_html"] == comment.handle_mentions()[0]
