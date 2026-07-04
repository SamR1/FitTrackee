from typing import TYPE_CHECKING, List

import numpy as np

if TYPE_CHECKING:
    import pandas as pd

WINDOW_LEN = 51


class ElevationMixin:
    @staticmethod
    def smooth_elevations(points: List[int]) -> List[int]:
        """
        smooth elevations using 'flat' window

        based on SciPy Cookbook:
        https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
        """
        if len(points) < 3:
            return [int(p) for p in points]

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

    def get_smoothed_elevations_from_df(
        self, elevation_df: "pd.DataFrame"
    ) -> "pd.DataFrame":
        if elevation_df.empty:
            return elevation_df

        elevations = elevation_df["elevation"].tolist()
        smoothed_elevations = self.smooth_elevations(elevations)
        elevation_df["elevation"] = smoothed_elevations

        return elevation_df
