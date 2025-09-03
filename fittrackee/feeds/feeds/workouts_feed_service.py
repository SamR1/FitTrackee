from typing import TYPE_CHECKING, List, Optional

import feedgenerator
import mistune
from flask import current_app
from flask_babel import force_locale, lazy_gettext

from fittrackee.feeds.feeds.feed_item_template import FeedItemTemplate
from fittrackee.utils import clean_input
from fittrackee.visibility_levels import (
    can_view,
)

if TYPE_CHECKING:
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout

KILOMETERS_TO_MILES_MULTIPLIER = 0.621371
METERS_TO_FEETS_MULTIPLIER = 3.280839895


class UserWorkoutsFeedService:
    def __init__(
        self,
        user: "User",
        workouts: List["Workout"],
        lang: str = "en",
        use_imperial_units: bool = False,
        with_description: bool = False,
    ):
        self.fittrackee_url = current_app.config["UI_URL"]
        self.user = user
        self.workouts = workouts
        self.lang = lang if lang in current_app.config["LANGUAGES"] else "en"
        self.with_description = with_description

        # to display distance and speed
        self.distance_multiplier = (
            KILOMETERS_TO_MILES_MULTIPLIER if use_imperial_units else 1.0
        )
        self.distance_unit = "mi" if use_imperial_units else "km"
        # to display elevation and ascent/descent
        self.elevation_multiplier = (
            METERS_TO_FEETS_MULTIPLIER if use_imperial_units else 1.0
        )
        self.elevation_unit = "ft" if use_imperial_units else "m"

        self.feed = self.init_feed()
        self.feed_template = FeedItemTemplate(
            current_app.config["FEEDS_TEMPLATES_FOLDER"],
            current_app.config["TRANSLATIONS_FOLDER"],
            current_app.config["LANGUAGES"],
        )

    def init_feed(self) -> "feedgenerator.Rss201rev2Feed":
        user_ui_url = f"{self.fittrackee_url}/users/{self.user.username}"
        with force_locale(self.lang):
            feed = feedgenerator.Rss201rev2Feed(
                description=(
                    lazy_gettext(
                        "Latest public workouts on FitTrackee from %(username)s",  # noqa
                        username=self.user.username,
                    )
                ),
                feed_url=f"{user_ui_url}/workouts.rss",
                language=self.lang,
                link=user_ui_url,
                title=(
                    lazy_gettext(
                        "%(username)s's workouts feed",
                        username=self.user.username,
                    )
                ),
            )
        return feed

    def _get_distance(self, value: Optional[float]) -> Optional[float]:
        if value is None:
            return None
        return round(float(value) * self.distance_multiplier, 3)

    def _get_elevation(
        self, value: Optional[float], can_view_altitude: bool = True
    ) -> Optional[float]:
        if value is None or not can_view_altitude:
            return None
        return round(float(value) * self.elevation_multiplier, 2)

    def _get_workout_item(
        self, fittrackee_url: str, workout: "Workout"
    ) -> dict:
        can_view_map = workout.map_id and can_view(
            workout,
            "calculated_map_visibility",
            user=None,
        )
        can_view_altitude = can_view(
            workout,
            "calculated_analysis_visibility",
            user=None,
        )
        data = {
            "workout_map": (
                f"{fittrackee_url}/api/workouts/map/{workout.map_id}"
                if can_view_map
                else None
            ),
            "workout_title": (
                clean_input(workout.title) if workout.title else ""
            ),
            "with_description": self.with_description and workout.description,
            "workout_distance": self._get_distance(workout.distance),
            "workout_distance_unit": self.distance_unit,
            "workout_min_altitude": self._get_elevation(
                workout.min_alt, can_view_altitude
            ),
            "workout_max_altitude": self._get_elevation(
                workout.max_alt, can_view_altitude
            ),
            "workout_ascent": self._get_elevation(workout.ascent),
            "workout_descent": self._get_elevation(workout.descent),
            "workout_elevation_unit": self.elevation_unit,
            "workout_duration": workout.moving,
            "sport_label": workout.sport.label,
        }
        return self.feed_template.get_item_data("workout", self.lang, data)

    def generate_user_workouts_feed(self) -> str:
        markdown = mistune.create_markdown(
            escape=False, plugins=["url", "speedup"]
        )
        for workout in self.workouts:
            item_data = self._get_workout_item(self.fittrackee_url, workout)
            workout_description = (
                clean_input(
                    markdown(workout.description),  # type: ignore[arg-type]
                    for_markdown_renderer=True,
                )
                if self.with_description and workout.description
                else ""
            )
            self.feed.add_item(
                title=item_data["title.txt"],
                link=f"{self.fittrackee_url}/workouts/{workout.short_id}",
                pubdate=workout.workout_date,
                description=item_data["body.html"] + workout_description,
            )
        return self.feed.writeString("UTF-8")
