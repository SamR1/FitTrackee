from datetime import datetime, timedelta
from typing import List, Optional

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.federation.exceptions import FederationDisabledException
from fittrackee.tests.comments.mixins import CommentMixin
from fittrackee.users.models import User
from fittrackee.utils import encode_uuid
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import Sport, Workout, WorkoutLike

from ..mixins import ReportMixin
from ..utils import random_string
from .utils import add_follower


@pytest.mark.disable_autouse_update_records_patch
class WorkoutModelTestCase(ReportMixin):
    @staticmethod
    def update_workout(
        workout: Workout,
        map_id: Optional[str] = None,
        gpx_path: Optional[str] = None,
        bounds: Optional[List[float]] = None,
    ) -> Workout:
        workout.map_id = map_id
        workout.map = random_string() if map_id is None else map_id
        workout.gpx = random_string() if gpx_path is None else gpx_path
        workout.bounds = [1.0, 2.0, 3.0, 4.0] if bounds is None else bounds
        workout.pauses = timedelta(minutes=15)
        return workout


class TestWorkoutModelForOwner(WorkoutModelTestCase):
    def test_sport_label_and_date_are_in_string_value(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.title = 'Test'
        db.session.commit()
        assert (
            f'<Workout \'{sport_1_cycling.label}\' - 2018-01-01 00:00:00>'
            == str(workout_cycling_user_1)
        )

    def test_short_id_returns_encoded_workout_uuid(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        assert workout_cycling_user_1.short_id == encode_uuid(
            workout_cycling_user_1.uuid
        )

    def test_suspension_action_is_none_when_no_suspension(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        assert workout_cycling_user_1.suspension_action is None

    def test_suspension_action_is_last_suspension_action_when_comment_is_suspended(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        expected_report_action = self.create_report_workout_action(
            user_1_admin, user_2, workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()

        assert (
            workout_cycling_user_2.suspension_action == expected_report_action
        )

    def test_suspension_action_is_none_when_comment_is_unsuspended(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.create_report_workout_action(
            user_1_admin, user_2, workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = None

        assert workout_cycling_user_2.suspension_action is None

    def test_it_serializes_workout_without_gpx(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout = workout_cycling_user_1

        serialized_workout = workout.serialize(user=user_1, light=False)

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout.ave_speed),
            'bounds': [],
            'creation_date': workout.creation_date,
            'descent': None,
            'description': None,
            'distance': float(workout.distance),
            'duration': str(workout.duration),
            'id': workout.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout.max_speed),
            'min_alt': None,
            'modification_date': None,
            'moving': str(workout.moving),
            'next_workout': None,
            'notes': None,
            'pauses': None,
            'previous_workout': None,
            'records': [record.serialize() for record in workout.records],
            'segments': [],
            'sport_id': workout.sport_id,
            'suspended': False,
            'suspended_at': None,
            'title': None,
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout.workout_date,
            'workout_visibility': workout.workout_visibility.value,
            'with_gpx': False,
        }

    def test_it_serializes_workout_without_gpx_and_with_ascent_and_descent(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout = workout_cycling_user_1
        workout.ascent = 0
        workout.descent = 10

        serialized_workout = workout.serialize(user=user_1, light=False)

        assert serialized_workout == {
            'ascent': float(workout.ascent),
            'ave_speed': float(workout.ave_speed),
            'bounds': [],
            'creation_date': workout.creation_date,
            'descent': float(workout.descent),
            'description': None,
            'distance': float(workout.distance),
            'duration': str(workout.duration),
            'id': workout.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout.max_speed),
            'min_alt': None,
            'modification_date': workout.modification_date,
            'moving': str(workout.moving),
            'next_workout': None,
            'notes': None,
            'pauses': None,
            'previous_workout': None,
            'records': [record.serialize() for record in workout.records],
            'segments': [],
            'sport_id': workout.sport_id,
            'suspended': False,
            'suspended_at': None,
            'title': None,
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout.workout_date,
            'workout_visibility': workout.workout_visibility.value,
            'with_gpx': False,
        }

    def test_it_serializes_workout_with_gpx(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: Workout,
    ) -> None:
        workout = self.update_workout(workout_cycling_user_1)
        workout.ascent = 0
        workout.descent = 10

        serialized_workout = workout.serialize(user=user_1, light=False)

        assert serialized_workout == {
            'ascent': float(workout.ascent),
            'ave_speed': float(workout.ave_speed),
            'bounds': workout.bounds,
            'creation_date': workout.creation_date,
            'descent': float(workout.descent),
            'description': None,
            'distance': float(workout.distance),
            'duration': str(workout.duration),
            'id': workout.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout.max_speed),
            'min_alt': None,
            'modification_date': workout.modification_date,
            'moving': str(workout.moving),
            'next_workout': None,
            'notes': None,
            'pauses': str(workout.pauses),
            'previous_workout': None,
            'records': [record.serialize() for record in workout.records],
            'segments': [segment.serialize() for segment in workout.segments],
            'sport_id': workout.sport_id,
            'suspended': False,
            'suspended_at': None,
            'title': None,
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout.workout_date,
            'workout_visibility': workout.workout_visibility.value,
            'with_gpx': True,
        }

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility,'
        'expected_map_visibility',
        [
            (
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PRIVATE,
            ),
            (
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.FOLLOWERS,
            ),
            (
                VisibilityLevel.PUBLIC,
                VisibilityLevel.PUBLIC,
                VisibilityLevel.PUBLIC,
            ),
            (
                VisibilityLevel.PUBLIC,
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PRIVATE,
            ),
            (
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PRIVATE,
            ),
            (
                VisibilityLevel.PUBLIC,
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.FOLLOWERS,
            ),
            (
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.PUBLIC,
                VisibilityLevel.FOLLOWERS,
            ),
            (
                VisibilityLevel.PRIVATE,
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.PRIVATE,
            ),
            (
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PUBLIC,
                VisibilityLevel.PRIVATE,
            ),
        ],
    )
    def test_workout_visibility_overrides_map_visibility_when_stricter(
        self,
        input_map_visibility: VisibilityLevel,
        input_workout_visibility: VisibilityLevel,
        expected_map_visibility: VisibilityLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.map_visibility = input_map_visibility
        workout_cycling_user_1.workout_visibility = input_workout_visibility

        assert (
            workout_cycling_user_1.calculated_map_visibility
            == expected_map_visibility
        )
        serialized_workout = workout_cycling_user_1.serialize(
            user=user_1, light=False
        )

        assert (
            serialized_workout['map_visibility']
            == expected_map_visibility.value
        )

    @pytest.mark.parametrize(
        "input_workout_visibility",
        [
            VisibilityLevel.PRIVATE,
            VisibilityLevel.FOLLOWERS,
            VisibilityLevel.PUBLIC,
        ],
    )
    def test_it_serializes_suspended_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2_admin: User,
        workout_cycling_user_1: Workout,
        input_workout_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.suspended_at = datetime.utcnow()
        expected_report_action = self.create_report_workout_action(
            user_2_admin, user_1, workout_cycling_user_1
        )

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_1, light=False
        )

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_1.ave_speed),
            'bounds': [],
            'creation_date': workout_cycling_user_1.creation_date,
            'descent': None,
            'description': None,
            'distance': float(workout_cycling_user_1.distance),
            'duration': str(workout_cycling_user_1.duration),
            'id': workout_cycling_user_1.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout_cycling_user_1.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_1.max_speed),
            'min_alt': None,
            'modification_date': workout_cycling_user_1.modification_date,
            'moving': str(workout_cycling_user_1.moving),
            'next_workout': None,
            'notes': None,
            'pauses': None,
            'previous_workout': None,
            'records': [
                record.serialize() for record in workout_cycling_user_1.records
            ],
            'segments': [],
            'sport_id': workout_cycling_user_1.sport_id,
            'suspended': True,
            'suspended_at': workout_cycling_user_1.suspended_at,
            'suspension': expected_report_action.serialize(user_1, full=False),
            'title': None,
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_1.workout_date,
            'workout_visibility': (
                workout_cycling_user_1.workout_visibility.value
            ),
            'with_gpx': False,
        }

    def test_it_serializes_minimal_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_workout = workout_cycling_user_1.serialize(
            user=user_1, light=True
        )

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_1.ave_speed),
            'bounds': [],
            'creation_date': None,
            'descent': None,
            'distance': float(workout_cycling_user_1.distance),
            'duration': str(workout_cycling_user_1.duration),
            'id': workout_cycling_user_1.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout_cycling_user_1.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_1.max_speed),
            'min_alt': None,
            'modification_date': workout_cycling_user_1.modification_date,
            'moving': str(workout_cycling_user_1.moving),
            'next_workout': None,
            'notes': '',
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_1.sport_id,
            'suspended': False,
            'suspended_at': None,
            'title': None,
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_1.workout_date,
            'workout_visibility': (
                workout_cycling_user_1.workout_visibility.value
            ),
            'with_gpx': False,
        }

    def test_it_serializes_minimal_workout_with_gpx(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout = self.update_workout(workout_cycling_user_1)
        workout.ascent = 0
        workout.descent = 10

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_1, light=True
        )

        assert serialized_workout == {
            'ascent': float(workout_cycling_user_1.ascent),
            'ave_speed': float(workout_cycling_user_1.ave_speed),
            'bounds': [],
            'creation_date': None,
            'descent': float(workout_cycling_user_1.descent),
            'distance': float(workout_cycling_user_1.distance),
            'duration': str(workout_cycling_user_1.duration),
            'id': workout_cycling_user_1.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout_cycling_user_1.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_1.max_speed),
            'min_alt': None,
            'modification_date': None,
            'moving': str(workout_cycling_user_1.moving),
            'next_workout': None,
            'notes': '',
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_1.sport_id,
            'suspended': False,
            'suspended_at': None,
            'title': None,
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_1.workout_date,
            'workout_visibility': (
                workout_cycling_user_1.workout_visibility.value
            ),
            'with_gpx': True,
        }

    def test_it_serializes_minimal_suspended_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2_admin: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.suspended_at = datetime.utcnow()
        self.create_report_workout_action(
            user_2_admin, user_1, workout_cycling_user_1
        )

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_1, light=True
        )

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_1.ave_speed),
            'bounds': [],
            'creation_date': None,
            'descent': None,
            'distance': float(workout_cycling_user_1.distance),
            'duration': str(workout_cycling_user_1.duration),
            'id': workout_cycling_user_1.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout_cycling_user_1.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_1.max_speed),
            'min_alt': None,
            'modification_date': None,
            'moving': str(workout_cycling_user_1.moving),
            'next_workout': None,
            'notes': '',
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_1.sport_id,
            'suspended': True,
            'suspended_at': workout_cycling_user_1.suspended_at,
            'suspension': workout_cycling_user_1.suspension_action.serialize(  # type: ignore # noqa
                current_user=user_1, full=False
            ),
            'title': None,
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_1.workout_date,
            'workout_visibility': (
                workout_cycling_user_1.workout_visibility.value
            ),
            'with_gpx': False,
        }

    def test_workout_segment_model(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: Workout,
    ) -> None:
        assert (
            f'<Segment \'{workout_cycling_user_1_segment.segment_id}\' '
            f'for workout \'{workout_cycling_user_1.short_id}\'>'
            == str(workout_cycling_user_1_segment)
        )

    def test_it_returns_previous_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        serialized_workout = workout_running_user_1.serialize(
            user=user_1, light=False
        )

        assert (
            serialized_workout['previous_workout']
            == workout_cycling_user_1.short_id
        )

    def test_it_returns_next_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        serialized_workout = workout_cycling_user_1.serialize(
            user=user_1, light=False
        )

        assert (
            serialized_workout['next_workout']
            == workout_running_user_1.short_id
        )

    def test_it_returns_equipments(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_1, light=False
        )

        assert serialized_workout['equipments'] == [
            equipment_bike_user_1.serialize()
        ]

    def test_it_raises_exception_when_workout_is_deleted_before_removing_equipment(  # noqa
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        db.session.commit()

        db.session.delete(workout_cycling_user_1)
        with pytest.raises(
            Exception, match="equipments exists, remove them first"
        ):
            db.session.commit()

        equipment_bike_user_1.total_workouts = 1

    def test_it_updates_equipments_totals(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        workout_running_user_1.equipments = [equipment_shoes_user_1]
        db.session.commit()

        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()
        assert equipment_bike_user_1.total_workouts == 0
        assert (
            equipment_shoes_user_1.total_distance
            == workout_running_user_1.distance
        )
        assert (
            equipment_shoes_user_1.total_duration
            == workout_running_user_1.duration
        )
        assert (
            equipment_shoes_user_1.total_moving
            == workout_running_user_1.moving
        )
        assert equipment_shoes_user_1.total_workouts == 1

        all_equipments = [equipment_bike_user_1, equipment_shoes_user_1]
        workout_cycling_user_1.equipments = all_equipments
        db.session.commit()

        assert (
            equipment_bike_user_1.total_distance
            == workout_cycling_user_1.distance
        )
        assert (
            equipment_bike_user_1.total_duration
            == workout_cycling_user_1.duration
        )
        assert (
            equipment_bike_user_1.total_moving == workout_cycling_user_1.moving
        )
        assert equipment_bike_user_1.total_workouts == 1
        assert equipment_shoes_user_1.total_distance == (
            workout_running_user_1.distance + workout_cycling_user_1.distance
        )
        assert equipment_shoes_user_1.total_duration == (
            workout_running_user_1.duration + workout_cycling_user_1.duration
        )
        assert equipment_shoes_user_1.total_moving == (
            workout_running_user_1.moving + workout_cycling_user_1.moving
        )
        assert equipment_shoes_user_1.total_workouts == 2

        workout_running_user_1.equipments = []
        db.session.commit()

        for equipment in all_equipments:
            assert equipment.total_distance == workout_cycling_user_1.distance
            assert equipment.total_duration == workout_cycling_user_1.duration
            assert equipment.total_moving == workout_cycling_user_1.moving
            assert equipment.total_workouts == 1

        workout_cycling_user_1.equipments = []
        db.session.commit()

        for equipment in all_equipments:
            assert equipment.total_distance == 0.0
            assert equipment.total_duration == timedelta()
            assert equipment.total_moving == timedelta()
            assert equipment.total_workouts == 0

    def test_it_returns_likes_count(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        user_3: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        for user in [user_2, user_3]:
            like = WorkoutLike(
                user_id=user.id, workout_id=workout_cycling_user_1.id
            )
            db.session.add(like)
        db.session.commit()

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_1, light=False
        )

        assert serialized_workout['likes_count'] == 2

    def test_it_returns_if_workout_is_not_liked_by_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_1, light=False
        )

        assert serialized_workout['liked'] is False

    def test_it_returns_if_workout_is_liked_by_user(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_1, light=False
        )

        assert serialized_workout['liked'] is True


class TestWorkoutModelAsFollower(CommentMixin, WorkoutModelTestCase):
    def test_it_raises_exception_when_workout_visibility_is_private(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PRIVATE
        add_follower(user_1, user_2)

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(user=user_2, light=False)

    def test_serializer_does_not_return_notes(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.notes = random_string()
        workout_cycling_user_1.workout_visibility = VisibilityLevel.FOLLOWERS
        add_follower(user_1, user_2)
        serialized_workout = workout_cycling_user_1.serialize(
            user=user_2, light=False
        )

        assert serialized_workout['notes'] is None

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.FOLLOWERS,
            ),
            (
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.PUBLIC,
            ),
            (
                VisibilityLevel.PUBLIC,
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_serializer_returns_map_related_data(
        self,
        input_map_visibility: VisibilityLevel,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        add_follower(user_1, user_2)
        workout = self.update_workout(
            workout_cycling_user_1, map_id=random_string()
        )

        serialized_workout = workout.serialize(user=user_2, light=False)

        assert serialized_workout['map'] == workout.map
        assert serialized_workout['bounds'] == workout.bounds
        assert serialized_workout['with_gpx'] is True
        assert serialized_workout['map_visibility'] == input_map_visibility
        assert (
            serialized_workout['workout_visibility']
            == input_workout_visibility
        )
        assert serialized_workout['segments'] == []

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (
                VisibilityLevel.PRIVATE,
                VisibilityLevel.FOLLOWERS,
            ),
            (
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_serializer_does_not_return_map_related_data(
        self,
        input_map_visibility: VisibilityLevel,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        add_follower(user_1, user_2)
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user=user_2, light=False)

        assert serialized_workout['map'] is None
        assert serialized_workout['bounds'] == []
        assert serialized_workout['with_gpx'] is False
        assert serialized_workout['map_visibility'] == input_map_visibility
        assert (
            serialized_workout['workout_visibility']
            == input_workout_visibility
        )
        assert serialized_workout['segments'] == []

    def test_serializer_does_not_return_next_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.FOLLOWERS
        add_follower(user_1, user_2)
        serialized_workout = workout_cycling_user_1.serialize(
            user=user_2, light=False
        )

        assert serialized_workout['next_workout'] is None

    def test_serializer_does_not_return_previous_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.workout_visibility = VisibilityLevel.FOLLOWERS
        add_follower(user_1, user_2)

        serialized_workout = workout_running_user_1.serialize(
            user=user_2, light=False
        )

        assert serialized_workout['previous_workout'] is None

    def test_serializer_does_not_return_suspended_at(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.FOLLOWERS
        add_follower(user_1, user_2)

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_2, light=False
        )

        assert 'suspended_at' not in serialized_workout

    @pytest.mark.parametrize(
        "input_workout_visibility",
        [VisibilityLevel.FOLLOWERS, VisibilityLevel.PUBLIC],
    )
    @pytest.mark.parametrize("input_for_report", [True, False])
    def test_it_raises_exception_when_workout_is_suspended(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        user_3: User,
        workout_cycling_user_1: Workout,
        input_workout_visibility: VisibilityLevel,
        input_for_report: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        add_follower(user_1, user_2)
        add_follower(user_1, user_3)
        self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        workout_cycling_user_1.suspended_at = datetime.utcnow()

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(
                user=user_2, for_report=input_for_report, light=False
            )

    def test_serialize_returns_suspended_workout_when_user_commented_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2_admin: User,
        user_3: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.FOLLOWERS
        add_follower(user_1, user_3)
        self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        self.create_report_workout_action(
            user_2_admin, user_1, workout_cycling_user_1
        )
        workout_cycling_user_1.suspended_at = datetime.utcnow()

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_3, light=False
        )

        assert serialized_workout == {
            'ascent': None,
            'bounds': [],
            'creation_date': None,
            'descent': None,
            'distance': None,
            'duration': None,
            'equipments': [],
            'id': workout_cycling_user_1.short_id,
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': None,
            'max_alt': None,
            'min_alt': None,
            'modification_date': None,
            'moving': None,
            'next_workout': None,
            'notes': '',
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_1.sport_id,
            'suspended': True,
            'title': '',
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'with_gpx': False,
            'workout_date': workout_cycling_user_1.workout_date,
            'workout_visibility': (
                workout_cycling_user_1.workout_visibility.value
            ),
        }

    def test_serializer_does_not_return_equipments(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.FOLLOWERS
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        add_follower(user_1, user_2)

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_2, light=False
        )

        assert serialized_workout["equipments"] == []

    def test_it_serializes_minimal_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2_admin: User,
        user_3: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.FOLLOWERS
        add_follower(user_1, user_3)
        self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_3, light=True
        )

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_1.ave_speed),
            'bounds': [],
            'creation_date': None,
            'descent': None,
            'distance': float(workout_cycling_user_1.distance),
            'duration': str(workout_cycling_user_1.duration),
            'id': workout_cycling_user_1.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout_cycling_user_1.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_1.max_speed),
            'min_alt': None,
            'modification_date': None,
            'moving': str(workout_cycling_user_1.moving),
            'next_workout': None,
            'notes': '',
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_1.sport_id,
            'suspended': False,
            'title': None,
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_1.workout_date,
            'workout_visibility': (
                workout_cycling_user_1.workout_visibility.value
            ),
            'with_gpx': False,
        }


class TestWorkoutModelAsUser(CommentMixin, WorkoutModelTestCase):
    @pytest.mark.parametrize(
        'input_desc, input_workout_visibility',
        [
            ('visibility: follower', VisibilityLevel.FOLLOWERS),
            ('visibility: private', VisibilityLevel.PRIVATE),
        ],
    )
    def test_it_raises_exception_when_workout_visibility_is_not_public(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(user=user_2, light=False)

    def test_serializer_does_not_return_notes(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.notes = random_string()
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_2, light=False
        )

        assert serialized_workout['notes'] is None

    def test_serializer_returns_map_related_data_when_visibility_is_public(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.map_visibility = VisibilityLevel.PUBLIC
        workout = self.update_workout(
            workout_cycling_user_1, map_id=random_string()
        )

        serialized_workout = workout.serialize(user=user_2, light=False)

        assert serialized_workout['map'] == workout.map
        assert serialized_workout['bounds'] == workout.bounds
        assert serialized_workout['with_gpx'] is True
        assert serialized_workout['map_visibility'] == VisibilityLevel.PUBLIC
        assert (
            serialized_workout['workout_visibility'] == VisibilityLevel.PUBLIC
        )
        assert serialized_workout['segments'] == []

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PUBLIC,
            ),
            (
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_serializer_does_not_return_map_related_data(
        self,
        input_map_visibility: VisibilityLevel,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user=user_2, light=False)

        assert serialized_workout['map'] is None
        assert serialized_workout['bounds'] == []
        assert serialized_workout['with_gpx'] is False
        assert serialized_workout['map_visibility'] == input_map_visibility
        assert (
            serialized_workout['workout_visibility']
            == input_workout_visibility
        )
        assert serialized_workout['segments'] == []

    def test_serializer_does_not_return_next_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_2, light=False
        )

        assert serialized_workout['next_workout'] is None

    def test_serializer_does_not_return_previous_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.workout_visibility = VisibilityLevel.PUBLIC

        serialized_workout = workout_running_user_1.serialize(
            user=user_2, light=False
        )

        assert serialized_workout['previous_workout'] is None

    def test_serializer_does_not_return_suspended_at(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_2, light=False
        )

        assert 'suspended_at' not in serialized_workout

    @pytest.mark.parametrize("input_for_report", [True, False])
    def test_it_raises_exception_when_workout_is_suspended(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        user_3: User,
        workout_cycling_user_1: Workout,
        input_for_report: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.suspended_at = datetime.utcnow()
        self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(
                user=user_2, for_report=input_for_report, light=False
            )

    def test_serialize_returns_suspended_workout_when_user_commented_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2_admin: User,
        user_3: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        self.create_report_workout_action(
            user_2_admin, user_1, workout_cycling_user_1
        )
        workout_cycling_user_1.suspended_at = datetime.utcnow()

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_3, light=False
        )

        assert serialized_workout == {
            'ascent': None,
            'bounds': [],
            'creation_date': None,
            'descent': None,
            'distance': None,
            'duration': None,
            'equipments': [],
            'id': workout_cycling_user_1.short_id,
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': None,
            'max_alt': None,
            'min_alt': None,
            'modification_date': None,
            'moving': None,
            'next_workout': None,
            'notes': '',
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_1.sport_id,
            'suspended': True,
            'title': '',
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'with_gpx': False,
            'workout_date': workout_cycling_user_1.workout_date,
            'workout_visibility': workout_cycling_user_1.workout_visibility,
        }

    def test_serializer_does_not_return_equipments(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.equipments = [equipment_bike_user_1]

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_2, light=False
        )

        assert serialized_workout["equipments"] == []

    def test_it_serializes_minimal_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2_admin: User,
        user_3: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )

        serialized_workout = workout_cycling_user_1.serialize(
            user=user_3, light=True
        )

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_1.ave_speed),
            'bounds': [],
            'creation_date': None,
            'descent': None,
            'distance': float(workout_cycling_user_1.distance),
            'duration': str(workout_cycling_user_1.duration),
            'id': workout_cycling_user_1.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout_cycling_user_1.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_1.max_speed),
            'min_alt': None,
            'modification_date': None,
            'moving': str(workout_cycling_user_1.moving),
            'next_workout': None,
            'notes': '',
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_1.sport_id,
            'suspended': False,
            'title': None,
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_1.workout_date,
            'workout_visibility': (
                workout_cycling_user_1.workout_visibility.value
            ),
            'with_gpx': False,
        }


