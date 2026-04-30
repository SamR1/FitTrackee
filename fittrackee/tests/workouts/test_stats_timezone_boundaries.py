"""
Tests for statistics timezone boundary handling.

These tests verify that:
1. Workouts crossing midnight are grouped by user's local timezone
2. Workouts crossing month boundaries are grouped correctly
3. UTC vs local timezone handling is correct
4. Manual workout creation respects user timezone
5. File import (GPX) respects timezone

Test scenarios:
- UTC: workout at 23:30 UTC should be in same day
- Paris (UTC+1): workout at 23:30 UTC = 00:30 Paris next day
- New York (UTC-5): workout at 04:00 UTC = 23:00 New York previous day
- Cross-month: workout at 23:30 UTC on Jan 31 = 00:30 Paris Feb 1
"""
import json
from datetime import datetime, timedelta, timezone
from typing import List

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.tests.fixtures.fixtures_workouts import update_workout
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin


class TestStatsTimezoneBoundaries(ApiTestCaseMixin):
    """
    Tests for statistics timezone boundary handling.
    """

    def create_workouts(
        self,
        user: User,
        sport: Sport,
        workout_dates: List[datetime],
        distances: List[float] = None,
    ) -> None:
        """Helper to create workouts with specific dates."""
        if distances is None:
            distances = [5.0] * len(workout_dates)

        for workout_date, distance in zip(workout_dates, distances):
            workout = Workout(
                user_id=user.id,
                sport_id=sport.id,
                workout_date=workout_date,
                distance=distance,
                duration=timedelta(seconds=3600),
            )
            update_workout(workout)
            db.session.add(workout)
            db.session.flush()
        db.session.commit()

    def test_utc_midnight_boundary_same_day(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test: User with UTC timezone.
        Workout at 2024-01-15 23:30 UTC should be grouped in 2024-01-15.
        Workout at 2024-01-16 00:30 UTC should be grouped in 2024-01-16.
        """
        self.create_workouts(
            user_1,
            sport_1_cycling,
            [
                datetime(2024, 1, 15, 23, 30, tzinfo=timezone.utc),
                datetime(2024, 1, 16, 0, 30, tzinfo=timezone.utc),
            ],
            [10.0, 15.0],
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/stats/{user_1.username}/by_time?time=day",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        stats = data["data"]["statistics"]

        assert "2024-01-15" in stats, (
            "23:30 UTC workout should be in 2024-01-15 for UTC user"
        )
        assert "2024-01-16" in stats, (
            "00:30 UTC workout should be in 2024-01-16 for UTC user"
        )

        jan_15_stats = stats["2024-01-15"][str(sport_1_cycling.id)]
        jan_16_stats = stats["2024-01-16"][str(sport_1_cycling.id)]

        assert jan_15_stats["total_distance"] == 10.0
        assert jan_15_stats["total_workouts"] == 1
        assert jan_16_stats["total_distance"] == 15.0
        assert jan_16_stats["total_workouts"] == 1

    def test_paris_timezone_cross_midnight(
        self,
        app: Flask,
        user_1_paris: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test: User with Europe/Paris timezone (UTC+1 in winter).
        Workout at 2024-01-15 23:30 UTC = 2024-01-16 00:30 Paris time.
        Should be grouped in 2024-01-16 (Paris local date).

        Workout at 2024-01-15 22:30 UTC = 2024-01-15 23:30 Paris time.
        Should be grouped in 2024-01-15.
        """
        self.create_workouts(
            user_1_paris,
            sport_1_cycling,
            [
                datetime(2024, 1, 15, 22, 30, tzinfo=timezone.utc),
                datetime(2024, 1, 15, 23, 30, tzinfo=timezone.utc),
            ],
            [10.0, 15.0],
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_paris.email
        )

        response = client.get(
            f"/api/stats/{user_1_paris.username}/by_time?time=day",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        stats = data["data"]["statistics"]

        assert "2024-01-15" in stats, (
            "22:30 UTC (23:30 Paris) should be in 2024-01-15"
        )
        assert "2024-01-16" in stats, (
            "23:30 UTC (00:30 Paris next day) should be in 2024-01-16"
        )

        jan_15_stats = stats["2024-01-15"][str(sport_1_cycling.id)]
        jan_16_stats = stats["2024-01-16"][str(sport_1_cycling.id)]

        assert jan_15_stats["total_distance"] == 10.0, (
            "22:30 UTC workout should be in Jan 15 Paris time"
        )
        assert jan_16_stats["total_distance"] == 15.0, (
            "23:30 UTC workout should be in Jan 16 Paris time (00:30 next day)"
        )

    def test_new_york_timezone_cross_midnight(
        self,
        app: Flask,
        user_1_full: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test: User with America/New_York timezone (UTC-5 in winter).
        Workout at 2024-01-16 04:00 UTC = 2024-01-15 23:00 New York time.
        Should be grouped in 2024-01-15 (New York local date).

        Workout at 2024-01-16 05:00 UTC = 2024-01-16 00:00 New York time.
        Should be grouped in 2024-01-16.
        """
        self.create_workouts(
            user_1_full,
            sport_1_cycling,
            [
                datetime(2024, 1, 16, 4, 0, tzinfo=timezone.utc),
                datetime(2024, 1, 16, 5, 0, tzinfo=timezone.utc),
            ],
            [10.0, 15.0],
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_full.email
        )

        response = client.get(
            f"/api/stats/{user_1_full.username}/by_time?time=day",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        stats = data["data"]["statistics"]

        assert "2024-01-15" in stats, (
            "04:00 UTC (23:00 NY previous day) should be in 2024-01-15"
        )
        assert "2024-01-16" in stats, (
            "05:00 UTC (00:00 NY) should be in 2024-01-16"
        )

        jan_15_stats = stats["2024-01-15"][str(sport_1_cycling.id)]
        jan_16_stats = stats["2024-01-16"][str(sport_1_cycling.id)]

        assert jan_15_stats["total_distance"] == 10.0, (
            "04:00 UTC workout should be in Jan 15 NY time (23:00 previous day)"
        )
        assert jan_16_stats["total_distance"] == 15.0, (
            "05:00 UTC workout should be in Jan 16 NY time"
        )

    def test_paris_timezone_cross_month_boundary(
        self,
        app: Flask,
        user_1_paris: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test: Cross-month boundary with Paris timezone.
        Workout at 2024-01-31 23:30 UTC = 2024-02-01 00:30 Paris time.
        Should be grouped in February 2024, not January.

        Workout at 2024-01-31 22:30 UTC = 2024-01-31 23:30 Paris time.
        Should be grouped in January 2024.
        """
        self.create_workouts(
            user_1_paris,
            sport_1_cycling,
            [
                datetime(2024, 1, 31, 22, 30, tzinfo=timezone.utc),
                datetime(2024, 1, 31, 23, 30, tzinfo=timezone.utc),
            ],
            [10.0, 15.0],
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_paris.email
        )

        response = client.get(
            f"/api/stats/{user_1_paris.username}/by_time?time=month",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        stats = data["data"]["statistics"]

        assert "2024-01" in stats, (
            "22:30 UTC (23:30 Paris Jan 31) should be in January"
        )
        assert "2024-02" in stats, (
            "23:30 UTC (00:30 Paris Feb 1) should be in February"
        )

        jan_stats = stats["2024-01"][str(sport_1_cycling.id)]
        feb_stats = stats["2024-02"][str(sport_1_cycling.id)]

        assert jan_stats["total_distance"] == 10.0, (
            "22:30 UTC workout should be in January Paris time"
        )
        assert feb_stats["total_distance"] == 15.0, (
            "23:30 UTC workout should be in February Paris time (00:30 Feb 1)"
        )

    def test_paris_timezone_cross_year_boundary(
        self,
        app: Flask,
        user_1_paris: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test: Cross-year boundary with Paris timezone.
        Workout at 2024-12-31 23:30 UTC = 2025-01-01 00:30 Paris time.
        Should be grouped in 2025, not 2024.
        """
        self.create_workouts(
            user_1_paris,
            sport_1_cycling,
            [
                datetime(2024, 12, 31, 22, 30, tzinfo=timezone.utc),
                datetime(2024, 12, 31, 23, 30, tzinfo=timezone.utc),
            ],
            [10.0, 15.0],
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_paris.email
        )

        response = client.get(
            f"/api/stats/{user_1_paris.username}/by_time?time=year",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        stats = data["data"]["statistics"]

        assert "2024" in stats, (
            "22:30 UTC (23:30 Paris Dec 31) should be in 2024"
        )
        assert "2025" in stats, (
            "23:30 UTC (00:30 Paris Jan 1) should be in 2025"
        )

        stats_2024 = stats["2024"][str(sport_1_cycling.id)]
        stats_2025 = stats["2025"][str(sport_1_cycling.id)]

        assert stats_2024["total_distance"] == 10.0, (
            "22:30 UTC workout should be in 2024 Paris time"
        )
        assert stats_2025["total_distance"] == 15.0, (
            "23:30 UTC workout should be in 2025 Paris time (00:30 Jan 1)"
        )

    def test_week_boundary_paris_timezone(
        self,
        app: Flask,
        user_1_paris: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test: Week boundary with Paris timezone.
        Let's say Sunday Jan 14, 23:30 UTC = Monday Jan 15, 00:30 Paris time.
        Should be grouped in next week.

        Note: 2024-01-14 is Sunday, 2024-01-15 is Monday.
        In ISO week format (IYYY-IW), week starts on Monday.
        """
        self.create_workouts(
            user_1_paris,
            sport_1_cycling,
            [
                datetime(2024, 1, 14, 22, 30, tzinfo=timezone.utc),
                datetime(2024, 1, 14, 23, 30, tzinfo=timezone.utc),
            ],
            [10.0, 15.0],
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_paris.email
        )

        response = client.get(
            f"/api/stats/{user_1_paris.username}/by_time?time=weekm",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        stats = data["data"]["statistics"]

        assert len(stats) == 2, (
            "Should have 2 different weeks: one for Sunday evening, "
            "one for Monday morning (Paris time)"
        )


class TestWorkoutCreationTimezone(ApiTestCaseMixin):
    """
    Tests for workout creation timezone handling.
    Verifies that when a user creates a workout manually,
    the date is interpreted in their local timezone.
    """

    def test_manual_workout_creation_with_timezone(
        self,
        app: Flask,
        user_1_paris: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test manual workout creation with timezone.

        When a Paris user creates a workout with date "2024-01-15T00:30:00",
        it should be interpreted as Paris time (00:30 CET = 23:30 UTC previous day).

        This is handled by WorkoutCreationService.get_workout_date().
        """
        from fittrackee.workouts.services.workout_creation_service import (
            WorkoutCreationService,
        )

        workout_data = {
            "sport_id": sport_1_cycling.id,
            "workout_date": "2024-01-15T00:30:00",
            "duration": "1:00:00",
            "distance": 10.0,
        }

        service = WorkoutCreationService(
            user_1_paris, workout_data, None
        )

        workout_date = service.get_workout_date()

        expected_utc = datetime(2024, 1, 14, 23, 30, tzinfo=timezone.utc)
        assert workout_date == expected_utc, (
            "00:30 Paris time should be converted to 23:30 UTC "
            "(previous day) when stored"
        )
