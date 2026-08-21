import hashlib
from abc import ABC, abstractmethod
from typing import IO, TYPE_CHECKING, Dict, List, Optional, Union

from flask import current_app
from staticmap3 import Line, StaticMap

from fittrackee import VERSION, appLog, db
from fittrackee.constants import (
    ElevationDataSource,
    ElevationProcessing,
)
from fittrackee.files import get_absolute_file_path

from ...exceptions import WorkoutException, WorkoutRefreshException
from ..elevation.elevation_service import ElevationService
from ..weather import WeatherService
from .workout_point import WorkoutPoint

if TYPE_CHECKING:
    from datetime import datetime

    from gpxpy.gpx import GPX

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout

weather_service = WeatherService()


class BaseWorkoutWithSegmentsCreationService(ABC):
    # file is converted in gpx format if not in gpx format
    gpx: "GPX"
    sport: "Sport"

    @abstractmethod
    def __init__(
        self,
        auth_user: "User",
        workout_file: IO[bytes],
        sport: "Sport",
        # stopped_speed_threshold based on the user's sports preferences, if
        # any. Otherwise, based on the sport
        stopped_speed_threshold: float,
        workout: Optional["Workout"],  # for refresh
        get_weather: bool = True,
        # for refresh from CLI in order to add missing elevation if a elevation
        # service is available
        get_elevation_on_refresh: bool = False,
        # elevation changes from UI:
        # - get_elevation_on_refresh is True
        # - change_elevation_source and elevation_processing are provided
        change_elevation_source: Optional["ElevationDataSource"] = None,
        elevation_processing: Optional["ElevationProcessing"] = None,
    ) -> None:
        self.auth_user = auth_user
        self.sport = sport
        self.coordinates: List[List[float]] = []
        self.stopped_speed_threshold = stopped_speed_threshold
        self.workout_name: Optional[str] = None
        self.workout_description: Optional[str] = None
        self.start_point: Optional["WorkoutPoint"] = None
        self.end_point: Optional["WorkoutPoint"] = None
        self.get_weather = get_weather
        self.workout = workout

        if not self.workout:
            self.is_creation = True
            self.get_elevation_on_refresh = False
            self.updated_elevation_data_source: Optional[
                "ElevationDataSource"
            ] = None
            self.elevation_processing: Optional["ElevationProcessing"] = None
            self.reuse_existing_elevation = False
            self.update_existing_elevation = False
            self.workout_has_missing_elevation: Optional[bool] = None

        # refresh
        else:
            self._check_elevation_parameters(
                change_elevation_source, elevation_processing
            )
            self.is_creation = False
            self._calculate_elevation_parameters_for_refresh(
                get_elevation_on_refresh,
                change_elevation_source,
                elevation_processing,
            )

    @staticmethod
    def _check_elevation_parameters(
        change_elevation_source: Optional["ElevationDataSource"] = None,
        elevation_processing: Optional["ElevationProcessing"] = None,
    ) -> None:
        if (
            change_elevation_source is None
            and elevation_processing is not None
        ) or (
            elevation_processing is None
            and change_elevation_source is not None
        ):
            raise WorkoutRefreshException(
                "error",
                (
                    "'change_elevation_source' and 'elevation_processing' "
                    "must be provided together"
                ),
            )

    def _calculate_elevation_parameters_for_refresh(
        self,
        get_elevation_on_refresh: bool,
        change_elevation_source: Optional["ElevationDataSource"],
        elevation_processing: Optional["ElevationProcessing"],
    ) -> None:
        if not self.workout:
            raise WorkoutException(
                "invalid", "no workout provided for refresh"
            )

        self.get_elevation_on_refresh = get_elevation_on_refresh
        self.reuse_existing_elevation = False
        self.update_existing_elevation = False
        self.elevation_processing = (
            elevation_processing
            if elevation_processing
            else self.auth_user.elevation_processing
            if self.get_elevation_on_refresh
            else self.workout.elevation_processing
        )
        self.workout_has_missing_elevation = (
            not self.workout.segments
            or any(not segment.points for segment in self.workout.segments)
            or any(
                point.get("elevation") is None
                for segment in self.workout.segments
                for point in segment.points
            )
        )

        self.updated_elevation_data_source = (
            None
            if (
                not self.get_elevation_on_refresh
                or self.workout.elevation_data_source
                == change_elevation_source
            )
            else change_elevation_source
        )

        if not self.get_elevation_on_refresh:
            self.reuse_existing_elevation = (
                self.workout.elevation_data_source != ElevationDataSource.FILE
                or self.workout.elevation_processing
                != ElevationProcessing.NONE
            )
            return

        is_elevation_service_available = (
            ElevationService(
                (
                    self.updated_elevation_data_source
                    or self.auth_user.missing_elevations_data_source
                ),
                ElevationProcessing.NONE,
            ).elevation_service
            is not None
        )

        if (
            self.updated_elevation_data_source is None
            and self.workout_has_missing_elevation
            and is_elevation_service_available
        ):
            self.updated_elevation_data_source = (
                self.auth_user.missing_elevations_data_source
            )

            self.reuse_existing_elevation = False
            self.update_existing_elevation = False
            self.elevation_processing = (
                elevation_processing or self.auth_user.elevation_processing
            )
            return

        # can not use or update existing elevation when elevation data source
        # is modified and elevation service available if case data source is
        # not file
        if self.updated_elevation_data_source:
            if (
                self.updated_elevation_data_source != ElevationDataSource.FILE
                and not is_elevation_service_available
            ):
                raise WorkoutRefreshException(
                    "invalid", "provided data source is not set"
                )

            if (
                self.update_existing_elevation != ElevationDataSource.FILE
                and not is_elevation_service_available
            ):
                # to avoid removing existing elevation from elevation API when
                # Elevation service has been disabled (i.e. elevation API URLs
                # have been removed, no elevation service available)

                if (
                    (
                        self.workout.elevation_processing
                        == ElevationProcessing.NONE
                    )
                    and self.elevation_processing
                    and self.elevation_processing != ElevationProcessing.NONE
                ):
                    self.reuse_existing_elevation = True
                    self.update_existing_elevation = True
                return

            self.reuse_existing_elevation = False
            self.update_existing_elevation = False
            self.elevation_processing = elevation_processing
            return

        if elevation_processing is None:
            if (
                # elevation data source is not modified and
                # elevation_processing is not provided
                self.workout.elevation_processing
                == self.auth_user.elevation_processing
                or not self.workout_has_missing_elevation
            ):
                self.reuse_existing_elevation = True
                self.update_existing_elevation = False
                self.elevation_processing = (
                    None
                    if not self.workout_has_missing_elevation
                    else elevation_processing
                )

        else:
            # elevation data source is not modified but the existing elevation
            # data have been processed
            self.reuse_existing_elevation = (
                self.workout.elevation_processing == ElevationProcessing.NONE
            )
            self.update_existing_elevation = (
                self.reuse_existing_elevation
                and self.workout.elevation_processing != elevation_processing
            )
            self.elevation_processing = elevation_processing

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
    def generate_map_image(cls, map_filepath: str, coordinates: List) -> None:
        m = StaticMap(
            width=400,
            height=225,
            padding_x=10,
            headers={"User-Agent": f"FitTrackee v{VERSION}"},
            delay_between_retries=5,
        )
        if not current_app.config["DEFAULT_STATICMAP"]:
            try:
                tile_provider = next(
                    iter(
                        current_app.config.get(
                            "available_tile_providers", {}
                        ).values()
                    )
                )
            except StopIteration:
                tile_provider = current_app.config["TILE_PROVIDERS"]["osm"]
            m.url_template = tile_provider.url

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
        try:
            workout = self._process_file()
        except Exception as e:
            db.session.rollback()
            raise e

        if not self.get_weather:
            return workout

        # Start and end points are None when they have no time
        # When start point has no time, it raises exception before getting
        # weather
        if not self.start_point or not self.end_point:
            appLog.error(
                f"no time for the last point for workout '{workout.short_id}',"
                " no weather data is fetched"
            )
            return workout

        # In case of refresh, it updates only workouts without weather data
        if not workout.weather_start and not workout.weather_end:
            weather_start, weather_end = self.get_weather_data(
                self.start_point,
                self.end_point,
            )
            if weather_start and weather_end:
                workout.weather_start = weather_start
                workout.weather_end = weather_end

        db.session.flush()
        return workout
