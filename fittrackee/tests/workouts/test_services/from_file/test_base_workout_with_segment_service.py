from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from staticmap3 import Line, StaticMap

from fittrackee import VERSION
from fittrackee.tests.fixtures.fixtures_workouts import (
    track_points_part_1_coordinates,
)
from fittrackee.workouts.services.workout_from_file import (
    BaseWorkoutWithSegmentsCreationService,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User


class TestBaseWorkoutWithSegmentsCreationServiceGenerateMapImage:
    def test_it_calls_staticmap_to_generate_map_image(
        self, app: "Flask", user_1: "User"
    ) -> None:
        with patch(
            "fittrackee.workouts.services.workout_from_file.base_workout_with_segment_service.StaticMap",
            return_value=StaticMap(400, 225, 10),
        ) as static_map_mock:
            BaseWorkoutWithSegmentsCreationService.generate_map_image(
                map_filepath="/tmp/map.png",
                coordinates=track_points_part_1_coordinates,
                auth_user=user_1,
            )

        static_map_mock.assert_called_once_with(
            width=400,
            height=225,
            padding_x=10,
            headers={"User-Agent": f"FitTrackee v{VERSION}"},
            delay_between_retries=5,
        )

    def test_it_calls_configured_tile_server_for_static_map_when_default_static_map_to_false(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        static_map_get_mock: MagicMock,
    ) -> None:
        """
        app and user default tile provider is "osm"
        """
        BaseWorkoutWithSegmentsCreationService.generate_map_image(
            map_filepath="/tmp/map.png",
            coordinates=track_points_part_1_coordinates,
            auth_user=user_1,
        )

        call_args, _ = static_map_get_mock.call_args

        assert (
            app.config["TILE_PROVIDERS"]["osm"]
            .url.replace("{s}.", "")
            .replace("/{z}/{x}/{y}.png", "")
            in call_args[0]
        )

    def test_it_calls_default_tile_server_for_static_map_with_user_default_tile_provider(  # noqa
        self,
        app_with_multiple_tile_servers_enabled: "Flask",
        user_1: "User",
        static_map_get_mock: MagicMock,
    ) -> None:
        """
        user default tile provider is "osm"
        app default tile provider is "cyclosm"
        """
        BaseWorkoutWithSegmentsCreationService.generate_map_image(
            map_filepath="/tmp/map.png",
            coordinates=track_points_part_1_coordinates,
            auth_user=user_1,
        )

        call_args, _ = static_map_get_mock.call_args
        assert (
            app_with_multiple_tile_servers_enabled.config["TILE_PROVIDERS"][
                "osm"
            ].url.replace("/{z}/{x}/{y}.png", "")
            in call_args[0]
        )

    def test_it_calls_default_tile_server_for_static_map_when_default_static_map_to_true(  # noqa
        self,
        app_default_static_map: "Flask",
        user_1: "User",
        static_map_get_mock: MagicMock,
    ) -> None:
        """
        app default tile provider is OSM (de)
        """
        user_1.default_tile_provider = "osm_de"
        BaseWorkoutWithSegmentsCreationService.generate_map_image(
            map_filepath="/tmp/map.png",
            coordinates=track_points_part_1_coordinates,
            auth_user=user_1,
        )

        call_args, _ = static_map_get_mock.call_args
        assert (
            app_default_static_map.config["TILE_PROVIDERS"][
                "osm_de"
            ].url.replace("/{z}/{x}/{y}.png", "")
            not in call_args[0]
        )

    def test_it_calls_static_map_with_fittrackee_user_agent(
        self,
        app: "Flask",
        user_1: "User",
        static_map_get_mock: MagicMock,
    ) -> None:
        BaseWorkoutWithSegmentsCreationService.generate_map_image(
            map_filepath="/tmp/map.png",
            coordinates=track_points_part_1_coordinates,
            auth_user=user_1,
        )

        _, call_kwargs = static_map_get_mock.call_args
        assert call_kwargs["headers"] == {
            "User-Agent": f"FitTrackee v{VERSION}"
        }

    def test_it_calls_line_with_given_coordinates(
        self, app: "Flask", user_1: "User"
    ) -> None:
        with patch(
            "fittrackee.workouts.services.workout_from_file.base_workout_with_segment_service.Line",
            return_value=Line(track_points_part_1_coordinates, "#3388FF", 4),
        ) as line_mock:
            BaseWorkoutWithSegmentsCreationService.generate_map_image(
                map_filepath="/tmp/map.png",
                coordinates=track_points_part_1_coordinates,
                auth_user=user_1,
            )

        line_mock.assert_called_once_with(
            coords=track_points_part_1_coordinates, color="#3388FF", width=4
        )
