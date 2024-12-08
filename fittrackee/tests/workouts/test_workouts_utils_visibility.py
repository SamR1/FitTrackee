import pytest
from flask import Flask

from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel, can_view
from fittrackee.workouts.models import Sport, Workout


class TestCanViewWorkout:
    @pytest.mark.parametrize(
        'input_description,input_workout_visibility',
        [
            (
                f'workout visibility: {VisibilityLevel.PRIVATE.value}',
                VisibilityLevel.PRIVATE,
            ),
            (
                f'workout visibility: {VisibilityLevel.FOLLOWERS.value}',
                VisibilityLevel.FOLLOWERS,
            ),
            (
                f'workout visibility: {VisibilityLevel.PUBLIC.value}',
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_workout_owner_can_view_his_workout(
        self,
        input_description: str,
        input_workout_visibility: VisibilityLevel,
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
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PRIVATE

        assert (
            can_view(workout_cycling_user_2, 'workout_visibility', user_1)
            is False
        )

    @pytest.mark.parametrize(
        'input_description,input_workout_visibility',
        [
            (
                f'workout visibility: {VisibilityLevel.FOLLOWERS.value}',
                VisibilityLevel.FOLLOWERS,
            ),
            (
                f'workout visibility: {VisibilityLevel.PUBLIC.value}',
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_follower_can_view_workout_when_public_or_follower_only(
        self,
        input_description: str,
        input_workout_visibility: VisibilityLevel,
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
                f'workout visibility: {VisibilityLevel.PRIVATE.value}',
                VisibilityLevel.PRIVATE,
            ),
            (
                f'workout visibility: {VisibilityLevel.FOLLOWERS.value}',
                VisibilityLevel.FOLLOWERS,
            ),
        ],
    )
    def test_another_user_can_not_view_workout_when_private_or_follower_only(
        self,
        input_description: str,
        input_workout_visibility: VisibilityLevel,
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

    def test_another_user_can_not_view_workout_when_public_and_user_blocked(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        user_2.blocks_user(user_1)

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
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC

        assert (
            can_view(workout_cycling_user_2, 'workout_visibility', user_1)
            is True
        )

    @pytest.mark.parametrize(
        'input_description,input_workout_visibility',
        [
            (
                f'workout visibility: {VisibilityLevel.PRIVATE.value}',
                VisibilityLevel.PRIVATE,
            ),
            (
                f'workout visibility: {VisibilityLevel.FOLLOWERS.value}',
                VisibilityLevel.FOLLOWERS,
            ),
        ],
    )
    def test_workout_can_not_viewed_when_no_user_and_private_or_follower_only_visibility(  # noqa
        self,
        input_description: str,
        input_workout_visibility: VisibilityLevel,
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
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC

        assert can_view(workout_cycling_user_2, 'workout_visibility') is True


class TestCanViewWorkoutMap:
    @pytest.mark.parametrize(
        'input_description,input_map_visibility',
        [
            (
                f'map visibility: {VisibilityLevel.PRIVATE.value}',
                VisibilityLevel.PRIVATE,
            ),
            (
                f'map visibility: {VisibilityLevel.FOLLOWERS.value}',
                VisibilityLevel.FOLLOWERS,
            ),
            (
                f'map visibility: {VisibilityLevel.PUBLIC.value}',
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_workout_owner_can_view_his_workout_map(
        self,
        input_description: str,
        input_map_visibility: VisibilityLevel,
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
        workout_cycling_user_2.map_visibility = VisibilityLevel.PRIVATE

        assert (
            can_view(workout_cycling_user_2, 'map_visibility', user_1) is False
        )

    @pytest.mark.parametrize(
        'input_description,input_map_visibility',
        [
            (
                f'map visibility: {VisibilityLevel.FOLLOWERS.value}',
                VisibilityLevel.FOLLOWERS,
            ),
            (
                f'map visibility: {VisibilityLevel.PUBLIC.value}',
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_follower_can_view_workout_map_when_public_or_follower_only(
        self,
        input_description: str,
        input_map_visibility: VisibilityLevel,
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
                f'map visibility: {VisibilityLevel.PRIVATE.value}',
                VisibilityLevel.PRIVATE,
            ),
            (
                f'map visibility: {VisibilityLevel.FOLLOWERS.value}',
                VisibilityLevel.FOLLOWERS,
            ),
        ],
    )
    def test_another_user_can_not_view_workout_map_when_private_or_follower_only(  # noqa
        self,
        input_description: str,
        input_map_visibility: VisibilityLevel,
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
        workout_cycling_user_2.map_visibility = VisibilityLevel.PUBLIC

        assert (
            can_view(workout_cycling_user_2, 'map_visibility', user_1) is True
        )

    @pytest.mark.parametrize(
        'input_description,input_map_visibility',
        [
            (
                f'map visibility: {VisibilityLevel.PRIVATE.value}',
                VisibilityLevel.PRIVATE,
            ),
            (
                f'map visibility: {VisibilityLevel.FOLLOWERS.value}',
                VisibilityLevel.FOLLOWERS,
            ),
        ],
    )
    def test_map_can_not_viewed_when_no_user_and_private_or_follower_only_visibility(  # noqa
        self,
        input_description: str,
        input_map_visibility: VisibilityLevel,
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
        workout_cycling_user_2.map_visibility = VisibilityLevel.PUBLIC

        assert can_view(workout_cycling_user_2, 'map_visibility') is True
