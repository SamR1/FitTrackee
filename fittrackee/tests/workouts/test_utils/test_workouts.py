from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import List, Optional, Union

import pytest
import pytz
from flask import Flask
from gpxpy.gpxfield import SimpleTZ

from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import Sport, Workout
from fittrackee.workouts.utils.workouts import (
    create_segment,
    get_average_speed,
    get_ordered_workouts,
    get_workout,
    get_workout_datetime,
)

utc_datetime = datetime(
    year=2022, month=6, day=11, hour=10, minute=23, second=00, tzinfo=pytz.utc
)
input_workout_dates = [
    utc_datetime,
    utc_datetime.replace(tzinfo=None),
    utc_datetime.replace(tzinfo=SimpleTZ('Z')),
    utc_datetime.astimezone(pytz.timezone('Europe/Paris')),
    utc_datetime.astimezone(pytz.timezone('America/Toronto')),
    '2022-06-11 12:23:00',
]


class TestWorkoutAverageSpeed:
    @pytest.mark.parametrize(
        'ave_speeds_list',
        [
            ([0]),
            ([10]),
            ([0, 0]),
            ([10, 20]),
            ([10, 0, 20, 10]),
            ([1.5, 2, 3.7, 4.2]),
        ],
    )
    def test_it_calculates_average_speed(self, ave_speeds_list: List) -> None:
        nb_workouts = len(ave_speeds_list)
        total_average_speed = (
            sum(ave_speeds_list[:-1]) / (len(ave_speeds_list) - 1)
            if len(ave_speeds_list) > 1
            else ave_speeds_list[0]
        )
        workout_average_speed = ave_speeds_list[-1]

        assert get_average_speed(
            nb_workouts, total_average_speed, workout_average_speed
        ) == mean(ave_speeds_list)


class TestWorkoutGetWorkoutDatetime:
    @pytest.mark.parametrize('input_workout_date', input_workout_dates)
    def test_it_returns_datetime_in_utc(
        self, input_workout_date: Union[datetime, str]
    ) -> None:
        workout_date, _ = get_workout_datetime(
            workout_date=input_workout_date, user_timezone='Europe/Paris'
        )

        assert workout_date == datetime(
            year=2022,
            month=6,
            day=11,
            hour=10,
            minute=23,
            second=00,
            tzinfo=timezone.utc,
        )

    def test_it_return_datetime_in_utc_when_no_user_timezone(self) -> None:
        workout_date, _ = get_workout_datetime(
            workout_date='2022-06-11 12:23:00', user_timezone=None
        )

        assert workout_date == datetime(
            year=2022,
            month=6,
            day=11,
            hour=12,
            minute=23,
            second=00,
            tzinfo=timezone.utc,
        )

    @pytest.mark.parametrize('input_workout_date', input_workout_dates)
    def test_it_returns_datetime_with_user_timezone(
        self, input_workout_date: Union[datetime, str]
    ) -> None:
        user_timezone = 'Europe/Paris'

        _, workout_date_with_tz = get_workout_datetime(
            input_workout_date,
            user_timezone=user_timezone,
            with_user_timezone=True,
        )

        assert workout_date_with_tz == datetime(
            year=2022,
            month=6,
            day=11,
            hour=10,
            minute=23,
            second=00,
            tzinfo=pytz.utc,
        ).astimezone(pytz.timezone(user_timezone))

    def test_it_does_not_return_datetime_with_user_timezone_when_no_user_tz(
        self,
    ) -> None:
        _, workout_date_with_tz = get_workout_datetime(
            workout_date='2022-06-11 12:23:00',
            user_timezone=None,
            with_user_timezone=True,
        )

        assert workout_date_with_tz is None

    def test_it_does_not_return_datetime_with_user_timezone_when_with_timezone_to_false(  # noqa
        self,
    ) -> None:
        _, workout_date_with_tz = get_workout_datetime(
            workout_date='2022-06-11 12:23:00',
            user_timezone='Europe/Paris',
            with_user_timezone=False,
        )

        assert workout_date_with_tz is None


