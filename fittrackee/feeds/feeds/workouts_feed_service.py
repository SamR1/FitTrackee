from typing import TYPE_CHECKING, List, Optional

import feedgenerator
from flask import current_app
from flask_babel import force_locale, lazy_gettext

from fittrackee.feeds.feeds.feed_item_template import FeedItemTemplate
from fittrackee.visibility_levels import (
    can_view,
)

if TYPE_CHECKING:
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout

KILOMETERS_TO_MILES_MULTIPLIER = 0.621371


class UserWorkoutsFeedService:
    def __init__(
        self,
        user: "User",
        workouts: List["Workout"],
        lang: str = "en",
        use_imperial_units: bool = False,
    ):
        self.fittrackee_url = current_app.config["UI_URL"]
        self.user = user
        self.workouts = workouts
        self.lang = lang if lang in current_app.config["LANGUAGES"] else "en"
        self.distance_multiplier = (
            KILOMETERS_TO_MILES_MULTIPLIER if use_imperial_units else 1.0
        )
        self.unit = "mi" if use_imperial_units else "km"
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

    def _get_workout_item(
        self, fittrackee_url: str, workout: "Workout"
    ) -> dict:
        can_view_map = workout.map_id and can_view(
            workout,
            "calculated_map_visibility",
            user=None,
        )
        data = {
            "workout_map": (
                f"{fittrackee_url}/api/workouts/map/{workout.map_id}"
                if can_view_map
                else None
            ),
            "workout_title": workout.title,
            "workout_distance": self._get_distance(workout.distance),
            "workout_unit": self.unit,
            "workout_duration": workout.moving,
            "sport_label": workout.sport.label,
        }
        return self.feed_template.get_item_data("workout", self.lang, data)

    def generate_user_workouts_feed(self) -> str:
        for workout in self.workouts:
            item_data = self._get_workout_item(self.fittrackee_url, workout)
            self.feed.add_item(
                title=item_data["title.txt"],
                link=f"{self.fittrackee_url}/workouts/{workout.short_id}",
                pubdate=workout.workout_date,
                description=item_data["body.html"],
            )
        return self.feed.writeString("UTF-8")