class TestWorkoutModelAsUnauthenticatedUser(
    CommentMixin, WorkoutModelTestCase
):
    @pytest.mark.parametrize(
        'input_desc, input_workout_visibility',
        [
            ('visibility: follower', VisibilityLevel.FOLLOWERS),
            ('visibility: private', VisibilityLevel.PRIVATE),
        ],
    )
    def test_it_raises_exception_when_workout_visibility_is_not_public(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize()

    def test_serializer_does_not_return_notes(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.notes = random_string()
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize(light=False)

        assert serialized_workout['notes'] is None

    def test_serializer_returns_map_related_data_when_visibility_is_public(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.map_visibility = VisibilityLevel.PUBLIC
        workout = self.update_workout(
            workout_cycling_user_1, map_id=random_string()
        )

        serialized_workout = workout.serialize(light=False)

        assert serialized_workout['map'] == workout.map
        assert serialized_workout['bounds'] == workout.bounds
        assert serialized_workout['with_gpx'] is True
        assert serialized_workout['map_visibility'] == VisibilityLevel.PUBLIC
        assert (
            serialized_workout['workout_visibility'] == VisibilityLevel.PUBLIC
        )
        assert serialized_workout['segments'] == []

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PUBLIC,
            ),
            (
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_serializer_does_not_return_map_related_data(
        self,
        input_map_visibility: VisibilityLevel,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize()

        assert serialized_workout['map'] is None
        assert serialized_workout['bounds'] == []
        assert serialized_workout['with_gpx'] is False
        assert serialized_workout['map_visibility'] == input_map_visibility
        assert (
            serialized_workout['workout_visibility']
            == input_workout_visibility
        )
        assert serialized_workout['segments'] == []

    def test_serializer_does_not_return_next_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize()

        assert serialized_workout['next_workout'] is None

    def test_serializer_does_not_return_previous_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.workout_visibility = VisibilityLevel.PUBLIC

        serialized_workout = workout_running_user_1.serialize()

        assert serialized_workout['previous_workout'] is None

    def test_it_returns_likes_count(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()

        serialized_workout = workout_cycling_user_1.serialize(light=False)

        assert serialized_workout['liked'] is False
        assert serialized_workout['likes_count'] == 1

    def test_serializer_does_not_return_suspended_at(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize()

        assert 'suspended_at' not in serialized_workout

    @pytest.mark.parametrize("input_for_report", [True, False])
    def test_it_raises_exception_when_workout_is_suspended(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
        input_for_report: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        workout_cycling_user_1.suspended_at = datetime.utcnow()

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(for_report=input_for_report)

    def test_serializer_does_not_return_equipments(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.equipments = [equipment_bike_user_1]

        serialized_workout = workout_cycling_user_1.serialize(light=False)

        assert serialized_workout["equipments"] == []

    def test_it_serializes_minimal_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2_admin: User,
        user_3: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )

        serialized_workout = workout_cycling_user_1.serialize(light=True)

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_1.ave_speed),
            'bounds': [],
            'creation_date': None,
            'descent': None,
            'distance': float(workout_cycling_user_1.distance),
            'duration': str(workout_cycling_user_1.duration),
            'id': workout_cycling_user_1.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout_cycling_user_1.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_1.max_speed),
            'min_alt': None,
            'modification_date': None,
            'moving': str(workout_cycling_user_1.moving),
            'next_workout': None,
            'notes': '',
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_1.sport_id,
            'suspended': False,
            'title': None,
            'user': user_1.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_1.workout_date,
            'workout_visibility': (
                workout_cycling_user_1.workout_visibility.value
            ),
            'with_gpx': False,
        }


class TestWorkoutModelAsModerator(WorkoutModelTestCase):
    @pytest.mark.parametrize(
        'input_desc, input_workout_visibility',
        [
            ('visibility: follower', VisibilityLevel.FOLLOWERS),
            ('visibility: private', VisibilityLevel.PRIVATE),
        ],
    )
    def test_it_raises_exception_when_workout_is_not_visible(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_moderator: User,
        user_2: User,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_2.serialize(
                user=user_1_moderator, light=False
            )

    @pytest.mark.parametrize(
        'input_desc, input_workout_visibility',
        [
            ('visibility: follower', VisibilityLevel.FOLLOWERS),
            ('visibility: private', VisibilityLevel.PRIVATE),
        ],
    )
    def test_it_returns_workout_when_report_flag_is_true(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_moderator: User,
        user_2: User,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility

        serialized_workout = workout_cycling_user_2.serialize(
            user=user_1_moderator, for_report=True, light=False
        )

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_2.ave_speed),
            'bounds': [],
            'creation_date': workout_cycling_user_2.creation_date,
            'descent': None,
            'description': None,
            'distance': float(workout_cycling_user_2.distance),
            'duration': str(workout_cycling_user_2.duration),
            'id': workout_cycling_user_2.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout_cycling_user_2.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_2.max_speed),
            'min_alt': None,
            'modification_date': workout_cycling_user_2.modification_date,
            'moving': str(workout_cycling_user_2.moving),
            'next_workout': None,
            'notes': None,
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_2.sport_id,
            'suspended': False,
            'suspended_at': None,
            'title': None,
            'user': user_2.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_2.workout_date,
            'workout_visibility': (
                workout_cycling_user_2.workout_visibility.value
            ),
            'with_gpx': False,
        }

    @pytest.mark.parametrize(
        'input_desc, input_workout_visibility',
        [
            ('visibility: follower', VisibilityLevel.FOLLOWERS),
            ('visibility: private', VisibilityLevel.PRIVATE),
        ],
    )
    def test_it_returns_workout_with_map_when_report_flag_is_true(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_moderator: User,
        user_2: User,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.map_visibility = input_workout_visibility
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        map_id = random_string()
        workout_cycling_user_2 = self.update_workout(
            workout_cycling_user_2, map_id=map_id
        )

        serialized_workout = workout_cycling_user_2.serialize(
            user=user_1_moderator, for_report=True, light=False
        )

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_2.ave_speed),
            'bounds': workout_cycling_user_2.bounds,
            'creation_date': workout_cycling_user_2.creation_date,
            'descent': None,
            'description': None,
            'distance': float(workout_cycling_user_2.distance),
            'duration': str(workout_cycling_user_2.duration),
            'id': workout_cycling_user_2.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': map_id,
            'map_visibility': workout_cycling_user_2.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_2.max_speed),
            'min_alt': None,
            'modification_date': workout_cycling_user_2.modification_date,
            'moving': str(workout_cycling_user_2.moving),
            'next_workout': None,
            'notes': None,
            'pauses': str(workout_cycling_user_2.pauses),
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_2.sport_id,
            'suspended': False,
            'suspended_at': None,
            'title': None,
            'user': user_2.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_2.workout_date,
            'workout_visibility': (
                workout_cycling_user_2.workout_visibility.value
            ),
            'with_gpx': True,
        }

    @pytest.mark.parametrize(
        "input_workout_visibility",
        [
            VisibilityLevel.PRIVATE,
            VisibilityLevel.FOLLOWERS,
            VisibilityLevel.PUBLIC,
        ],
    )
    def test_it_raises_exception_when_workout_is_suspended(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_moderator: User,
        user_2: User,
        workout_cycling_user_2: Workout,
        input_workout_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        workout_cycling_user_2.suspended_at = datetime.utcnow()

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_2.serialize(
                user=user_1_moderator, light=False
            )

    @pytest.mark.parametrize(
        "input_workout_visibility",
        [
            VisibilityLevel.PRIVATE,
            VisibilityLevel.FOLLOWERS,
            VisibilityLevel.PUBLIC,
        ],
    )
    def test_it_serializes_suspended_workout_for_report(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_moderator: User,
        user_2: User,
        workout_cycling_user_2: Workout,
        input_workout_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        expected_report_action = self.create_report_workout_action(
            user_1_moderator, user_2, workout_cycling_user_2
        )

        serialized_workout = workout_cycling_user_2.serialize(
            user=user_1_moderator, for_report=True, light=False
        )

        assert (
            serialized_workout["suspended_at"]
            == workout_cycling_user_2.suspended_at
        )
        assert serialized_workout[
            "suspension"
        ] == expected_report_action.serialize(
            current_user=user_1_moderator,  # type: ignore
            full=False,
        )

    def test_it_serializes_minimal_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_moderator: User,
        user_2: User,
        workout_cycling_user_2: Workout,
    ) -> None:
        serialized_workout = workout_cycling_user_2.serialize(
            user=user_1_moderator, for_report=True, light=True
        )

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_2.ave_speed),
            'bounds': [],
            'creation_date': None,
            'descent': None,
            'distance': float(workout_cycling_user_2.distance),
            'duration': str(workout_cycling_user_2.duration),
            'id': workout_cycling_user_2.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout_cycling_user_2.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_2.max_speed),
            'min_alt': None,
            'modification_date': None,
            'moving': str(workout_cycling_user_2.moving),
            'next_workout': None,
            'notes': '',
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_2.sport_id,
            'suspended': False,
            'suspended_at': None,
            'title': None,
            'user': user_2.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_2.workout_date,
            'workout_visibility': (
                workout_cycling_user_2.workout_visibility.value
            ),
            'with_gpx': False,
        }


