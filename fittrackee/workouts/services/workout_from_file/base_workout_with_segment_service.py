import hashlib
from abc import ABC, abstractmethod
from typing import IO, TYPE_CHECKING, Dict, List, Optional, Tuple, Union

from flask import current_app
from staticmap3 import Line, StaticMap

from fittrackee import VERSION, appLog, db
from fittrackee.constants import (
    DEFAULT_TILE_PROVIDER,
    ElevationDataSource,
    ElevationProcessing,
)
from fittrackee.files import get_absolute_file_path

from ...constants import SPORTS_WITHOUT_ELEVATION_DATA
from ...exceptions import WorkoutRefreshException
from ..elevation.elevation_service import ElevationService
from ..weather import WeatherService
from .workout_point import WorkoutPoint

if TYPE_CHECKING:
    from datetime import datetime

    import gpxpy

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout

weather_service = WeatherService()


class BaseWorkoutWithSegmentsCreationService(ABC):
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
        # for refresh from CLI in order to add missing elevation if an
        # elevation service is available
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
        self.cadences: List[int] = []
        self.heart_rates: List[int] = []
        self.powers: List[int] = []
        self.get_weather = get_weather
        self.workout = workout
        self.is_creation = self.workout is None

        # The file is converted to GPX format if it is not already in
        # GPX format
        self.gpx, self.file_stats, self.sessions_stats = self.parse_file(
            workout_file, auth_user.segments_creation_event, sport
        )
        self.track: "gpxpy.gpx.GPXTrack" = self.gpx.tracks[0]
        self.track_segments: List["gpxpy.gpx.GPXTrackSegment"] = (
            self.track.segments
        )

        self.workout_has_missing_elevation: bool = (
            self._has_missing_elevation()
        )

        # default values
        self.updated_elevation_data_source: Optional["ElevationDataSource"] = (
            None
        )
        self.elevation_processing = ElevationProcessing.NONE
        self.get_elevation_on_refresh = False
        self.reuse_existing_elevation = False
        self.update_existing_elevation = False
        self.elevation_service: Optional["ElevationService"] = None

        self._initialize_values(
            get_elevation_on_refresh,
            change_elevation_source,
            elevation_processing,
        )

    @classmethod
    @abstractmethod
    def parse_file(
        cls,
        workout_file: IO[bytes],
        segments_creation_event: str,
        sport: "Sport",
    ) -> Tuple["gpxpy.gpx.GPX", Dict, List[Dict]]:
        pass

    def _has_missing_elevation(self) -> bool:
        # refresh
        if self.workout:
            return (
                not self.workout.segments
                or any(not segment.points for segment in self.workout.segments)
                or any(
                    point.get("elevation") is None
                    for segment in self.workout.segments
                    for point in segment.points
                )
            )

        # creation
        has_missing_elevation = False
        for segment in self.track_segments:
            if len(segment.points) < 2:
                continue
            has_missing_elevation = any(
                point.elevation is None for point in segment.points
            )
            if has_missing_elevation:
                break
        return has_missing_elevation

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

    def _calculate_elevation_parameters(self) -> None:
        """
        For creation or refresh
        (not for elevation change from UI)
        """
        if (
            self.workout_has_missing_elevation
            or not self.auth_user.process_only_missing_elevations
        ):
            self.updated_elevation_data_source = (
                None
                if (
                    self.auth_user.elevation_data_source
                    == ElevationDataSource.FILE
                )
                else self.auth_user.elevation_data_source
            )
            self.elevation_processing = self.auth_user.elevation_processing

    def _check_elevation_service(self) -> None:
        """
        Check if sport is valid for get elevation and initialize the elevation
        service
        It also checks if the elevation service is available
        (in case, the user set a preference for a service, but the
        administrator later disabled it)
        """

        if self.sport.label in SPORTS_WITHOUT_ELEVATION_DATA:
            self.updated_elevation_data_source = None
            self.elevation_service = None
            return

        # initialize the elevation service if elevation data source changed
        # to OpenElevation or Valhalla
        if self.updated_elevation_data_source is not None and (
            self.updated_elevation_data_source != ElevationDataSource.FILE
        ):
            self.elevation_service = ElevationService(
                self.updated_elevation_data_source,
                self.elevation_processing,
            )
        # or when data source is unchanged, but elevation processing switches
        # to "no processing"
        elif (
            self.workout
            and self.updated_elevation_data_source is None
            and self.elevation_processing == ElevationProcessing.NONE
            and self.workout.elevation_processing != ElevationProcessing.NONE
        ):
            self.elevation_service = ElevationService(
                self.workout.elevation_data_source,
                self.elevation_processing,
            )

        # check if service is still available
        if self.elevation_service and not self.elevation_service.is_available:
            self.updated_elevation_data_source = None
            self.elevation_service = None

    def _initialize_values(
        self,
        # for refresh or update
        get_elevation_on_refresh: bool = False,
        change_elevation_source: Optional["ElevationDataSource"] = None,
        elevation_processing: Optional["ElevationProcessing"] = None,
    ) -> None:
        # refresh or elevation update
        if self.workout:
            # existing workout value
            self.elevation_processing = self.workout.elevation_processing
            self.get_elevation_on_refresh = get_elevation_on_refresh
            self.reuse_existing_elevation = True

            if not self.get_elevation_on_refresh:
                self.reuse_existing_elevation = (
                    self.workout.elevation_data_source
                    != ElevationDataSource.FILE
                ) or (
                    self.workout.elevation_processing
                    != ElevationProcessing.NONE
                )

            else:
                self._check_elevation_parameters(
                    change_elevation_source, elevation_processing
                )

                if change_elevation_source and elevation_processing:
                    self.updated_elevation_data_source = (
                        None
                        if (
                            self.workout.elevation_data_source
                            == change_elevation_source
                        )
                        else change_elevation_source
                    )
                    self.elevation_processing = elevation_processing

                    if self.updated_elevation_data_source is not None:
                        self.reuse_existing_elevation = False
                    if (
                        self.elevation_processing
                        != self.workout.elevation_processing
                    ) or self.updated_elevation_data_source is not None:
                        self.update_existing_elevation = True

                else:
                    self._calculate_elevation_parameters()

                self._check_elevation_service()

                # do not reuse existing elevation when:
                # - elevation data source is back to file (to read file
                # content)
                # - elevation data source switched from OpenElevation to
                # Valhalla and vice versa
                if self.updated_elevation_data_source is not None:
                    self.reuse_existing_elevation = False
                elif (
                    self.elevation_service
                    and (
                        self.updated_elevation_data_source
                        != ElevationDataSource.FILE
                    )
                    and (
                        self.workout.elevation_data_source
                        != ElevationDataSource.FILE
                    )
                ):
                    self.reuse_existing_elevation = False
                # reuse existing elevation when:
                # - processing is unchanged
                # - or datasource is not changed and smoothing is applied or
                # processing is unchanged
                else:
                    self.reuse_existing_elevation = (
                        self.updated_elevation_data_source is None
                        and (
                            (
                                self.elevation_processing
                                == self.workout.elevation_processing
                            )
                            or (
                                self.workout.elevation_processing
                                == ElevationProcessing.NONE
                            )
                        )
                    ) or (
                        (
                            self.workout.elevation_processing
                            != ElevationProcessing.NONE
                        )
                        and (
                            self.elevation_processing
                            != ElevationProcessing.NONE
                        )
                    )

        # creation
        else:
            self._calculate_elevation_parameters()
            self._check_elevation_service()

            # prevent smoothing elevation when data is missing
            if (
                self.updated_elevation_data_source is None
                and self.elevation_processing != ElevationProcessing.NONE
                and self.workout_has_missing_elevation
            ):
                self.elevation_processing = ElevationProcessing.NONE

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
    def generate_map_image(
        cls, map_filepath: str, coordinates: List, auth_user: "User"
    ) -> None:
        m = StaticMap(
            width=400,
            height=225,
            padding_x=10,
            headers={"User-Agent": f"FitTrackee v{VERSION}"},
            delay_between_retries=5,
        )
        if not current_app.config["DEFAULT_STATICMAP"]:
            default_tile_provider = auth_user.default_tile_provider

            # in case of:
            # - no tile providers available (should not happen) or
            # - provider set in user preference have been disabled,
            # get default provider set for application
            if not current_app.config.get("available_tile_providers") or (
                default_tile_provider
                not in current_app.config.get("available_tile_providers", {})
            ):
                default_tile_provider = current_app.config.get(
                    "default_tile_provider", DEFAULT_TILE_PROVIDER
                )
                tile_provider = current_app.config["TILE_PROVIDERS"][
                    default_tile_provider
                ]
            else:
                tile_provider = current_app.config["available_tile_providers"][
                    default_tile_provider
                ]
            m.url_template = tile_provider.url_with_subdomain

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
