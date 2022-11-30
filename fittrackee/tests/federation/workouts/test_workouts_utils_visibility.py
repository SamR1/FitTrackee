import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout
from fittrackee.workouts.utils.visibility import can_view_workout


class TestFederationCanViewWorkout:
    def test_workout_owner_can_view_his_workout(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )

        assert can_view_workout(
            workout_cycling_user_1, 'workout_visibility', user_1
        ) == (True, 'owner')

    @pytest.mark.parametrize(
        'input_workout_visibility',
        [
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_remote_follower_can_not_view_workout_when_visibility_does_not_allow_it(  # noqa
        self,
        input_workout_visibility: PrivacyLevel,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_visibility

        assert can_view_workout(
            workout_cycling_user_2, 'workout_visibility', user_1
        ) == (False, 'remote_follower')

    @pytest.mark.parametrize(
        'input_workout_visibility',
        [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.PUBLIC,
        ],
    )
    def test_remote_follower_can_view_workout_when_visibility_allows_it(
        self,
        input_workout_visibility: PrivacyLevel,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_visibility

        assert can_view_workout(
            workout_cycling_user_2, 'workout_visibility', user_1
        ) == (True, 'remote_follower')

    def test_local_follower_can_view_workout_when_follower_and_remote_only(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )

        assert can_view_workout(
            workout_cycling_user_2, 'workout_visibility', user_1
        ) == (True, 'follower')

    def test_another_user_can_not_view_workout_when_follower_and_remote_only(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )

        assert can_view_workout(
            workout_cycling_user_2, 'workout_visibility', user_1
        ) == (False, 'other')


class TestFederationCanViewWorkoutMap:
    def test_workout_owner_can_view_his_workout_map(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.map_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )

        assert can_view_workout(
            workout_cycling_user_1, 'map_visibility', user_1
        ) == (True, 'owner')

    @pytest.mark.parametrize(
        'input_map_visibility',
        [
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_remote_follower_can_not_view_workout_map_when_visibility_does_not_allow_it(  # noqa
        self,
        input_map_visibility: PrivacyLevel,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_2.map_visibility = input_map_visibility

        assert can_view_workout(
            workout_cycling_user_2, 'map_visibility', user_1
        ) == (False, 'remote_follower')

    @pytest.mark.parametrize(
        'input_map_visibility',
        [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.PUBLIC,
        ],
    )
    def test_remote_follower_can_view_workout_map_when_visibility_allows_it(
        self,
        input_map_visibility: PrivacyLevel,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_2.map_visibility = input_map_visibility

        assert can_view_workout(
            workout_cycling_user_2, 'map_visibility', user_1
        ) == (True, 'remote_follower')

    def test_local_follower_can_not_view_workout_map_when_follower_and_remote_only(  # noqa
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
        workout_cycling_user_2.map_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )

        assert can_view_workout(
            workout_cycling_user_2, 'map_visibility', user_1
        ) == (True, 'follower')

    def test_another_user_can_not_view_workout_map_when_follower_and_remote_only(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_2.map_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )

        assert can_view_workout(
            workout_cycling_user_2, 'map_visibility', user_1
        ) == (False, 'other')
