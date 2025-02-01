import pytest
from flask import Flask

from fittrackee import db
from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.objects.like import LikeObject
from fittrackee.tests.workouts.test_workouts_model import WorkoutModelTestCase
from fittrackee.tests.workouts.utils import add_follower
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import (
    Sport,
    Workout,
    WorkoutLike,
    WorkoutSegment,
)

from ...utils import random_string

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class TestWorkoutModelAsRemoteFollower(WorkoutModelTestCase):
    def test_it_raises_exception_when_workout_visibility_is_private(
        self,
        app_with_federation: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        remote_user: User,
    ) -> None:
        add_follower(user_1, remote_user)
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PRIVATE

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(user=remote_user)

    def test_it_raises_exception_when_workout_visibility_is_local_follower_only(  # noqa
        self,
        app_with_federation: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        remote_user: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        add_follower(user_1, remote_user)
        workout_cycling_user_1.workout_visibility = VisibilityLevel.FOLLOWERS

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(user=remote_user)

    @pytest.mark.parametrize(
        "input_analysis_visibility,input_workout_visibility",
        [
            (
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
            ),
            (
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
                VisibilityLevel.PUBLIC,
            ),
            (
                VisibilityLevel.PUBLIC,
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_serializer_returns_analysis_related_data(
        self,
        input_analysis_visibility: VisibilityLevel,
        input_workout_visibility: VisibilityLevel,
        app_with_federation: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        remote_user: User,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        add_follower(user_1, remote_user)
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.analysis_visibility = input_analysis_visibility
        workout = self.update_workout_with_gpx_data(
            workout_cycling_user_1, map_id=random_string()
        )

        serialized_workout = workout.serialize(user=remote_user, light=False)

        assert serialized_workout["map"] is None
        assert serialized_workout["bounds"] == []
        assert serialized_workout["with_gpx"] is False
        assert serialized_workout["map_visibility"] == VisibilityLevel.PRIVATE
        assert (
            serialized_workout["analysis_visibility"]
            == input_analysis_visibility
        )
        assert (
            serialized_workout["workout_visibility"]
            == input_workout_visibility
        )
        assert serialized_workout["segments"] == [
            workout_cycling_user_1_segment.serialize()
        ]

    @pytest.mark.parametrize(
        "input_analysis_visibility,input_workout_visibility",
        [
            (
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
            ),
            (
                VisibilityLevel.PRIVATE,
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
            ),
        ],
    )
    def test_serializer_does_not_return_analysis_related_data(
        self,
        input_analysis_visibility: VisibilityLevel,
        input_workout_visibility: VisibilityLevel,
        app_with_federation: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        remote_user: User,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        add_follower(user_1, remote_user)
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.analysis_visibility = input_analysis_visibility
        workout = self.update_workout_with_gpx_data(workout_cycling_user_1)

        serialized_workout = workout.serialize(user=remote_user)

        assert serialized_workout["map"] is None
        assert serialized_workout["bounds"] == []
        assert serialized_workout["with_gpx"] is False
        assert serialized_workout["map_visibility"] == VisibilityLevel.PRIVATE
        assert (
            serialized_workout["analysis_visibility"]
            == VisibilityLevel.PRIVATE
        )
        assert (
            serialized_workout["workout_visibility"]
            == input_workout_visibility
        )
        assert serialized_workout["segments"] == []


class TestWorkoutModelGetWorkoutCreateActivity:
    activity_type = "Create"

    @pytest.mark.parametrize(
        "input_visibility",
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    def test_it_raises_error_if_visibility_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
        with pytest.raises(InvalidVisibilityException):
            workout_cycling_user_1.get_activities(
                activity_type=self.activity_type
            )

    @pytest.mark.parametrize(
        "workout_visibility",
        [VisibilityLevel.FOLLOWERS_AND_REMOTE, VisibilityLevel.PUBLIC],
    )
    def test_it_returns_activities_when_visibility_is_valid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = workout_visibility
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()
        workout_cycling_user_1.remote_url = (
            workout_cycling_user_1.get_remote_url()
        )

        create_workout, create_note = workout_cycling_user_1.get_activities(
            activity_type=self.activity_type
        )

        assert create_workout["type"] == self.activity_type
        assert create_workout["object"]["type"] == "Workout"
        assert create_note["type"] == self.activity_type
        assert create_note["object"]["type"] == "Note"


class TestWorkoutModelGetWorkoutUpdateActivity(
    TestWorkoutModelGetWorkoutCreateActivity
):
    activity_type = "Update"


class TestWorkoutModelGetWorkoutDeleteActivity:
    @pytest.mark.parametrize(
        "input_visibility",
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    def test_it_raises_error_if_visibility_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
        with pytest.raises(InvalidVisibilityException):
            workout_cycling_user_1.get_activities(activity_type="Delete")

    @pytest.mark.parametrize(
        "workout_visibility",
        [VisibilityLevel.FOLLOWERS_AND_REMOTE, VisibilityLevel.PUBLIC],
    )
    def test_it_returns_activities_when_visibility_is_valid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = workout_visibility
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()

        delete_workout, _ = workout_cycling_user_1.get_activities(
            activity_type="Delete"
        )

        assert delete_workout["type"] == "Delete"
        assert delete_workout["object"]["type"] == "Tombstone"
        assert delete_workout["object"]["id"] == workout_cycling_user_1.ap_id


class TestWorkoutLikeActivities:
    def test_it_returns_like_activity(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()
        workout_cycling_user_1.remote_url = (
            workout_cycling_user_1.get_remote_url()
        )
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()

        like_activity = like.get_activity()

        assert (
            like_activity
            == LikeObject(
                target_object_ap_id=workout_cycling_user_1.ap_id,
                like_id=like.id,
                actor_ap_id=user_1.actor.activitypub_id,
            ).get_activity()
        )

    def test_it_returns_undo_like_activity(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()
        workout_cycling_user_1.remote_url = (
            workout_cycling_user_1.get_remote_url()
        )
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()

        like_activity = like.get_activity(is_undo=True)

        assert (
            like_activity
            == LikeObject(
                target_object_ap_id=workout_cycling_user_1.ap_id,
                like_id=like.id,
                actor_ap_id=user_1.actor.activitypub_id,
                is_undo=True,
            ).get_activity()
        )
