from fittrackee.constants import ElevationProcessing
from fittrackee.tests.fixtures.fixtures_workouts import (
    ELEVATIONS,
    SMOOTHED_ELEVATION_WITH_FLAT_WINDOWS,
    SMOOTHED_ELEVATION_WITH_SAVITZKY_GOLAY_FILTER,
)
from fittrackee.workouts.services.elevation.elevation_mixin import (
    ElevationMixin,
)


class TestElevationSmoothWithFlatWindows:
    def test_it_returns_elevation_unchanged_when_length_below_3(self) -> None:
        elevations = ElevationMixin.smooth_with_flat_window(ELEVATIONS[:2])

        assert elevations == ELEVATIONS[:2]

    def test_it_returns_smoothed_elevation(self) -> None:
        elevations = ElevationMixin.smooth_with_flat_window(ELEVATIONS)

        assert elevations == SMOOTHED_ELEVATION_WITH_FLAT_WINDOWS


class TestElevationSmoothWithSavitzkyGolayFilter:
    def test_it_returns_elevation_unchanged_when_length_below_5(self) -> None:
        elevations = ElevationMixin.smooth_with_savitzky_golay_filter(
            ELEVATIONS[:4]
        )

        assert elevations == ELEVATIONS[:4]

    def test_it_returns_smoothed_elevation(self) -> None:
        elevations = ElevationMixin.smooth_with_savitzky_golay_filter(
            ELEVATIONS
        )
        assert elevations == SMOOTHED_ELEVATION_WITH_SAVITZKY_GOLAY_FILTER


class TestElevationSmoothElevations:
    def test_it_smoothes_with_flat_windows(self) -> None:
        elevations = ElevationMixin().smooth_elevations(
            ELEVATIONS, ElevationProcessing.FLAT_WINDOWS
        )
        assert elevations == SMOOTHED_ELEVATION_WITH_FLAT_WINDOWS

    def test_it_smoothes_with_savitzky_golay_filter(self) -> None:
        elevations = ElevationMixin().smooth_elevations(
            ELEVATIONS, ElevationProcessing.SAVITZKY_GOLAY
        )
        assert elevations == SMOOTHED_ELEVATION_WITH_SAVITZKY_GOLAY_FILTER

    def test_it_does_not_smooth_elevation(self) -> None:
        elevations = ElevationMixin().smooth_elevations(
            ELEVATIONS, ElevationProcessing.NONE
        )
        assert elevations == ELEVATIONS
