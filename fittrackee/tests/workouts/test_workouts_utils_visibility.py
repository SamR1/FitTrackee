import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel, can_view
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout


class TestCanViewWorkout:
    @pytest.mark.parametrize(
        'input_description,input_workout_visibility',
        [
            (
                f'workout visibility: {PrivacyLevel.PRIVATE.value}',
                PrivacyLevel.PRIVATE,
            ),
            (
                f'workout visibility: {PrivacyLevel.FOLLOWERS.value}',
                PrivacyLevel.FOLLOWERS,
            ),
            (
                f'workout visibility: {PrivacyLevel.PUBLIC.value}',
                PrivacyLevel.PUBLIC,
            ),
        ],
    )
    def test_workout_owner_can_view_his_workout(
        self,
        input_description: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility

        assert (
            can_view(workout_cycling_user_1, 'workout_visibility', user_1)
            is True
        )

    def test_follower_can_not_view_workout_when_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PRIVATE

        assert (
            can_view(workout_cycling_user_2, 'workout_visibility', user_1)
            is False
        )

    @pytest.mark.parametrize(
        'input_description,input_workout_visibility',
        [
            (
                f'workout visibility: {PrivacyLevel.FOLLOWERS.value}',
                PrivacyLevel.FOLLOWERS,
            ),
            (
                f'workout visibility: {PrivacyLevel.PUBLIC.value}',
                PrivacyLevel.PUBLIC,
            ),
        ],
    )
    def test_follower_can_view_workout_when_public_or_follower_only(
        self,
        input_description: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_visibility

        assert (
            can_view(workout_cycling_user_2, 'workout_visibility', user_1)
            is True
        )

    @pytest.mark.parametrize(
        'input_description,input_workout_visibility',
        [
            (
                f'workout visibility: {PrivacyLevel.PRIVATE.value}',
                PrivacyLevel.PRIVATE,
            ),
            (
                f'workout visibility: {PrivacyLevel.FOLLOWERS.value}',
                PrivacyLevel.FOLLOWERS,
            ),
        ],
    )
    def test_another_user_can_not_view_workout_when_private_or_follower_only(
        self,
        input_description: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility

        assert (
            can_view(workout_cycling_user_2, 'workout_visibility', user_1)
            is False
        )

    def test_another_user_can_view_workout_when_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC

        assert (
            can_view(workout_cycling_user_2, 'workout_visibility', user_1)
            is True
        )

    @pytest.mark.parametrize(
        'input_description,input_workout_visibility',
        [
            (
                f'workout visibility: {PrivacyLevel.PRIVATE.value}',
                PrivacyLevel.PRIVATE,
            ),
            (
                f'workout visibility: {PrivacyLevel.FOLLOWERS.value}',
                PrivacyLevel.FOLLOWERS,
            ),
        ],
    )
    def test_workout_can_not_viewed_when_no_user_and_private_or_follower_only_visibility(  # noqa
        self,
        input_description: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility

        assert can_view(workout_cycling_user_2, 'workout_visibility') is False

    def test_workout_can_be_viewed_when_public_and_no_user_provided(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC

        assert can_view(workout_cycling_user_2, 'workout_visibility') is True


class TestCanViewWorkoutMap:
    @pytest.mark.parametrize(
        'input_description,input_map_visibility',
        [
            (
                f'map visibility: {PrivacyLevel.PRIVATE.value}',
                PrivacyLevel.PRIVATE,
            ),
            (
                f'map visibility: {PrivacyLevel.FOLLOWERS.value}',
                PrivacyLevel.FOLLOWERS,
            ),
            (
                f'map visibility: {PrivacyLevel.PUBLIC.value}',
                PrivacyLevel.PUBLIC,
            ),
        ],
    )
    def test_workout_owner_can_view_his_workout_map(
        self,
        input_description: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.map_visibility = input_map_visibility

        assert (
            can_view(workout_cycling_user_1, 'map_visibility', user_1) is True
        )

    def test_follower_can_not_view_workout_map_when_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.map_visibility = PrivacyLevel.PRIVATE

        assert (
            can_view(workout_cycling_user_2, 'map_visibility', user_1) is False
        )

    @pytest.mark.parametrize(
        'input_description,input_map_visibility',
        [
            (
                f'map visibility: {PrivacyLevel.FOLLOWERS.value}',
                PrivacyLevel.FOLLOWERS,
            ),
            (
                f'map visibility: {PrivacyLevel.PUBLIC.value}',
                PrivacyLevel.PUBLIC,
            ),
        ],
    )
    def test_follower_can_view_workout_map_when_public_or_follower_only(
        self,
        input_description: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.map_visibility = input_map_visibility

        assert (
            can_view(workout_cycling_user_2, 'map_visibility', user_1) is True
        )

    @pytest.mark.parametrize(
        'input_description,input_map_visibility',
        [
            (
                f'map visibility: {PrivacyLevel.PRIVATE.value}',
                PrivacyLevel.PRIVATE,
            ),
            (
                f'map visibility: {PrivacyLevel.FOLLOWERS.value}',
                PrivacyLevel.FOLLOWERS,
            ),
        ],
    )
    def test_another_user_can_not_view_workout_map_when_private_or_follower_only(  # noqa
        self,
        input_description: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.map_visibility = input_map_visibility

        assert (
            can_view(workout_cycling_user_2, 'map_visibility', user_1) is False
        )

    def test_another_user_can_view_workout_map_when_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.map_visibility = PrivacyLevel.PUBLIC

        assert (
            can_view(workout_cycling_user_2, 'map_visibility', user_1) is True
        )

    @pytest.mark.parametrize(
        'input_description,input_map_visibility',
        [
            (
                f'map visibility: {PrivacyLevel.PRIVATE.value}',
                PrivacyLevel.PRIVATE,
            ),
            (
                f'map visibility: {PrivacyLevel.FOLLOWERS.value}',
                PrivacyLevel.FOLLOWERS,
            ),
        ],
    )
    def test_map_can_not_viewed_when_no_user_and_private_or_follower_only_visibility(  # noqa
        self,
        input_description: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.map_visibility = input_map_visibility

        assert can_view(workout_cycling_user_2, 'map_visibility') is False

    def test_workout_can_be_viewed_when_public_and_no_user_provided(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.map_visibility = PrivacyLevel.PUBLIC

        assert can_view(workout_cycling_user_2, 'map_visibility') is True