class TestWorkoutModelAsAdmin(WorkoutModelTestCase):
    def test_it_raises_exception_when_workout_is_not_visible(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_admin: User,
        user_2: User,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_2.serialize(user=user_1_admin, light=False)

    def test_it_returns_workout_when_report_flag_is_true(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_admin: User,
        user_2: User,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS

        serialized_workout = workout_cycling_user_2.serialize(
            user=user_1_admin, for_report=True, light=False
        )

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_2.ave_speed),
            'bounds': [],
            'creation_date': workout_cycling_user_2.creation_date,
            'descent': None,
            'description': None,
            'distance': float(workout_cycling_user_2.distance),
            'duration': str(workout_cycling_user_2.duration),
            'id': workout_cycling_user_2.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': None,
            'map_visibility': workout_cycling_user_2.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_2.max_speed),
            'min_alt': None,
            'modification_date': workout_cycling_user_2.modification_date,
            'moving': str(workout_cycling_user_2.moving),
            'next_workout': None,
            'notes': None,
            'pauses': None,
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_2.sport_id,
            'suspended': False,
            'suspended_at': None,
            'title': None,
            'user': user_2.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_2.workout_date,
            'workout_visibility': (
                workout_cycling_user_2.workout_visibility.value
            ),
            'with_gpx': False,
        }

    def test_it_returns_workout_with_map_when_report_flag_is_true(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_admin: User,
        user_2: User,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.map_visibility = VisibilityLevel.FOLLOWERS
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        map_id = random_string()
        workout_cycling_user_2 = self.update_workout(
            workout_cycling_user_2, map_id=map_id
        )

        serialized_workout = workout_cycling_user_2.serialize(
            user=user_1_admin, for_report=True, light=False
        )

        assert serialized_workout == {
            'ascent': None,
            'ave_speed': float(workout_cycling_user_2.ave_speed),
            'bounds': workout_cycling_user_2.bounds,
            'creation_date': workout_cycling_user_2.creation_date,
            'descent': None,
            'description': None,
            'distance': float(workout_cycling_user_2.distance),
            'duration': str(workout_cycling_user_2.duration),
            'id': workout_cycling_user_2.short_id,
            'equipments': [],
            'liked': False,
            'likes_count': 0,
            'map': map_id,
            'map_visibility': workout_cycling_user_2.map_visibility.value,
            'max_alt': None,
            'max_speed': float(workout_cycling_user_2.max_speed),
            'min_alt': None,
            'modification_date': workout_cycling_user_2.modification_date,
            'moving': str(workout_cycling_user_2.moving),
            'next_workout': None,
            'notes': None,
            'pauses': str(workout_cycling_user_2.pauses),
            'previous_workout': None,
            'records': [],
            'segments': [],
            'sport_id': workout_cycling_user_2.sport_id,
            'suspended': False,
            'suspended_at': None,
            'title': None,
            'user': user_2.serialize(),
            'weather_end': None,
            'weather_start': None,
            'workout_date': workout_cycling_user_2.workout_date,
            'workout_visibility': (
                workout_cycling_user_2.workout_visibility.value
            ),
            'with_gpx': True,
        }


class TestWorkoutModelGetActivity:
    def test_it_raises_error_if_federation_is_disabled(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        with pytest.raises(FederationDisabledException):
            workout_cycling_user_1.get_activities(activity_type='Create')
