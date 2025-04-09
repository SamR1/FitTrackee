import os
import secrets
import tempfile
import zipfile
from abc import abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from io import BytesIO
from typing import IO, TYPE_CHECKING, Dict, List, Optional, Tuple, Type, Union

from flask import current_app

from fittrackee import db
from fittrackee.equipments.exceptions import InvalidEquipmentsException
from fittrackee.equipments.models import Equipment
from fittrackee.files import get_absolute_file_path
from fittrackee.users.models import User, UserTask
from fittrackee.visibility_levels import get_calculated_visibility
from fittrackee.workouts.models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
)

from ..exceptions import WorkoutException, WorkoutFileException
from .base_workout_service import BaseWorkoutService
from .workout_from_file import WorkoutGpxCreationService

if TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage

    from fittrackee.visibility_levels import VisibilityLevel
    from fittrackee.workouts.models import Workout

    from .workout_from_file import BaseWorkoutWithSegmentsCreationService

WORKOUT_FROM_FILE_SERVICES: Dict[
    str, Type["BaseWorkoutWithSegmentsCreationService"]
] = {
    "gpx": WorkoutGpxCreationService,
}
NO_FILE_ERROR_MESSAGE = "no workout file provided"


@dataclass
class WorkoutsData:
    sport_id: int
    analysis_visibility: Optional["VisibilityLevel"] = None
    description: Optional[str] = None
    equipment_ids: Optional[List[str]] = None
    map_visibility: Optional["VisibilityLevel"] = None
    notes: Optional[str] = None
    title: Optional[str] = None
    workout_visibility: Optional["VisibilityLevel"] = None


class AbstractWorkoutsCreationService(BaseWorkoutService):
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

    @abstractmethod
    def process(self) -> Tuple[List["Workout"], Dict]:
        pass

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

    def _get_workout_title(
        self, service_workout_name: Optional[str], workout_date: datetime
    ) -> Optional[str]:
        title = ""
        if self.workouts_data.title:
            title = self.workouts_data.title
        elif service_workout_name:
            title = service_workout_name
        return self._get_title(workout_date, title)

    def _get_workout_description(
        self, service_workout_description: Optional[str]
    ) -> Optional[str]:
        if self.workouts_data.description:
            return self.workouts_data.description[:DESCRIPTION_MAX_CHARACTERS]

        if service_workout_description:
            return service_workout_description[:DESCRIPTION_MAX_CHARACTERS]

        return None

    def _get_workout_notes(self) -> Optional[str]:
        if self.workouts_data.notes is None:
            return None
        return self.workouts_data.notes[:NOTES_MAX_CHARACTERS]

    def _store_file(
        self, new_workout: "Workout", workout_file: Optional["IO[bytes]"]
    ) -> str:
        if not workout_file and not self.file:
            return ""

        workout_filepath = self.get_file_path(
            workout_date=new_workout.workout_date.strftime(
                "%Y-%m-%d_%H-%M-%S"
            ),
            extension=".gpx",
        )
        new_workout.gpx = workout_filepath
        absolute_workout_filepath = get_absolute_file_path(workout_filepath)
        try:
            if workout_file:  # when file from archive
                with open(absolute_workout_filepath, "wb") as f:
                    workout_file.seek(0)
                    f.write(workout_file.read())
            elif self.file:
                self.file.stream.seek(0)
                self.file.save(absolute_workout_filepath)
            else:
                return ""
        except Exception as e:
            raise WorkoutException(
                "error", "error when storing gpx file"
            ) from e
        return absolute_workout_filepath

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
            raise WorkoutException("error", NO_FILE_ERROR_MESSAGE)

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
        new_workout.title = self._get_workout_title(
            workout_service.workout_name, new_workout.workout_date
        )
        new_workout.description = self._get_workout_description(
            workout_service.workout_description
        )
        new_workout.notes = self._get_workout_notes()

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
        absolute_workout_filepath = self._store_file(new_workout, workout_file)

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
        db.session.commit()
        return new_workout

    @staticmethod
    def _get_extension(filename: str) -> str:
        return filename.rsplit(".", 1)[-1].lower()

    def process_archive_content(
        self,
        archive_content: Union[BytesIO, IO[bytes]],
        files_to_process: List[str],
        equipments: Union[List["Equipment"], None],
        upload_task: Optional["UserTask"] = None,
    ) -> Tuple[List["Workout"], Dict]:
        if not files_to_process:
            raise WorkoutFileException(
                "error", "No files from archive to process"
            )

        new_workouts = []
        errored_workouts = {}
        total_files = len(files_to_process)
        with zipfile.ZipFile(archive_content, "r") as zip_ref:
            for index, file in enumerate(files_to_process, start=1):
                try:
                    extension = self._get_extension(file)
                    file_content = zip_ref.open(file)
                    new_workout = self.create_workout_from_file(
                        extension, equipments, file_content
                    )
                except Exception as e:
                    db.session.rollback()
                    errored_workouts[file] = e.args[0]
                    if upload_task:
                        upload_task.progress = int(100 * index / total_files)
                        db.session.commit()
                    continue

                new_workouts.append(new_workout)
                if upload_task:
                    upload_task.progress = int(100 * index / total_files)
                    db.session.commit()

        return new_workouts, errored_workouts


