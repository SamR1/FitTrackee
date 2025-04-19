import hashlib
import random
from abc import abstractmethod
from typing import IO, TYPE_CHECKING, Dict, List, Optional, Union

from flask import current_app
from staticmap import Line, StaticMap

from fittrackee import VERSION, db
from fittrackee.files import get_absolute_file_path

from ..weather import WeatherService
from .workout_point import WorkoutPoint

if TYPE_CHECKING:
    from datetime import datetime

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout

weather_service = WeatherService()


class BaseWorkoutWithSegmentsCreationService:
    @abstractmethod
    def __init__(
        self,
        auth_user: "User",
        workout_file: IO[bytes],
        sport_id: int,
        stopped_speed_threshold: float,
    ) -> None:
        self.auth_user = auth_user
        self.sport_id = sport_id
        self.coordinates: List[List[float]] = []
        self.stopped_speed_threshold = stopped_speed_threshold
        self.workout_name: Optional[str] = None
        self.workout_description: Optional[str] = None
        self.start_point: Optional["WorkoutPoint"] = None
        self.end_point: Optional["WorkoutPoint"] = None

    @abstractmethod
    def get_workout_date(self) -> "datetime":
        pass

    @classmethod
    def get_map_hash(cls, map_filepath: str) -> str:
        """
        Generate a md5 hash used as id instead of workout id, to retrieve map
        image (maps are sensitive data)
        """
        md5 = hashlib.md5(usedforsecurity=False)
        absolute_map_filepath = get_absolute_file_path(map_filepath)
        with open(absolute_map_filepath, "rb") as f:
            for chunk in iter(lambda: f.read(128 * md5.block_size), b""):
                md5.update(chunk)
        return md5.hexdigest()

    @classmethod
    def get_static_map_tile_server_url(cls, tile_server_config: Dict) -> str:
        if tile_server_config["STATICMAP_SUBDOMAINS"]:
            subdomains = tile_server_config["STATICMAP_SUBDOMAINS"].split(",")
            subdomain = f"{random.choice(subdomains)}."  # nosec
        else:
            subdomain = ""
        return tile_server_config["URL"].replace("{s}.", subdomain)

    @classmethod
    def generate_map_image(cls, map_filepath: str, coordinates: List) -> None:
        m = StaticMap(
            width=400,
            height=225,
            padding_x=10,
            headers={"User-Agent": f"FitTrackee v{VERSION}"},
            delay_between_retries=5,
        )
        if not current_app.config["TILE_SERVER"]["DEFAULT_STATICMAP"]:
            m.url_template = cls.get_static_map_tile_server_url(
                current_app.config["TILE_SERVER"]
            )
        line = Line(coords=coordinates, color="#3388FF", width=4)
        m.add_line(line)
        image = m.render()
        image.save(map_filepath)

    @staticmethod
    def get_weather_data(
        start_point: WorkoutPoint, end_point: WorkoutPoint
    ) -> List[Union[Dict, None]]:
        return [
            weather_service.get_weather(start_point),
            weather_service.get_weather(end_point),
        ]

    @abstractmethod
    def _process_file(self) -> "Workout":
        pass

    def process_workout(self) -> "Workout":
        new_workout = self._process_file()

        if self.start_point and self.end_point:
            new_workout.weather_start, new_workout.weather_end = (
                self.get_weather_data(
                    self.start_point,
                    self.end_point,
                )
            )

        db.session.flush()
        return new_workout
