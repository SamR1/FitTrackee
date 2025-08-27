from datetime import datetime, timezone
from email.utils import format_datetime
from typing import TYPE_CHECKING

import feedgenerator
from flask import Flask
from time_machine import travel

from fittrackee.feeds.feeds.feed_item_template import FeedItemTemplate
from fittrackee.feeds.feeds.workouts_feed_service import (
    UserWorkoutsFeedService,
)
from fittrackee.visibility_levels import VisibilityLevel

from ...mixins import WorkoutMixin
from ..template_results.workouts import (
    expected_en_empty_feed,
    expected_en_feed_workout_cycling_user_1,
    expected_en_feed_workout_cycling_user_1_with_elevation,
    expected_en_feed_workout_cycling_user_1_with_elevation_in_imperial_units,
    expected_en_feed_workout_cycling_user_1_with_map,
    expected_en_feed_workout_cycling_user_1_without_elevation,
    expected_fr_feed_workout_cycling_user_1_with_map,
)

if TYPE_CHECKING:
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout

WORKOUT_MAP_ID = "c2e9a2b48e7eb934d7ec39f4a6641c57"
WORKOUT_TITLE = "Some title"


class TestUserWorkoutsFeedServiceInitialisation:
    def test_it_initialises_service_with_default_values(
        self,
        app: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        service = UserWorkoutsFeedService(
            user=user_1, workouts=[workout_cycling_user_1]
        )

        assert service.distance_multiplier == 1
        assert service.distance_unit == "km"
        assert service.elevation_multiplier == 1
        assert service.elevation_unit == "m"
        assert service.fittrackee_url == app.config["UI_URL"]
        assert service.lang == "en"
        assert service.user == user_1
        assert service.workouts == [workout_cycling_user_1]
        assert isinstance(service.feed, feedgenerator.Rss201rev2Feed)
        assert isinstance(service.feed_template, FeedItemTemplate)

    def test_it_initialises_service_with_given_values(
        self,
        app: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        service = UserWorkoutsFeedService(
            user=user_1,
            workouts=[workout_cycling_user_1],
            lang="fr",
            use_imperial_units=True,
        )

        assert service.distance_multiplier == 0.621371
        assert service.distance_unit == "mi"
        assert service.elevation_multiplier == 3.280839895
        assert service.elevation_unit == "ft"
        assert service.fittrackee_url == app.config["UI_URL"]
        assert service.lang == "fr"
        assert service.user == user_1
        assert service.workouts == [workout_cycling_user_1]
        assert isinstance(service.feed, feedgenerator.Rss201rev2Feed)
        assert isinstance(service.feed_template, FeedItemTemplate)


class TestUserWorkoutsFeedServiceGenerateUserWorkoutsFeed(WorkoutMixin):
    def test_it_returns_feed_for_en_language(
        self,
        app: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = WORKOUT_TITLE
        service = UserWorkoutsFeedService(
            user=user_1, workouts=[workout_cycling_user_1]
        )

        feed = service.generate_user_workouts_feed()

        assert feed == expected_en_feed_workout_cycling_user_1.format(
            workout_short_id=workout_cycling_user_1.short_id,
            workout_title=WORKOUT_TITLE,
        )

    def test_it_returns_feed_for_workout_with_map(
        self,
        app: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = WORKOUT_TITLE
        workout_cycling_user_1.map_id = WORKOUT_MAP_ID
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.map_visibility = VisibilityLevel.PUBLIC
        service = UserWorkoutsFeedService(
            user=user_1, workouts=[workout_cycling_user_1]
        )

        feed = service.generate_user_workouts_feed()

        assert feed == expected_en_feed_workout_cycling_user_1_with_map.format(
            workout_short_id=workout_cycling_user_1.short_id,
            workout_map_id=WORKOUT_MAP_ID,
            workout_title=WORKOUT_TITLE,
        )

    def test_it_returns_feed_for_workout_with_map_when_map_is_not_visible(
        self,
        app: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = WORKOUT_TITLE
        workout_cycling_user_1.map_id = WORKOUT_MAP_ID
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.FOLLOWERS
        workout_cycling_user_1.map_visibility = VisibilityLevel.FOLLOWERS
        service = UserWorkoutsFeedService(
            user=user_1, workouts=[workout_cycling_user_1]
        )

        feed = service.generate_user_workouts_feed()

        assert feed == expected_en_feed_workout_cycling_user_1.format(
            workout_short_id=workout_cycling_user_1.short_id,
            workout_title=WORKOUT_TITLE,
        )

    def test_it_returns_feed_for_workout_with_elevation(
        self,
        app: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = WORKOUT_TITLE
        workout_cycling_user_1.map_id = WORKOUT_MAP_ID
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.PUBLIC
        self.update_workout_with_file_data(workout_cycling_user_1)
        service = UserWorkoutsFeedService(
            user=user_1, workouts=[workout_cycling_user_1]
        )

        feed = service.generate_user_workouts_feed()

        assert (
            feed
            == expected_en_feed_workout_cycling_user_1_with_elevation.format(
                workout_short_id=workout_cycling_user_1.short_id,
                workout_title=WORKOUT_TITLE,
            )
        )

    def test_it_returns_feed_for_without_elevation_when_visibility_does_not_allow_it(  # noqa
        self,
        app: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = WORKOUT_TITLE
        workout_cycling_user_1.map_id = WORKOUT_MAP_ID
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.FOLLOWERS
        self.update_workout_with_file_data(workout_cycling_user_1)
        service = UserWorkoutsFeedService(
            user=user_1, workouts=[workout_cycling_user_1]
        )

        feed = service.generate_user_workouts_feed()

        assert feed == (
            expected_en_feed_workout_cycling_user_1_without_elevation.format(
                workout_short_id=workout_cycling_user_1.short_id,
                workout_title=WORKOUT_TITLE,
            )
        )

    def test_it_returns_feed_in_imperial_unit(
        self,
        app: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = WORKOUT_TITLE
        workout_cycling_user_1.map_id = WORKOUT_MAP_ID
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.PUBLIC
        self.update_workout_with_file_data(workout_cycling_user_1)
        service = UserWorkoutsFeedService(
            user=user_1,
            workouts=[workout_cycling_user_1],
            use_imperial_units=True,
        )

        feed = service.generate_user_workouts_feed()

        assert feed == (
            expected_en_feed_workout_cycling_user_1_with_elevation_in_imperial_units.format(
                workout_short_id=workout_cycling_user_1.short_id,
                workout_title=WORKOUT_TITLE,
            )
        )

    def test_it_returns_feed_for_fr_language(
        self,
        app: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = WORKOUT_TITLE
        workout_cycling_user_1.map_id = WORKOUT_MAP_ID
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.map_visibility = VisibilityLevel.PUBLIC
        service = UserWorkoutsFeedService(
            user=user_1, workouts=[workout_cycling_user_1], lang="fr"
        )

        feed = service.generate_user_workouts_feed()

        assert feed == expected_fr_feed_workout_cycling_user_1_with_map.format(
            workout_short_id=workout_cycling_user_1.short_id,
            workout_map_id=WORKOUT_MAP_ID,
            workout_title=WORKOUT_TITLE,
        )

    def test_it_returns_feed_in_en_when_language_is_not_supported(
        self,
        app: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.title = WORKOUT_TITLE
        service = UserWorkoutsFeedService(
            user=user_1, workouts=[workout_cycling_user_1], lang="ar"
        )

        feed = service.generate_user_workouts_feed()

        assert feed == expected_en_feed_workout_cycling_user_1.format(
            workout_short_id=workout_cycling_user_1.short_id,
            workout_title=WORKOUT_TITLE,
        )

    def test_it_returns_feed_when_no_workouts(
        self,
        app: Flask,
        user_1: "User",
    ) -> None:
        service = UserWorkoutsFeedService(user=user_1, workouts=[])
        now = datetime.now(timezone.utc)

        with travel(now, tick=False):
            feed = service.generate_user_workouts_feed()

        assert feed == expected_en_empty_feed.format(
            username=user_1.username, last_date=format_datetime(now)
        )
