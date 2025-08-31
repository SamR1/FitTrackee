from typing import TYPE_CHECKING, Dict, Type

from fittrackee.workouts.services import (
    WorkoutFitService,
    WorkoutGpxService,
    WorkoutKmlService,
    WorkoutKmzService,
    WorkoutTcxService,
)

if TYPE_CHECKING:
    from fittrackee.workouts.services.workout_from_file import (
        BaseWorkoutWithSegmentsCreationService,
    )

WORKOUT_FROM_FILE_SERVICES: Dict[
    str, Type["BaseWorkoutWithSegmentsCreationService"]
] = {
    "gpx": WorkoutGpxService,
    "fit": WorkoutFitService,
    "kml": WorkoutKmlService,
    "kmz": WorkoutKmzService,
    "tcx": WorkoutTcxService,
}
