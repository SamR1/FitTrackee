from typing import TYPE_CHECKING, List, Optional, Union

import numpy as np

from fittrackee.constants import ElevationProcessing

if TYPE_CHECKING:
    import pandas as pd

WINDOW_LEN = 51


class ElevationMixin:
    """
    For now, only flat window-based smoothing is available.
    """

    @staticmethod
    def smooth_with_flat_window(
        points: Union[List[int], List[float]],
    ) -> Union[List[int], List[float]]:
        """
        smooth elevations using 'flat' window

        based on SciPy Cookbook:
        https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
        """
        if len(points) < 3:
            return points

        points_array = np.array(points)
        window_len = len(points) if len(points) < WINDOW_LEN else WINDOW_LEN

        s = np.r_[
            points_array[window_len - 1 : 0 : -1],
            points_array,
            points_array[-2 : -window_len - 1 : -1],
        ]
        w = np.ones(window_len, "d")
        y = np.convolve(w / w.sum(), s, mode="valid")
        start = window_len // 2 + 1
        end = start + len(points_array)
        smooth_array = y[start:end]

        return [int(p) for p in smooth_array]

    def smooth_elevations(
        self,
        points: Union[List[int], List[float]],
        data_processing: Optional["ElevationProcessing"],
    ) -> Union[List[int], List[float]]:
        if data_processing == ElevationProcessing.FLAT_WINDOWS:
            return self.smooth_with_flat_window(points)

        return points

    def get_smoothed_elevations_from_df(
        self,
        elevation_df: "pd.DataFrame",
        data_processing: Optional["ElevationProcessing"],
    ) -> "pd.DataFrame":
        if elevation_df.empty or data_processing == ElevationProcessing.NONE:
            return elevation_df

        elevations = elevation_df["elevation"].tolist()
        smoothed_elevations = self.smooth_elevations(
            elevations, data_processing
        )
        elevation_df["elevation"] = smoothed_elevations

        return elevation_df
