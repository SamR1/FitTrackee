"""
Tests for user profile statistics visibility filtering.

These tests verify that:
1. Private workouts are NOT included in public profile statistics
2. Followers-only workouts are only visible to followers
3. Public workouts are visible to everyone
4. nb_workouts, nb_sports, total_distance, total_duration, total_ascent
   should all respect visibility levels
"""
import json
from datetime import datetime, timedelta, timezone
from typing import List

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.tests.fixtures.fixtures_workouts import update_workout
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin


class TestUserProfileVisibilityStats(ApiTestCaseMixin):
    """
    Tests for user profile statistics visibility filtering.
    """

    def create_workout_with_visibility(
        self,
        user: User,
        sport: Sport,
        workout_date: datetime,
        distance: float,
        visibility: VisibilityLevel,
    ) -> Workout:
        """Helper to create a workout with specific visibility."""
        workout = Workout(
            user_id=user.id,
            sport_id=sport.id,
            workout_date=workout_date,
            distance=distance,
            duration=timedelta(seconds=3600),
        )
        update_workout(workout)
        workout.workout_visibility = visibility
        db.session.add(workout)
        db.session.commit()
        return workout

    def test_public_workout_included_in_owner_stats(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test that owner can see their own public workout in statistics.
        """
        self.create_workout_with_visibility(
            user_1,
            sport_1_cycling,
            datetime(2024, 1, 1, 10, tzinfo=timezone.utc),
            10.0,
            VisibilityLevel.PUBLIC,
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        user_data = data["data"]["users"][0]

        assert user_data["nb_workouts"] == 1
        assert user_data["total_distance"] == 10.0

    def test_private_workout_included_in_owner_stats(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test that owner can see their own private workout in statistics.
        """
        self.create_workout_with_visibility(
            user_1,
            sport_1_cycling,
            datetime(2024, 1, 1, 10, tzinfo=timezone.utc),
            10.0,
            VisibilityLevel.PRIVATE,
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_1.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        user_data = data["data"]["users"][0]

        assert user_data["nb_workouts"] == 1
        assert user_data["total_distance"] == 10.0

    def test_private_workout_excluded_from_other_user_stats(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test that private workouts are EXCLUDED from statistics
        when viewed by other users.

        This is a critical privacy test - other users should NOT see
        statistics that include private workouts.
        """
        self.create_workout_with_visibility(
            user_2,
            sport_1_cycling,
            datetime(2024, 1, 1, 10, tzinfo=timezone.utc),
            10.0,
            VisibilityLevel.PRIVATE,
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        user_data = data["data"]["users"][0]

        assert user_data["nb_workouts"] == 0, (
            "Private workout should NOT be counted in nb_workouts "
            "when viewed by other users"
        )
        assert user_data.get("total_distance") in [0, None, 0.0], (
            "Private workout distance should NOT be included "
            "when viewed by other users"
        )

    def test_followers_only_workout_excluded_from_non_follower_stats(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test that followers-only workouts are EXCLUDED from statistics
        when viewed by non-followers.
        """
        self.create_workout_with_visibility(
            user_2,
            sport_1_cycling,
            datetime(2024, 1, 1, 10, tzinfo=timezone.utc),
            10.0,
            VisibilityLevel.FOLLOWERS,
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        user_data = data["data"]["users"][0]

        assert user_data["nb_workouts"] == 0, (
            "Followers-only workout should NOT be counted "
            "when viewed by non-followers"
        )

    def test_mixed_visibility_workouts_stats_for_other_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
    ) -> None:
        """
        Test that when a user has mixed visibility workouts:
        - Public workouts ARE included in statistics for other users
        - Private workouts are NOT included
        - Followers-only workouts are NOT included (for non-followers)

        Expected: only public workout (5km) should be counted.
        """
        self.create_workout_with_visibility(
            user_2,
            sport_1_cycling,
            datetime(2024, 1, 1, 10, tzinfo=timezone.utc),
            5.0,
            VisibilityLevel.PUBLIC,
        )
        self.create_workout_with_visibility(
            user_2,
            sport_1_cycling,
            datetime(2024, 1, 2, 10, tzinfo=timezone.utc),
            10.0,
            VisibilityLevel.PRIVATE,
        )
        self.create_workout_with_visibility(
            user_2,
            sport_2_running,
            datetime(2024, 1, 3, 10, tzinfo=timezone.utc),
            15.0,
            VisibilityLevel.FOLLOWERS,
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        user_data = data["data"]["users"][0]

        assert user_data["nb_workouts"] == 1, (
            "Only public workout should be counted for other users"
        )
        assert user_data.get("total_distance") == 5.0, (
            "Only public workout distance (5km) should be included"
        )
        assert user_data.get("nb_sports") == 1, (
            "Only cycling (public workout) should be counted, not running"
        )
        assert user_data.get("sports_list") == [sport_1_cycling.id], (
            "Only cycling sport should be in sports_list"
        )

    def test_owner_sees_all_workouts_in_stats(
        self,
        app: Flask,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
    ) -> None:
        """
        Test that owner sees ALL their workouts in statistics,
        regardless of visibility level.

        Expected: all 3 workouts (5+10+15=30km) should be counted.
        """
        self.create_workout_with_visibility(
            user_2,
            sport_1_cycling,
            datetime(2024, 1, 1, 10, tzinfo=timezone.utc),
            5.0,
            VisibilityLevel.PUBLIC,
        )
        self.create_workout_with_visibility(
            user_2,
            sport_1_cycling,
            datetime(2024, 1, 2, 10, tzinfo=timezone.utc),
            10.0,
            VisibilityLevel.PRIVATE,
        )
        self.create_workout_with_visibility(
            user_2,
            sport_2_running,
            datetime(2024, 1, 3, 10, tzinfo=timezone.utc),
            15.0,
            VisibilityLevel.FOLLOWERS,
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            f"/api/users/{user_2.username}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        user_data = data["data"]["users"][0]

        assert user_data["nb_workouts"] == 3, (
            "Owner should see all 3 workouts"
        )
        assert user_data.get("total_distance") == 30.0, (
            "Owner should see total distance of 30km (5+10+15)"
        )
        assert user_data.get("nb_sports") == 2, (
            "Owner should see both sports"
        )

    def test_unauthenticated_user_sees_only_public_workouts(
        self,
        app: Flask,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
    ) -> None:
        """
        Test that unauthenticated users only see public workouts in statistics.
        """
        self.create_workout_with_visibility(
            user_2,
            sport_1_cycling,
            datetime(2024, 1, 1, 10, tzinfo=timezone.utc),
            5.0,
            VisibilityLevel.PUBLIC,
        )
        self.create_workout_with_visibility(
            user_2,
            sport_2_running,
            datetime(2024, 1, 2, 10, tzinfo=timezone.utc),
            10.0,
            VisibilityLevel.PRIVATE,
        )

        client = app.test_client()

        response = client.get(
            f"/api/users/{user_2.username}",
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        user_data = data["data"]["users"][0]

        assert user_data["nb_workouts"] == 1, (
            "Unauthenticated users should only see public workouts"
        )
        assert "total_distance" not in user_data, (
            "Unauthenticated users should not see detailed statistics"
        )


class TestLatestWorkoutsVisibility(ApiTestCaseMixin):
    """
    Tests for get_user_latest_workouts endpoint visibility filtering.
    This endpoint already has proper filtering - these tests verify it works.
    """

    def create_workout_with_visibility(
        self,
        user: User,
        sport: Sport,
        workout_date: datetime,
        distance: float,
        visibility: VisibilityLevel,
    ) -> Workout:
        workout = Workout(
            user_id=user.id,
            sport_id=sport.id,
            workout_date=workout_date,
            distance=distance,
            duration=timedelta(seconds=3600),
        )
        update_workout(workout)
        workout.workout_visibility = visibility
        db.session.add(workout)
        db.session.commit()
        return workout

    def test_private_workout_not_in_latest_workouts_for_other_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test that private workouts do NOT appear in latest_workouts
        when viewed by other users.
        """
        self.create_workout_with_visibility(
            user_2,
            sport_1_cycling,
            datetime(2024, 1, 1, 10, tzinfo=timezone.utc),
            10.0,
            VisibilityLevel.PRIVATE,
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}/workouts",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())

        assert len(data["data"]["workouts"]) == 0, (
            "Private workout should NOT appear in latest_workouts "
            "for other users"
        )

    def test_public_workout_in_latest_workouts_for_other_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
    ) -> None:
        """
        Test that public workouts DO appear in latest_workouts
        when viewed by other users.
        """
        self.create_workout_with_visibility(
            user_2,
            sport_1_cycling,
            datetime(2024, 1, 1, 10, tzinfo=timezone.utc),
            10.0,
            VisibilityLevel.PUBLIC,
        )

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/users/{user_2.username}/workouts",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())

        assert len(data["data"]["workouts"]) == 1, (
            "Public workout should appear in latest_workouts for other users"
        )
