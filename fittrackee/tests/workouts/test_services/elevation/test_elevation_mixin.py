import numpy as np
import pytest

from fittrackee.constants import ElevationProcessing
from fittrackee.tests.fixtures.fixtures_workouts import (
    ELEVATIONS,
    SMOOTHED_ELEVATION_WITH_FLAT_WINDOW,
)
from fittrackee.workouts.services.elevation.elevation_mixin import (
    ElevationMixin,
)
from fittrackee.workouts.services.elevation.exceptions import (
    ElevationException,
)


class TestElevationSmoothWithFlatWindows:
    def test_it_returns_elevation_unchanged_when_length_below_3(self) -> None:
        elevations = ElevationMixin.smooth_with_flat_window(ELEVATIONS[:2])

        assert elevations == ELEVATIONS[:2]

    def test_it_returns_smoothed_elevation(self) -> None:
        elevations = ElevationMixin.smooth_with_flat_window(ELEVATIONS)

        assert elevations == SMOOTHED_ELEVATION_WITH_FLAT_WINDOW

    def test_it_raises_exception_when_elevations_are_none(self) -> None:
        with pytest.raises(ElevationException):
            ElevationMixin.smooth_with_flat_window([None, None, None, None])

    def test_it_raises_exception_when_value_is_nan(self) -> None:
        with pytest.raises(ElevationException):
            ElevationMixin.smooth_with_flat_window(
                [998.0, 996.0, np.nan, 998.0]
            )

    def test_it_raises_exception_when_value_is_None(self) -> None:
        with pytest.raises(ElevationException):
            ElevationMixin.smooth_with_flat_window([998.0, None, 996.0, 998.0])


class TestElevationSmoothElevations:
    def test_it_smoothes_with_flat_window(self) -> None:
        elevations = ElevationMixin().smooth_elevations(
            ELEVATIONS, ElevationProcessing.FLAT_WINDOW
        )
        assert elevations == SMOOTHED_ELEVATION_WITH_FLAT_WINDOW

    def test_it_does_not_smooth_elevation(self) -> None:
        elevations = ElevationMixin().smooth_elevations(
            ELEVATIONS, ElevationProcessing.NONE
        )
        assert elevations == ELEVATIONS
