from datetime import datetime, timedelta
from statistics import mean
from typing import List, Union

import pytest
import pytz
from flask import Flask
from gpxpy.gpxfield import SimpleTZ

from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout
from fittrackee.workouts.utils.workouts import (
    create_segment,
    get_average_speed,
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
    def test_it_returns_naive_datetime(
        self, input_workout_date: Union[datetime, str]
    ) -> None:
        naive_workout_date, _ = get_workout_datetime(
            workout_date=input_workout_date, user_timezone='Europe/Paris'
        )

        assert naive_workout_date == datetime(
            year=2022, month=6, day=11, hour=10, minute=23, second=00
        )

    def test_it_return_naive_datetime_when_no_user_timezone(self) -> None:
        naive_workout_date, _ = get_workout_datetime(
            workout_date='2022-06-11 12:23:00', user_timezone=None
        )

        assert naive_workout_date == datetime(
            year=2022, month=6, day=11, hour=12, minute=23, second=00
        )

    @pytest.mark.parametrize('input_workout_date', input_workout_dates)
    def test_it_returns_datetime_with_user_timezone(
        self, input_workout_date: Union[datetime, str]
    ) -> None:
        timezone = 'Europe/Paris'

        _, workout_date_with_tz = get_workout_datetime(
            input_workout_date, user_timezone=timezone, with_timezone=True
        )

        assert workout_date_with_tz == datetime(
            year=2022,
            month=6,
            day=11,
            hour=10,
            minute=23,
            second=00,
            tzinfo=pytz.utc,
        ).astimezone(pytz.timezone(timezone))

    def test_it_does_not_return_datetime_with_user_timezone_when_no_user_tz(
        self,
    ) -> None:
        _, workout_date_with_tz = get_workout_datetime(
            workout_date='2022-06-11 12:23:00',
            user_timezone=None,
            with_timezone=True,
        )

        assert workout_date_with_tz is None

    def test_it_does_not_return_datetime_with_user_timezone_when_with_timezone_to_false(  # noqa
        self,
    ) -> None:
        _, workout_date_with_tz = get_workout_datetime(
            workout_date='2022-06-11 12:23:00',
            user_timezone='Europe/Paris',
            with_timezone=False,
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
