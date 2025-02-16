import os
import secrets
import zipfile
from dataclasses import dataclass
from io import BytesIO
from typing import IO, TYPE_CHECKING, Dict, List, Optional, Type, Union

import pytz
from flask import current_app

from fittrackee.equipments.exceptions import InvalidEquipmentsException
from fittrackee.files import get_absolute_file_path
from fittrackee.visibility_levels import (
    VisibilityLevel,
    get_calculated_visibility,
)
from fittrackee.workouts.models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
    TITLE_MAX_CHARACTERS,
)

from ..exceptions import WorkoutException, WorkoutFileException
from .base_workout_service import BaseWorkoutService
from .workout_from_file import WorkoutGpxCreationService

if TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage

    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout

    from .workout_from_file import BaseWorkoutWithSegmentsCreationService


WORKOUT_FROM_FILE_SERVICES: Dict[
    str, Type["BaseWorkoutWithSegmentsCreationService"]
] = {
    "gpx": WorkoutGpxCreationService,
}


@dataclass
class WorkoutsData:
    sport_id: int
    analysis_visibility: Optional[VisibilityLevel] = None
    description: Optional[str] = None
    equipment_ids: Optional[List[str]] = None
    map_visibility: Optional[VisibilityLevel] = None
    notes: Optional[str] = None
    title: Optional[str] = None
    workout_visibility: Optional[VisibilityLevel] = None