class WorkoutsFromFileCreationService(AbstractWorkoutsCreationService):
    def __init__(
        self,
        auth_user: "User",
        workouts_data: Dict,
        file: Optional["FileStorage"] = None,
    ):
        super().__init__(auth_user, workouts_data, file)

    def _is_workout_file(self, filename: str) -> bool:
        extension = self._get_extension(filename)
        return (
            extension in current_app.config["WORKOUT_ALLOWED_EXTENSIONS"]
            and extension != "zip"
        )

    def get_files_from_archive(self) -> List[str]:
        if not self.file:
            raise WorkoutException("error", NO_FILE_ERROR_MESSAGE)
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
                            > current_app.config["file_limit_import"]
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

    def _get_archive_content(self) -> Union[BytesIO, IO[bytes]]:
        if not self.file:
            raise WorkoutException("error", NO_FILE_ERROR_MESSAGE)

        # handle Python < 3.11, see:
        # - https://github.com/python/cpython/issues/70363
        # - https://docs.python.org/3.11/whatsnew/3.11.html#tempfile
        if not hasattr(self.file.stream, "seekable"):
            return BytesIO(self.file.getvalue())
        return self.file.stream

    def add_workouts_upload_task(
        self,
        files_to_process: List[str],
        equipments: Union[List["Equipment"], None],
    ) -> str:
        from fittrackee.workouts.tasks import upload_workouts_archive

        if self.file is None:
            raise WorkoutException("error", NO_FILE_ERROR_MESSAGE)
        if not files_to_process:
            raise WorkoutFileException(
                "error", "No files from archive to process"
            )
        if UserTask.query.filter(
            UserTask.user_id == self.auth_user.id,
            UserTask.task_type == "workouts_archive_upload",
            UserTask.errored != True,  # noqa
            UserTask.progress != 100,
        ).first():
            raise WorkoutException("invalid", "ongoing upload task exists")

        _, path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        self.file.stream.seek(0)
        self.file.save(path)

        upload_task = UserTask(
            user_id=self.auth_user.id,
            task_type="workouts_archive_upload",
            data={
                "workouts_data": asdict(self.workouts_data),
                "files_to_process": files_to_process,
                "new_workouts_count": 0,
                "equipment_ids": (
                    None
                    if equipments is None
                    else [equipment.short_id for equipment in equipments]
                ),
            },
            file_path=path,
        )
        upload_task.errors = {
            "archive": None,
            "files": {},
        }
        db.session.add(upload_task)
        db.session.commit()

        upload_workouts_archive.send(task_id=upload_task.id)
        return upload_task.short_id

    def process_zip_archive(
        self, equipments: Union[List["Equipment"], None]
    ) -> Tuple[List["Workout"], Dict]:
        if not self.file:
            raise WorkoutException("error", NO_FILE_ERROR_MESSAGE)
        files_to_process = self.get_files_from_archive()
        if (
            len(files_to_process)
            > current_app.config["file_sync_limit_import"]
        ):
            task_short_id = self.add_workouts_upload_task(
                files_to_process, equipments
            )
            return [], {"task_short_id": task_short_id}

        new_workouts, errored_workouts = self.process_archive_content(
            archive_content=self._get_archive_content(),
            files_to_process=files_to_process,
            equipments=equipments,
        )
        return new_workouts, {
            "errored_workouts": errored_workouts,
            "task_short_id": None,
        }

    def process(self) -> Tuple[List["Workout"], Dict]:
        if self.file is None:
            raise WorkoutException("error", NO_FILE_ERROR_MESSAGE)
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
                new_workouts, processing_output = self.process_zip_archive(
                    equipments
                )
                return new_workouts, processing_output
            else:
                new_workout = self.create_workout_from_file(
                    extension, equipments
                )
                return [new_workout], {
                    "task_short_id": None,
                    "errored_workouts": [],
                }
        except InvalidEquipmentsException as e:
            raise WorkoutException("error", str(e)) from e


class WorkoutsFromArchiveCreationAsyncService(AbstractWorkoutsCreationService):
    def __init__(
        self,
        task_id: int,
    ) -> None:
        upload_task = UserTask.query.filter_by(id=task_id).first()
        if (
            not upload_task
            or upload_task.task_type != "workouts_archive_upload"
        ):
            raise WorkoutException("error", "no import task found")
        auth_user = User.query.filter_by(id=upload_task.user_id).one()
        import_data = upload_task.data
        super().__init__(auth_user, import_data["workouts_data"], None)
        self.file_path = upload_task.file_path
        self.files_to_process = import_data["files_to_process"]
        self.equipment_ids = import_data["equipment_ids"]
        self.upload_task = upload_task

    def process(self) -> Tuple[List["Workout"], Dict]:
        if self.equipment_ids is None:
            equipments = None
        elif not self.equipment_ids:
            equipments = []
        else:
            equipments = Equipment.query.filter(
                Equipment.id.in_(self.equipment_ids)
            ).all()

        errored_workouts: Dict = {}
        new_workouts: List["Workout"] = []
        try:
            with open(self.file_path, "rb") as zip_file:
                new_workouts, errored_workouts = self.process_archive_content(
                    archive_content=zip_file,
                    files_to_process=self.files_to_process,
                    equipments=equipments,
                    upload_task=self.upload_task,
                )
        except FileNotFoundError:
            self.upload_task.errored = True
            self.upload_task.errors = {
                **self.upload_task.errors,
                "archive": "archive file does not exist",
            }

        self.upload_task.data = {
            **self.upload_task.data,
            "new_workouts_count": len(new_workouts),
        }

        if errored_workouts:
            self.upload_task.errored = True
            self.upload_task.errors = {
                **self.upload_task.errors,
                "files": errored_workouts,
            }

        if os.path.exists(self.file_path):
            os.remove(self.file_path)

        db.session.commit()
        return new_workouts, {
            "errored_workouts": errored_workouts,
            "task_short_id": self.upload_task.short_id,
        }
