import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Union
from zipfile import ZipFile

from flask import current_app

from fittrackee import appLog, db
from fittrackee.emails.tasks import send_email
from fittrackee.files import get_absolute_file_path
from fittrackee.utils import decode_short_id
from fittrackee.workouts.constants import WORKOUT_ALLOWED_EXTENSIONS

from .exceptions import UserTaskException
from .models import Notification, User, UserTask
from .utils.language import get_language


class UserDataExporter:
    """
    generates a zip archive with:
    - user info from database (json file)
    - data from database for all workouts if exist (json file)
    - profile picture file if exists
    - gpx files if exist
    """

    def __init__(self, user: User) -> None:
        self.user = user
        self.export_directory = get_absolute_file_path(
            os.path.join("exports", str(self.user.id))
        )
        os.makedirs(self.export_directory, exist_ok=True)
        self.workouts_directory = get_absolute_file_path(
            os.path.join("workouts", str(self.user.id))
        )

    def get_user_info(self) -> Dict:
        return self.user.serialize(current_user=self.user)

    def get_user_workouts_data(self) -> List[Dict]:
        workouts_data = []
        for workout in self.user.workouts:
            workout_data = workout.get_workout_data(
                self.user, additional_data=True, light=False
            )
            workout_data["sport_label"] = workout.sport.label
            workout_data["gpx"] = (
                workout.gpx.split("/")[-1] if workout.gpx else None
            )
            workout_data["original_file"] = (
                workout.original_file.split("/")[-1]
                if workout.original_file
                else None
            )
            workouts_data.append(workout_data)
        return workouts_data

    def get_user_comments_data(self) -> List[Dict]:
        comments_data = []
        for comment in self.user.comments:
            comments_data.append(
                {
                    "created_at": comment.created_at,
                    "id": comment.short_id,
                    "modification_date": comment.modification_date,
                    "text": comment.text,
                    "text_visibility": comment.text_visibility.value,
                    "workout_id": (
                        comment.workout.short_id
                        if comment.workout_id
                        else None
                    ),
                }
            )
        return comments_data

    def get_user_equipments_data(self) -> List[Dict]:
        return [
            equipment.serialize(current_user=self.user)
            for equipment in self.user.equipments
        ]

    def export_data(self, data: Union[Dict, List], name: str) -> str:
        """export data in existing user upload directory"""
        json_object = json.dumps(data, indent=4, default=str)
        file_path = os.path.join(self.export_directory, f"{name}.json")
        with open(file_path, "w") as export_file:
            export_file.write(json_object)
        return file_path

    def generate_archive(self) -> Tuple[Optional[str], Optional[str]]:
        try:
            user_data_file_name = self.export_data(
                self.get_user_info(), "user_data"
            )
            workout_data_file_name = self.export_data(
                self.get_user_workouts_data(), "workouts_data"
            )
            equipments_data_file_name = self.export_data(
                self.get_user_equipments_data(), "equipments_data"
            )
            comments_data_file_name = self.export_data(
                self.get_user_comments_data(), "comments_data"
            )
            zip_file = f"archive_{secrets.token_urlsafe(15)}.zip"
            zip_path = os.path.join(self.export_directory, zip_file)
            with ZipFile(zip_path, "w") as zip_object:
                zip_object.write(user_data_file_name, "user_data.json")
                zip_object.write(
                    workout_data_file_name, "user_workouts_data.json"
                )
                zip_object.write(
                    equipments_data_file_name, "user_equipments_data.json"
                )
                zip_object.write(
                    comments_data_file_name, "user_comments_data.json"
                )
                if self.user.picture:
                    picture_path = get_absolute_file_path(self.user.picture)
                    if os.path.isfile(picture_path):
                        zip_object.write(
                            picture_path, self.user.picture.split("/")[-1]
                        )
                if os.path.exists(self.workouts_directory):
                    for file in os.listdir(self.workouts_directory):
                        extension = file.split(".")[-1]
                        if (
                            extension in WORKOUT_ALLOWED_EXTENSIONS
                            and os.path.isfile(
                                os.path.join(self.workouts_directory, file)
                            )
                        ):
                            zip_object.write(
                                os.path.join(self.workouts_directory, file),
                                f"workout_files/{file}",
                            )

            file_exists = os.path.exists(zip_path)
            os.remove(user_data_file_name)
            os.remove(workout_data_file_name)
            os.remove(equipments_data_file_name)
            os.remove(comments_data_file_name)
            return (zip_path, zip_file) if file_exists else (None, None)
        except Exception as e:
            appLog.error(f"Error when generating user data archive: {e!s}")
            return None, None