class TestCreateSegment:
    def test_it_removes_microseconds(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        duration = timedelta(seconds=3600, microseconds=100)

        segment = create_segment(
            workout_id=workout_cycling_user_1.id,
            workout_uuid=workout_cycling_user_1.uuid,
            segment_data={
                'idx': 0,
                'duration': duration,
                'distance': 10,
                'stop_time': timedelta(seconds=0),
                'moving_time': duration,
                'elevation_min': None,
                'elevation_max': None,
                'downhill': None,
                'uphill': None,
                'max_speed': 10,
                'average_speed': 10,
            },
        )

        assert segment.duration.microseconds == 0


class TestGetOrderedWorkouts:
    def test_it_returns_empty_list_when_no_workouts_provided(
        self,
        app: Flask,
    ) -> None:
        ordered_workouts = get_ordered_workouts([])

        assert ordered_workouts == []

    def test_it_returns_workouts_ordered_by_workout_date_descending(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        ordered_workouts = get_ordered_workouts(seven_workouts_user_1)

        assert ordered_workouts == [
            seven_workouts_user_1[6],
            seven_workouts_user_1[5],
            seven_workouts_user_1[3],
            seven_workouts_user_1[4],
            seven_workouts_user_1[2],
            seven_workouts_user_1[1],
            seven_workouts_user_1[0],
        ]


class GetWorkoutTestCase:
    @staticmethod
    def assert_workout_is_returned(
        workout: Workout, user: Optional[User], allow_admin: bool
    ) -> None:
        workout = get_workout(
            workout_short_id=workout.short_id,
            auth_user=user,
            allow_admin=allow_admin,
        )

        assert workout.id == workout.id

    @staticmethod
    def assert_raises_forbidden_exception(
        workout: Workout, user: Optional[User], allow_admin: bool
    ) -> None:
        with pytest.raises(WorkoutForbiddenException):
            get_workout(
                workout_short_id=workout.short_id,
                auth_user=user,
                allow_admin=allow_admin,
            )


class TestGetWorkoutForPublicWorkout(GetWorkoutTestCase):
    visibility_level = VisibilityLevel.PUBLIC

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_returns_workout_when_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_workout_is_returned(
            workout_cycling_user_1, None, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_returns_workout_when_user_is_not_a_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_workout_is_returned(
            workout_cycling_user_1, user_2, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_returns_workout_when_user_is_a_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
        input_allow_admin: bool,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_workout_is_returned(
            workout_cycling_user_1, user_2, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_returns_workout_when_user_is_owner(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_workout_is_returned(
            workout_cycling_user_1, user_1, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_raises_exception_when_user_is_blocked_by_owner(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        user_1.blocks_user(user_2)
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_raises_forbidden_exception(
            workout_cycling_user_1, user_2, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_returns_workout_when_user_has_admin_right(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_workout_is_returned(
            workout_cycling_user_1, user_2_admin, input_allow_admin
        )


class TestGetWorkoutForFollowerOnlyWorkout(GetWorkoutTestCase):
    visibility_level = VisibilityLevel.FOLLOWERS

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_raises_exception_when_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_raises_forbidden_exception(
            workout_cycling_user_1, None, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_raises_exception_when_user_is_not_a_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_raises_forbidden_exception(
            workout_cycling_user_1, user_2, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_returns_workout_when_user_is_a_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
        input_allow_admin: bool,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_workout_is_returned(
            workout_cycling_user_1, user_2, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_returns_workout_when_user_is_owner(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_workout_is_returned(
            workout_cycling_user_1, user_1, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_raises_exception_when_user_is_blocked_by_owner(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        user_1.blocks_user(user_2)
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_raises_forbidden_exception(
            workout_cycling_user_1, user_2, input_allow_admin
        )

    def test_it_raises_exception_when_user_has_admin_right_and_flag_is_false(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_raises_forbidden_exception(
            workout_cycling_user_1, user_2_admin, False
        )

    def test_it_returns_workout_when_user_has_admin_right_and_flag_is_true(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_workout_is_returned(
            workout_cycling_user_1, user_2_admin, True
        )


class TestGetWorkoutForPrivateWorkout(GetWorkoutTestCase):
    visibility_level = VisibilityLevel.PRIVATE

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_raises_exception_when_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_raises_forbidden_exception(
            workout_cycling_user_1, None, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_raises_exception_when_user_is_not_a_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_raises_forbidden_exception(
            workout_cycling_user_1, user_2, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_raises_exception_when_user_is_a_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
        input_allow_admin: bool,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_raises_forbidden_exception(
            workout_cycling_user_1, user_2, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_returns_workout_when_user_is_owner(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_workout_is_returned(
            workout_cycling_user_1, user_1, input_allow_admin
        )

    @pytest.mark.parametrize('input_allow_admin', [True, False])
    def test_it_raises_exception_when_user_is_blocked_by_owner(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_allow_admin: bool,
    ) -> None:
        user_1.blocks_user(user_2)
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_raises_forbidden_exception(
            workout_cycling_user_1, user_2, input_allow_admin
        )

    def test_it_raises_exception_when_user_has_admin_right_and_flag_is_false(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_raises_forbidden_exception(
            workout_cycling_user_1, user_2_admin, False
        )

    def test_it_returns_workout_when_user_has_admin_right_and_flag_is_true(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = self.visibility_level

        self.assert_workout_is_returned(
            workout_cycling_user_1, user_2_admin, True
        )