class WorkoutsFromFileCreationService(BaseWorkoutService):
    def __init__(
        self,
        auth_user: "User",
        workouts_data: Dict,
        file: Optional["FileStorage"] = None,
    ):
        super().__init__(
            auth_user,
            workouts_data.get("sport_id"),
            workouts_data.get("equipment_ids"),
        )
        self.file: Optional["FileStorage"] = file
        self.workouts_data = WorkoutsData(**workouts_data)

    def _get_user_path(
        self,
    ) -> str:
        user_path = os.path.join("workouts", str(self.auth_user.id))
        absolute_user_path = get_absolute_file_path(user_path)
        if not os.path.exists(absolute_user_path):
            os.makedirs(absolute_user_path)
        return user_path

    def get_file_path(
        self,
        workout_date: str,
        extension: str,
    ) -> str:
        suffix = secrets.token_urlsafe(8)
        new_filename = (
            f"{workout_date}_{self.workouts_data.sport_id}_{suffix}{extension}"
        )
        dir_path = self._get_user_path()
        file_path = os.path.join(dir_path, new_filename.split("/")[-1])
        return file_path

    def create_workout_from_file(
        self,
        extension: str,
        equipments: Union[List["Equipment"], None],
        workout_file: Optional["IO[bytes]"] = None,
    ) -> "Workout":
        """
        Return map absolute file path in order to delete file on error
        """
        if workout_file is None and self.file is None:
            raise WorkoutException("error", "no workout file provided")

        workout_service = WORKOUT_FROM_FILE_SERVICES[extension](
            auth_user=self.auth_user,
            workout_file=(
                self.file.stream  # type: ignore
                if workout_file is None
                else workout_file
            ),
            sport_id=self.workouts_data.sport_id,
            stopped_speed_threshold=self.stopped_speed_threshold,
        )

        # extract and calculate data from provided file
        new_workout = workout_service.process_workout()

        # store title, description and notes
        title = (
            self.workouts_data.title
            if self.workouts_data.title
            else workout_service.workout_name
            if workout_service.workout_name
            else ""
        )
        if title:
            new_workout.title = title[:TITLE_MAX_CHARACTERS]
        else:
            workout_datetime = (
                new_workout.workout_date.astimezone(
                    pytz.timezone(self.auth_user.timezone)
                )
                if self.auth_user.timezone
                else new_workout.workout_date
            ).strftime("%Y-%m-%d %H:%M:%S")
            new_workout.title = f"{self.sport.label} - {workout_datetime}"

        new_workout.description = (
            self.workouts_data.description[:DESCRIPTION_MAX_CHARACTERS]
            if self.workouts_data.description
            else workout_service.workout_description[
                :DESCRIPTION_MAX_CHARACTERS
            ]
            if workout_service.workout_description
            else None
        )
        new_workout.notes = (
            None
            if self.workouts_data.notes is None
            else self.workouts_data.notes[:NOTES_MAX_CHARACTERS]
        )

        # add equipments if ids provided
        if equipments is not None:
            new_workout.equipments = equipments

        # update visibility
        new_workout.workout_visibility = (
            self.workouts_data.workout_visibility
            if self.workouts_data.workout_visibility
            else self.auth_user.workouts_visibility
        )
        new_workout.analysis_visibility = get_calculated_visibility(
            visibility=(
                self.workouts_data.analysis_visibility
                if self.workouts_data.analysis_visibility
                else self.auth_user.analysis_visibility
            ),
            parent_visibility=new_workout.workout_visibility,
        )
        new_workout.map_visibility = get_calculated_visibility(
            visibility=(
                self.workouts_data.map_visibility
                if self.workouts_data.map_visibility
                else self.auth_user.map_visibility
            ),
            parent_visibility=new_workout.analysis_visibility,
        )

        # store workout file
        if self.file:
            workout_filepath = self.get_file_path(
                workout_date=new_workout.workout_date.strftime(
                    "%Y-%m-%d_%H-%M-%S"
                ),
                extension=".gpx",
            )
            new_workout.gpx = workout_filepath
            absolute_workout_filepath = get_absolute_file_path(
                workout_filepath
            )
            try:
                self.file.stream.seek(0)
                self.file.save(absolute_workout_filepath)
            except Exception as e:
                raise WorkoutException(
                    "error", "error when storing gpx file"
                ) from e

        # generate and store map image
        map_filepath = self.get_file_path(
            workout_date=new_workout.workout_date.strftime(
                "%Y-%m-%d_%H-%M-%S"
            ),
            extension=".png",
        )
        new_workout.map = map_filepath
        absolute_map_filepath = get_absolute_file_path(map_filepath)
        try:
            workout_service.generate_map_image(
                map_filepath=absolute_map_filepath,
                coordinates=workout_service.coordinates,
            )
            new_workout.map_id = workout_service.get_map_hash(map_filepath)
        except Exception as e:
            if os.path.exists(absolute_map_filepath):
                os.remove(absolute_map_filepath)
            if os.path.exists(absolute_workout_filepath):
                os.remove(absolute_workout_filepath)
            raise WorkoutException(
                "error", "error when generating map image"
            ) from e
        return new_workout

    @staticmethod
    def _get_extension(filename: str) -> str:
        return filename.rsplit(".", 1)[-1].lower()

    def _is_workout_file(self, filename: str) -> bool:
        extension = self._get_extension(filename)
        return (
            extension in current_app.config["WORKOUT_ALLOWED_EXTENSIONS"]
            and extension != "zip"
        )

    def get_files_from_archive(self) -> List[str]:
        if not self.file:
            raise WorkoutException("error", "no workout file provided")
        files_to_process = []
        max_file_size = current_app.config["max_single_file_size"]
        try:
            with zipfile.ZipFile(self.file.stream, "r") as zip_ref:
                for zip_info in zip_ref.infolist():
                    if self._is_workout_file(zip_info.filename):
                        if zip_info.file_size > max_file_size:
                            raise WorkoutFileException(
                                "fail",
                                (
                                    "at least one file in zip archive "
                                    "exceeds size limit, "
                                    "please check the archive"
                                ),
                            )
                        files_to_process.append(zip_info.filename)

                        if (
                            len(files_to_process)
                            > current_app.config["gpx_limit_import"]
                        ):
                            raise WorkoutFileException(
                                "fail",
                                (
                                    "the number of files in the archive "
                                    "exceeds the limit"
                                ),
                            )

        except zipfile.BadZipFile as e:
            raise WorkoutFileException("error", "invalid zip file") from e

        if not files_to_process:
            raise WorkoutFileException(
                "fail", "archive does not contain valid workout files"
            )

        return files_to_process

    def process_zip_archive(
        self, equipments: Union[List["Equipment"], None]
    ) -> List["Workout"]:
        if not self.file:
            raise WorkoutException("error", "no workout file provided")
        files_to_process = self.get_files_from_archive()
        new_workouts = []

        # handle Python < 3.11, see:
        # - https://github.com/python/cpython/issues/70363
        # - https://docs.python.org/3.11/whatsnew/3.11.html#tempfile
        if not hasattr(self.file.stream, "seekable"):
            archive_content: Union[BytesIO, IO[bytes]] = BytesIO(
                self.file.getvalue()
            )
        else:
            archive_content = self.file.stream

        try:
            with zipfile.ZipFile(archive_content, "r") as zip_ref:
                for file in files_to_process:
                    extension = self._get_extension(file)
                    file_content = zip_ref.open(file)
                    new_workouts.append(
                        self.create_workout_from_file(
                            extension, equipments, file_content
                        )
                    )
        except WorkoutFileException as e:
            raise e
        except Exception as e:
            for workout in new_workouts:
                if workout.gpx and os.path.exists(
                    get_absolute_file_path(workout.gpx)
                ):
                    os.remove(get_absolute_file_path(workout.gpx))
                if workout.map and os.path.exists(
                    get_absolute_file_path(workout.map)
                ):
                    os.remove(get_absolute_file_path(workout.map))
            raise WorkoutException(
                "error", "error when processing archive"
            ) from e
        return new_workouts

    def process(self) -> List["Workout"]:
        if self.file is None:
            raise WorkoutException("error", "no workout file provided")
        if self.file.filename is None:
            raise WorkoutFileException("error", "workout file has no filename")

        extension = self._get_extension(self.file.filename)
        if extension not in current_app.config["WORKOUT_ALLOWED_EXTENSIONS"]:
            raise WorkoutFileException(
                "error", "workout file invalid extension"
            )
        equipments = self.get_equipments()

        try:
            if extension == "zip":
                return self.process_zip_archive(equipments)
            else:
                new_workout = self.create_workout_from_file(
                    extension, equipments
                )
                return [new_workout]
        except InvalidEquipmentsException as e:
            raise WorkoutException("error", str(e)) from e
