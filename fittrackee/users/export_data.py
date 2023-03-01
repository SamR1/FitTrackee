import json
import os
import secrets
from typing import Dict, List, Optional, Union
from zipfile import ZipFile

from fittrackee.files import get_absolute_file_path

from .models import User


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

    def generate_archive(self) -> Optional[str]:
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
                for file in os.listdir(self.workouts_directory):
                    if os.path.isfile(
                        os.path.join(self.workouts_directory, file)
                    ) and file.endswith('.gpx'):
                        zip_object.write(
                            os.path.join(self.workouts_directory, file),
                            f"gpx/{file}",
                        )

            file_exists = os.path.exists(zip_path)
            return zip_file if file_exists else None
        except Exception:
            return None
