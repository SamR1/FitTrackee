from datetime import datetime, timezone
from typing import Any, Dict

import pytest
from flask import Flask

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.constants import AP_CTX, DATE_FORMAT
from fittrackee.federation.exceptions import InvalidWorkoutException
from fittrackee.federation.objects.exceptions import InvalidObjectException
from fittrackee.federation.objects.workout import (
    WorkoutObject,
    convert_duration_string_to_seconds,
    convert_workout_activity,
)
from fittrackee.tests.mixins import RandomMixin
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.constants import WORKOUT_DATE_FORMAT
from fittrackee.workouts.models import Sport, Workout


class WorkoutObjectTestCase(RandomMixin):
    @staticmethod
    def get_updated(workout: Workout, activity_type: str) -> Dict:
        return (
            {"updated": workout.modification_date.strftime(DATE_FORMAT)}
            if activity_type == "Update" and workout.modification_date
            else {}
        )


class TestWorkoutObject(WorkoutObjectTestCase):
    @pytest.mark.parametrize(
        "input_visibility",
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    def test_it_raises_error_when_visibility_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
        with pytest.raises(
            InvalidVisibilityException,
            match=f"object visibility is: '{input_visibility.value}'",
        ):
            WorkoutObject(workout_cycling_user_1, "Create")

    def test_it_raises_error_when_activity_type_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        invalid_activity_type = self.random_string()
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()
        workout_cycling_user_1.remote_url = (
            workout_cycling_user_1.get_remote_url()
        )
        with pytest.raises(
            ValueError,
            match=f"'{invalid_activity_type}' is not a valid ActivityType",
        ):
            WorkoutObject(workout_cycling_user_1, invalid_activity_type)

    def test_it_raises_error_when_workout_has_no_ap_id(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.remote_url = (
            workout_cycling_user_1.get_remote_url()
        )
        with pytest.raises(
            InvalidObjectException,
            match="Invalid workout, missing 'ap_id' or 'remote_url'",
        ):
            WorkoutObject(workout_cycling_user_1, "Create")

    def test_it_raises_error_when_workout_has_no_remote_url(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()
        with pytest.raises(
            InvalidObjectException,
            match="Invalid workout, missing 'ap_id' or 'remote_url'",
        ):
            WorkoutObject(workout_cycling_user_1, "Create")

    @pytest.mark.parametrize("input_activity_type", ["Create", "Update"])
    def test_it_generates_activity_when_visibility_is_followers_and_remote_only(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_activity_type: str,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = (
            VisibilityLevel.FOLLOWERS_AND_REMOTE
        )
        workout_cycling_user_1.modification_date = (
            datetime.now(timezone.utc)
            if input_activity_type == "Update"
            else None
        )
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()
        workout_cycling_user_1.remote_url = (
            workout_cycling_user_1.get_remote_url()
        )
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        updated = self.get_updated(workout_cycling_user_1, input_activity_type)
        workout = WorkoutObject(workout_cycling_user_1, input_activity_type)

        serialized_workout = workout.get_activity()

        assert serialized_workout == {
            "@context": AP_CTX,
            "id": (
                f"{workout_cycling_user_1.ap_id}/{input_activity_type.lower()}"
            ),
            "type": input_activity_type,
            "actor": user_1.actor.activitypub_id,
            "published": published,
            "to": [user_1.actor.followers_url],
            "cc": [],
            "object": {
                "id": workout_cycling_user_1.ap_id,
                "type": "Workout",
                "published": published,
                "url": workout_cycling_user_1.remote_url,
                "attributedTo": user_1.actor.activitypub_id,
                "to": [user_1.actor.followers_url],
                "cc": [],
                "ave_speed": workout_cycling_user_1.ave_speed,
                "distance": workout_cycling_user_1.distance,
                "duration": str(workout_cycling_user_1.duration),
                "max_speed": workout_cycling_user_1.max_speed,
                "moving": str(workout_cycling_user_1.moving),
                "sport_id": workout_cycling_user_1.sport_id,
                "title": workout_cycling_user_1.title,
                "workout_date": workout_cycling_user_1.workout_date.strftime(
                    WORKOUT_DATE_FORMAT
                ),
                **updated,
            },
        }

    @pytest.mark.parametrize("input_activity_type", ["Create", "Update"])
    def test_it_generates_create_activity_when_visibility_is_public(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_activity_type: str,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.modification_date = (
            datetime.now(timezone.utc)
            if input_activity_type == "Update"
            else None
        )
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()
        workout_cycling_user_1.remote_url = (
            workout_cycling_user_1.get_remote_url()
        )
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()
        workout_cycling_user_1.remote_url = (
            workout_cycling_user_1.get_remote_url()
        )
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        updated = self.get_updated(workout_cycling_user_1, input_activity_type)
        workout = WorkoutObject(workout_cycling_user_1, input_activity_type)

        serialized_workout = workout.get_activity()

        assert serialized_workout == {
            "@context": AP_CTX,
            "id": (
                f"{workout_cycling_user_1.ap_id}/{input_activity_type.lower()}"
            ),
            "type": input_activity_type,
            "actor": user_1.actor.activitypub_id,
            "published": published,
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [user_1.actor.followers_url],
            "object": {
                "id": workout_cycling_user_1.ap_id,
                "type": "Workout",
                "published": published,
                "url": workout_cycling_user_1.remote_url,
                "attributedTo": user_1.actor.activitypub_id,
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": [user_1.actor.followers_url],
                "ave_speed": workout_cycling_user_1.ave_speed,
                "distance": workout_cycling_user_1.distance,
                "duration": str(workout_cycling_user_1.duration),
                "max_speed": workout_cycling_user_1.max_speed,
                "moving": str(workout_cycling_user_1.moving),
                "sport_id": workout_cycling_user_1.sport_id,
                "title": workout_cycling_user_1.title,
                "workout_date": workout_cycling_user_1.workout_date.strftime(
                    WORKOUT_DATE_FORMAT
                ),
                **updated,
            },
        }


class TestWorkoutNoteObject(WorkoutObjectTestCase):
    @staticmethod
    def expected_workout_note(workout: Workout, expected_url: str) -> str:
        return f"""<p>New workout: <a href="{expected_url}" target="_blank" rel="noopener noreferrer">{workout.title}</a> ({workout.sport.label})

Distance: {workout.distance:.2f}km
Duration: {workout.duration}</p>
"""

    @pytest.mark.parametrize("input_activity_type", ["Create", "Update"])
    def test_it_returns_note_activity_when_visibility_is_followers_only(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_activity_type: str,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = (
            VisibilityLevel.FOLLOWERS_AND_REMOTE
        )
        workout_cycling_user_1.modification_date = (
            datetime.now(timezone.utc)
            if input_activity_type == "Update"
            else None
        )
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()
        workout_cycling_user_1.remote_url = (
            workout_cycling_user_1.get_remote_url()
        )
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        updated = self.get_updated(workout_cycling_user_1, input_activity_type)
        workout = WorkoutObject(workout_cycling_user_1, input_activity_type)

        serialized_workout_note = workout.get_activity(is_note=True)

        assert serialized_workout_note == {
            "@context": AP_CTX,
            "id": (
                f"{workout_cycling_user_1.ap_id}/"
                f"note/{input_activity_type.lower()}"
            ),
            "type": input_activity_type,
            "actor": user_1.actor.activitypub_id,
            "published": published,
            "to": [user_1.actor.followers_url],
            "cc": [],
            "object": {
                "id": workout_cycling_user_1.ap_id,
                "type": "Note",
                "published": published,
                "url": workout_cycling_user_1.remote_url,
                "attributedTo": user_1.actor.activitypub_id,
                "content": self.expected_workout_note(
                    workout_cycling_user_1,
                    workout_cycling_user_1.remote_url,  # type: ignore
                ),
                "to": [user_1.actor.followers_url],
                "cc": [],
                **updated,
            },
        }

    @pytest.mark.parametrize("input_activity_type", ["Create", "Update"])
    def test_it_returns_note_activity_when_visibility_is_public(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_activity_type: str,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.modification_date = (
            datetime.now(timezone.utc)
            if input_activity_type == "Update"
            else None
        )
        workout_cycling_user_1.ap_id = workout_cycling_user_1.get_ap_id()
        workout_cycling_user_1.remote_url = (
            workout_cycling_user_1.get_remote_url()
        )
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        updated = self.get_updated(workout_cycling_user_1, input_activity_type)
        workout = WorkoutObject(workout_cycling_user_1, input_activity_type)

        serialized_workout_note = workout.get_activity(is_note=True)

        assert serialized_workout_note == {
            "@context": AP_CTX,
            "id": (
                f"{workout_cycling_user_1.ap_id}/"
                f"note/{input_activity_type.lower()}"
            ),
            "type": input_activity_type,
            "actor": user_1.actor.activitypub_id,
            "published": published,
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [user_1.actor.followers_url],
            "object": {
                "id": workout_cycling_user_1.ap_id,
                "type": "Note",
                "published": published,
                "url": workout_cycling_user_1.remote_url,
                "attributedTo": user_1.actor.activitypub_id,
                "content": self.expected_workout_note(
                    workout_cycling_user_1,
                    workout_cycling_user_1.remote_url,  # type: ignore
                ),
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": [user_1.actor.followers_url],
                **updated,
            },
        }


class TestWorkoutConvertDurationStringToSeconds:
    @pytest.mark.parametrize(
        "input_duration,expected_seconds",
        [
            ("0:00:00", 0),
            ("1:00:00", 3600),
            ("01:00:00", 3600),
            ("00:30:00", 1800),
            ("00:00:10", 10),
            ("01:20:30", 4830),
        ],
    )
    def test_it_converts_duration_string_into_seconds(
        self, input_duration: str, expected_seconds: int
    ) -> None:
        assert (
            convert_duration_string_to_seconds(duration_str=input_duration)
            == expected_seconds
        )

    @pytest.mark.parametrize(
        "input_duration",
        ["", "1:00", 3600, None],
    )
    def test_it_raises_exception_if_duration_is_invalid(
        self, input_duration: Any
    ) -> None:
        with pytest.raises(
            InvalidWorkoutException,
            match="Invalid workout data: duration or moving format is invalid",
        ):
            convert_duration_string_to_seconds(duration_str=input_duration)


class TestWorkoutConvertWorkoutActivity(RandomMixin):
    def test_it_convert_workout_data_from_activity(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_activity_object = {
            "id": self.random_string(),
            "type": "Workout",
            "published": workout_cycling_user_1.creation_date.strftime(
                DATE_FORMAT
            ),
            "url": self.random_string(),
            "attributedTo": user_1.actor.activitypub_id,
            "to": [user_1.actor.followers_url],
            "cc": [],
            "ave_speed": workout_cycling_user_1.ave_speed,
            "distance": workout_cycling_user_1.distance,
            "duration": str(workout_cycling_user_1.duration),
            "max_speed": workout_cycling_user_1.max_speed,
            "moving": str(workout_cycling_user_1.moving),
            "sport_id": workout_cycling_user_1.sport_id,
            "title": workout_cycling_user_1.title,
            "workout_date": workout_cycling_user_1.workout_date.strftime(
                WORKOUT_DATE_FORMAT
            ),
            "workout_visibility": workout_cycling_user_1.workout_visibility,
        }

        assert convert_workout_activity(workout_activity_object) == {
            **workout_activity_object,
            "duration": workout_cycling_user_1.duration.seconds,
            "moving": workout_cycling_user_1.moving.seconds,  # type: ignore
        }
