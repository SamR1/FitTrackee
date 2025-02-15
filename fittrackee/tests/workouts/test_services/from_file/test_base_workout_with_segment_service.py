from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from staticmap import Line, StaticMap

from fittrackee import VERSION
from fittrackee.tests.fixtures.fixtures_workouts import (
    track_points_part_1_coordinates,
)
from fittrackee.tests.mixins import BaseTestMixin
from fittrackee.workouts.services.workout_from_file import (
    BaseWorkoutWithSegmentsCreationService,
)

if TYPE_CHECKING:
    from flask import Flask


class TestBaseWorkoutWithSegmentsCreationServiceGetStaticMapTileServerUrl:
    @pytest.mark.parametrize(
        "input_tile_server_url,"
        "input_tile_server_subdomains,"
        "expected_tile_server_url",
        [
            # tile server without subdomain
            (
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                "",
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            ),
            (
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                "a",
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            ),
            # tile server with subdomain
            (
                "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/"
                "{z}/{x}/{y}.png",
                "a",
                "https://a.tile-cyclosm.openstreetmap.fr/cyclosm/"
                "{z}/{x}/{y}.png",
            ),
            (
                "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/"
                "{z}/{x}/{y}.png",
                "",
                "https://tile-cyclosm.openstreetmap.fr/cyclosm/"
                "{z}/{x}/{y}.png",
            ),
        ],
    )
    def test_it_returns_tile_server_url(
        self,
        input_tile_server_url: str,
        input_tile_server_subdomains: str,
        expected_tile_server_url: str,
    ) -> None:
        tile_config = {
            "URL": input_tile_server_url,
            "STATICMAP_SUBDOMAINS": input_tile_server_subdomains,
        }

        assert (
            BaseWorkoutWithSegmentsCreationService.get_static_map_tile_server_url(
                tile_config
            )
            == expected_tile_server_url
        )

    def test_it_returns_tile_server_url_with_random_subdomain(self) -> None:
        """in case multiple subdomains are provided"""
        tile_config = {
            "URL": (
                "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/"
                "{z}/{x}/{y}.png"
            ),
            "STATICMAP_SUBDOMAINS": "a,b,c",
        }

        with patch("random.choice", return_value="b"):
            assert (
                BaseWorkoutWithSegmentsCreationService.get_static_map_tile_server_url(
                    tile_config
                )
                == (
                    "https://b.tile-cyclosm.openstreetmap.fr/cyclosm/"
                    "{z}/{x}/{y}.png"
                )
            )


class TestBaseWorkoutWithSegmentsCreationServiceGenerateMapImage(
    BaseTestMixin
):
    def test_it_calls_staticmap_to_generate_map_image(
        self, app: "Flask"
    ) -> None:
        with patch(
            "fittrackee.workouts.services.workout_from_file.base_workout_with_segment_service.StaticMap",
            return_value=StaticMap(400, 225, 10),
        ) as static_map_mock:
            BaseWorkoutWithSegmentsCreationService.generate_map_image(
                map_filepath="/tmp/map.png",
                coordinates=track_points_part_1_coordinates,
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
        static_map_get_mock: MagicMock,
    ) -> None:
        BaseWorkoutWithSegmentsCreationService.generate_map_image(
            map_filepath="/tmp/map.png",
            coordinates=track_points_part_1_coordinates,
        )

        call_args = self.get_args(static_map_get_mock.call_args)
        assert (
            app.config["TILE_SERVER"]["URL"]
            .replace("{s}.", "")
            .replace("/{z}/{x}/{y}.png", "")
            in call_args[0]
        )

    def test_it_calls_default_tile_server_for_static_map_when_default_static_map_to_true(  # noqa
        self,
        app_default_static_map: "Flask",
        static_map_get_mock: MagicMock,
    ) -> None:
        BaseWorkoutWithSegmentsCreationService.generate_map_image(
            map_filepath="/tmp/map.png",
            coordinates=track_points_part_1_coordinates,
        )

        call_args = self.get_args(static_map_get_mock.call_args)
        assert (
            app_default_static_map.config["TILE_SERVER"]["URL"]
            .replace("{s}.", "")
            .replace("/{z}/{x}/{y}.png", "")
            not in call_args[0]
        )

    def test_it_calls_static_map_with_fittrackee_user_agent(
        self,
        app: "Flask",
        static_map_get_mock: MagicMock,
    ) -> None:
        BaseWorkoutWithSegmentsCreationService.generate_map_image(
            map_filepath="/tmp/map.png",
            coordinates=track_points_part_1_coordinates,
        )

        call_kwargs = self.get_kwargs(static_map_get_mock.call_args)

        assert call_kwargs["headers"] == {
            "User-Agent": f"FitTrackee v{VERSION}"
        }

    def test_it_calls_line_with_given_coordinates(self, app: "Flask") -> None:
        with patch(
            "fittrackee.workouts.services.workout_from_file.base_workout_with_segment_service.Line",
            return_value=Line(track_points_part_1_coordinates, "#3388FF", 4),
        ) as line_mock:
            BaseWorkoutWithSegmentsCreationService.generate_map_image(
                map_filepath="/tmp/map.png",
                coordinates=track_points_part_1_coordinates,
            )

        line_mock.assert_called_once_with(
            coords=track_points_part_1_coordinates, color="#3388FF", width=4
        )
