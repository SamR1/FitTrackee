from datetime import datetime

import pytest
from flask import Flask
from freezegun import freeze_time

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.utils import encode_uuid
from fittrackee.workouts.exceptions import CommentForbiddenException
from fittrackee.workouts.models import Sport, Workout, WorkoutComment

from .utils import WorkoutCommentMixin


class TestWorkoutCommentModel(WorkoutCommentMixin):
    def test_comment_model(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        text = self.random_string()
        created_at = datetime.utcnow()
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text=text,
            created_at=created_at,
        )

        assert comment.user_id == user_1.id
        assert comment.workout_id == workout_cycling_user_1.id
        assert comment.text == text
        assert comment.created_at == created_at
        assert comment.modification_date is None

    def test_created_date_is_initialized_on_creation_when_not_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        now = datetime.utcnow()
        with freeze_time(now):

            comment = self.create_comment(
                user=user_1,
                workout=workout_cycling_user_1,
            )

        assert comment.created_at == now

    def test_privacy_is_private_when_not_provided_on_creation(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        now = datetime.utcnow()
        with freeze_time(now):

            comment = WorkoutComment(
                user_id=user_1.id,
                workout_id=workout_cycling_user_1.id,
                workout_visibility=workout_cycling_user_1.workout_visibility,
                text=self.random_string(),
                created_at=now,
            )

        assert comment.text_visibility == PrivacyLevel.PRIVATE

    def test_it_raises_error_when_privacy_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        text_visibility = PrivacyLevel.FOLLOWERS_AND_REMOTE
        with pytest.raises(
            InvalidVisibilityException,
            match=(
                f'invalid visibility: {text_visibility}, '
                'federation is disabled.'
            ),
        ):
            WorkoutComment(
                user_id=user_1.id,
                workout_id=workout_cycling_user_1.id,
                workout_visibility=workout_cycling_user_1.workout_visibility,
                text=self.random_string(),
                text_visibility=text_visibility,
            )

    @pytest.mark.parametrize(
        'input_workout_visibility, input_text_visibility',
        [
            (PrivacyLevel.PRIVATE, PrivacyLevel.PRIVATE),
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.FOLLOWERS),
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE),
            (PrivacyLevel.PUBLIC, PrivacyLevel.PUBLIC),
            (PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS),
            (PrivacyLevel.PUBLIC, PrivacyLevel.PRIVATE),
        ],
    )
    def test_it_initializes_text_visibility_when_workout_visibility_is_not_stricter(  # noqa
        self,
        input_workout_visibility: PrivacyLevel,
        input_text_visibility: PrivacyLevel,
        app: Flask,
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
            (PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS),
            (PrivacyLevel.PRIVATE, PrivacyLevel.PUBLIC),
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_raises_when_workout_visibility_is_stricter(
        self,
        input_workout_visibility: PrivacyLevel,
        input_text_visibility: PrivacyLevel,
        app: Flask,
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

    def test_short_id_returns_encoded_comment_uuid(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
        )

        assert comment.short_id == encode_uuid(comment.uuid)

    def test_it_returns_string_representation(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
        )

        assert str(comment) == f'<WorkoutComment {comment.id}>'


class TestWorkoutCommentModelSerializeForCommentOwner(WorkoutCommentMixin):
    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC],
    )
    def test_it_serializes_owner_comment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=input_visibility,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'modification_date': comment.modification_date,
        }


class TestWorkoutCommentModelSerializeForFollower(WorkoutCommentMixin):
    def test_it_raises_error_when_user_does_not_follow_comment_owner(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_2)

    def test_it_raises_error_when_privacy_does_not_allow_it(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PRIVATE,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_2)

    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC]
    )
    def test_it_serializes_comment_for_follower_when_privacy_allows_it(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
        input_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = input_visibility
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=input_visibility,
        )

        serialized_comment = comment.serialize(user_2)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'modification_date': comment.modification_date,
        }


class TestWorkoutCommentModelSerializeForUser(WorkoutCommentMixin):
    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE]
    )
    def test_it_raises_error_when_comment_is_not_public(
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
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=input_visibility,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_2)

    def test_it_serializes_comment_when_comment_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        # TODO: mentions
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )

        serialized_comment = comment.serialize(user_2)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'modification_date': comment.modification_date,
        }


class TestWorkoutCommentModelSerializeForUnauthenticatedUser(
    WorkoutCommentMixin
):
    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE]
    )
    def test_it_raises_error_when_comment_is_not_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=input_visibility,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize()

    def test_it_serializes_comment_when_comment_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        # TODO: mentions
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )

        serialized_comment = comment.serialize()

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'modification_date': comment.modification_date,
        }