def export_user_data(task_id: int) -> None:
    export_request = UserTask.query.filter_by(id=task_id).first()

    if not export_request:
        appLog.error(f"No export to process for id '{task_id}'")
        return

    if export_request.completed:
        appLog.info(f"Export id '{task_id}' already processed")
        return

    user = User.query.filter_by(id=export_request.user_id).one()
    exporter = UserDataExporter(user)

    try:
        archive_file_path, archive_file_name = exporter.generate_archive()
        if archive_file_name and archive_file_path:
            export_request.file_path = os.path.join(
                "exports", str(user.id), archive_file_name
            )
            export_request.file_size = os.path.getsize(archive_file_path)
            db.session.flush()
            export_request.progress = 100

            notification = Notification(
                from_user_id=export_request.user_id,
                to_user_id=export_request.user_id,
                created_at=datetime.now(tz=timezone.utc),
                event_object_id=export_request.id,
                event_type=export_request.task_type,
            )
            db.session.add(notification)
            db.session.commit()

            if current_app.config["CAN_SEND_EMAILS"]:
                fittrackee_url = current_app.config["UI_URL"]
                email_data = {
                    "username": user.username,
                    "fittrackee_url": fittrackee_url,
                    "account_url": f"{fittrackee_url}/profile/edit/account",
                }
                user_data = {
                    "language": get_language(user.language),
                    "email": user.email,
                }
                send_email.send(
                    user_data, email_data, template="data_export_ready"
                )
        else:
            export_request.errored = True
            db.session.commit()

    except Exception as e:
        export_request.errored = True
        db.session.commit()
        appLog.error(f"Error when exporting user data: {e!s}")


def clean_user_data_export(days: int) -> Dict:
    counts = {"deleted_requests": 0, "deleted_archives": 0, "freed_space": 0}
    limit = datetime.now(timezone.utc) - timedelta(days=days)
    export_requests = UserTask.query.filter(
        UserTask.created_at < limit,
        UserTask.progress == 100,
        UserTask.task_type == "user_data_export",
    ).all()

    if not export_requests:
        return counts

    for request in export_requests:
        if request.file_path:
            archive_path = get_absolute_file_path(request.file_path)
            if os.path.exists(archive_path):
                counts["deleted_archives"] += 1
                counts["freed_space"] += request.file_size
        # Archive is deleted when row is deleted
        db.session.delete(request)
        counts["deleted_requests"] += 1

    db.session.commit()
    return counts


def generate_user_data_archives(max_count: int) -> int:
    count = 0
    export_requests = (
        db.session.query(UserTask)
        .filter(
            UserTask.progress != 100,
            UserTask.task_type == "user_data_export",
        )
        .order_by(UserTask.created_at)
        .limit(max_count)
        .all()
    )

    for export_request in export_requests:
        export_user_data(export_request.id)
        count += 1

    return count


def process_queued_data_export(task_short_id: str) -> None:
    try:
        task_id = decode_short_id(task_short_id)
    except Exception as e:
        raise UserTaskException("Invalid task id") from e

    export_request = UserTask.query.filter_by(
        uuid=task_id, task_type="user_data_export"
    ).first()
    if not export_request:
        raise UserTaskException("No task found")
    if (
        export_request.progress > 0
        or export_request.errored
        or export_request.aborted
    ):
        raise UserTaskException("Task is not queued")

    export_user_data(export_request.id)
