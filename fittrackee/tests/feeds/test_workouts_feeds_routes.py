from datetime import datetime, timezone
from email.utils import format_datetime
from typing import TYPE_CHECKING, List
from unittest.mock import patch

from time_machine import travel

from fittrackee.visibility_levels import VisibilityLevel

from ..mixins import ApiTestCaseMixin
from .template_results.workouts import (
    expected_en_empty_feed,
    expected_en_feed_user_1_workouts,
    expected_en_feed_workout_cycling_user_1,
    expected_en_feed_workout_cycling_user_1_in_imperials_units,
    expected_fr_feed_workout_cycling_user_1_with_map,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout


class TestGetUserPublicWorkoutsFeed(ApiTestCaseMixin):
    route = "/users/{username}/workouts.rss"

    def test_it_returns_error_when_user_does_not_exist(
        self, app: "Flask"
    ) -> None:
        client = app.test_client()

        response = client.get(self.route.format(username="not_existing"))

        self.assert_404_with_message(response, "user does not exist")

    def test_it_returns_empty_feed_when_no_visible_workouts(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PRIVATE
        client = app.test_client()
        now = datetime.now(timezone.utc)

        with travel(now, tick=False):
            response = client.get(self.route.format(username=user_1.username))

        assert response.status_code == 200
        assert response.mimetype == "text/xml"
        assert response.data.decode() == expected_en_empty_feed.format(
            username=user_1.username, last_date=format_datetime(now)
        )

    def test_it_returns_empty_feed_when_user_is_suspended(
        self,
        app: "Flask",
        suspended_user: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        client = app.test_client()
        now = datetime.now(timezone.utc)

        with travel(now, tick=False):
            response = client.get(
                self.route.format(username=suspended_user.username)
            )

        assert response.status_code == 200
        assert response.mimetype == "text/xml"
        assert response.data.decode() == expected_en_empty_feed.format(
            username=suspended_user.username, last_date=format_datetime(now)
        )

    @patch("fittrackee.feeds.routes.FEED_ITEMS_LIMIT", 2)
    def test_it_returns_feed_for_user_visible_workouts(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        seven_workouts_user_1: List["Workout"],
        workout_cycling_user_2: "Workout",
    ) -> None:
        for index, workout in enumerate(seven_workouts_user_1):
            if index % 2 == 0:
                workout.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC

        client = app.test_client()
        now = datetime.now(timezone.utc)

        with travel(now, tick=False):
            response = client.get(self.route.format(username=user_1.username))

        assert response.status_code == 200
        assert response.mimetype == "text/xml"

        assert (
            response.data.decode()
            == expected_en_feed_user_1_workouts.format(
                workout_1_short_id=seven_workouts_user_1[6].short_id,
                workout_2_short_id=seven_workouts_user_1[4].short_id,
            )
        )

    def test_it_returns_feed_with_imperial_unit(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = "some_title"
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        client = app.test_client()
        now = datetime.now(timezone.utc)

        with travel(now, tick=False):
            response = client.get(
                f"{self.route.format(username=user_1.username)}?"
                "imperial_unit=true"
            )

        assert response.status_code == 200
        assert response.mimetype == "text/xml"
        assert response.data.decode() == (
            expected_en_feed_workout_cycling_user_1_in_imperials_units.format(
                workout_short_id=workout_cycling_user_1.short_id,
                workout_title=workout_cycling_user_1.title,
            )
        )

    def test_it_returns_feed_in_metric_system_when_imperial_unit_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = "some title"
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        client = app.test_client()
        now = datetime.now(timezone.utc)

        with travel(now, tick=False):
            response = client.get(
                f"{self.route.format(username=user_1.username)}?"
                f"imperial_unit=invalid"
            )

        assert response.status_code == 200
        assert response.mimetype == "text/xml"
        assert (
            response.data.decode()
            == expected_en_feed_workout_cycling_user_1.format(
                workout_short_id=workout_cycling_user_1.short_id,
                workout_title=workout_cycling_user_1.title,
            )
        )

    def ttest_it_returns_feed_with_fr_language(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = "some title"
        workout_cycling_user_1.map_id = "some_id"
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.map_visibility = VisibilityLevel.PUBLIC
        client = app.test_client()
        now = datetime.now(timezone.utc)

        with travel(now, tick=False):
            response = client.get(
                f"{self.route.format(username=user_1.username)}?lang=fr"
            )

        assert response.status_code == 200
        assert response.mimetype == "text/xml"
        assert (
            response.data.decode()
            == expected_fr_feed_workout_cycling_user_1_with_map.format(
                workout_short_id=workout_cycling_user_1.short_id,
                workout_map_id=workout_cycling_user_1.map_id,
                workout_title=workout_cycling_user_1.title,
            )
        )
