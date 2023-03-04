import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from zipfile import ZipFile

from flask import current_app

from fittrackee import appLog, db
from fittrackee.emails.tasks import data_export_email
from fittrackee.files import get_absolute_file_path

from .models import User, UserDataExport
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
            os.path.join('exports', str(self.user.id))
        )
        os.makedirs(self.export_directory, exist_ok=True)
        self.workouts_directory = get_absolute_file_path(
            os.path.join('workouts', str(self.user.id))
        )

    def get_user_info(self) -> Dict:
        return self.user.serialize(self.user)

    def get_user_workouts_data(self) -> List[Dict]:
        workouts_data = []
        for workout in self.user.workouts:
            workout_data = workout.get_workout_data()
            workout_data["sport_label"] = workout.sport.label
            workout_data["gpx"] = (
                workout.gpx.split('/')[-1] if workout.gpx else None
            )
            workouts_data.append(workout_data)
        return workouts_data

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
            zip_file = f"archive_{secrets.token_urlsafe(15)}.zip"
            zip_path = os.path.join(self.export_directory, zip_file)
            with ZipFile(zip_path, 'w') as zip_object:
                zip_object.write(user_data_file_name, "user_data.json")
                zip_object.write(
                    workout_data_file_name, "user_workouts_data.json"
                )
                if self.user.picture:
                    picture_path = get_absolute_file_path(self.user.picture)
                    if os.path.isfile(picture_path):
                        zip_object.write(
                            picture_path, self.user.picture.split('/')[-1]
                        )
                if os.path.exists(self.workouts_directory):
                    for file in os.listdir(self.workouts_directory):
                        if os.path.isfile(
                            os.path.join(self.workouts_directory, file)
                        ) and file.endswith('.gpx'):
                            zip_object.write(
                                os.path.join(self.workouts_directory, file),
                                f"gpx/{file}",
                            )

            file_exists = os.path.exists(zip_path)
            os.remove(user_data_file_name)
            os.remove(workout_data_file_name)
            return (zip_path, zip_file) if file_exists else (None, None)
        except Exception as e:
            appLog.error(f'Error when generating user data archive: {str(e)}')
            return None, None


def export_user_data(export_request_id: int) -> None:
    export_request = UserDataExport.query.filter_by(
        id=export_request_id
    ).first()

    if not export_request:
        appLog.error(f"No export to process for id '{export_request_id}'")
        return

    if export_request.completed:
        appLog.info(f"Export id '{export_request_id}' already processed")
        return

    user = User.query.filter_by(id=export_request.user_id).first()
    exporter = UserDataExporter(user)
    archive_file_path, archive_file_name = exporter.generate_archive()

    try:
        export_request.completed = True
        if archive_file_name and archive_file_path:
            export_request.file_name = archive_file_name
            export_request.file_size = os.path.getsize(archive_file_path)
            db.session.commit()

            if current_app.config['CAN_SEND_EMAILS']:
                ui_url = current_app.config['UI_URL']
                email_data = {
                    'username': user.username,
                    'fittrackee_url': ui_url,
                    'account_url': f'{ui_url}/profile/edit/account',
                }
                user_data = {
                    'language': get_language(user.language),
                    'email': user.email,
                }
                data_export_email.send(user_data, email_data)
        else:
            db.session.commit()
    except Exception as e:
        appLog.error(f'Error when exporting user data: {str(e)}')


def clean_user_data_export(days: int) -> Dict:
    counts = {"deleted_requests": 0, "deleted_archives": 0, "freed_space": 0}
    limit = datetime.now() - timedelta(days=days)
    export_requests = UserDataExport.query.filter(
        UserDataExport.created_at < limit,
        UserDataExport.completed == True,  # noqa
    ).all()

    if not export_requests:
        return counts

    archive_directory = get_absolute_file_path("exports")
    for request in export_requests:
        if request.file_name:
            archive_path = os.path.join(
                archive_directory, f"{request.user_id}", request.file_name
            )
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
        db.session.query(UserDataExport)
        .filter(UserDataExport.completed == False)  # noqa
        .order_by(UserDataExport.created_at)
        .limit(max_count)
        .all()
    )

    for export_request in export_requests:
        export_user_data(export_request.id)
        count += 1

    return count
