import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from unittest.mock import Mock, call, patch

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.tests.comments.mixins import CommentMixin
from fittrackee.users.exceptions import UserTaskException
from fittrackee.users.export_data import (
    UserDataExporter,
    clean_user_data_export,
    export_user_data,
    generate_user_data_archives,
    process_queued_data_export,
)
from fittrackee.users.models import User, UserTask
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ..mixins import RandomMixin, UserTaskMixin
from ..workouts.utils import post_a_workout


class TestUserDataExporterGetUserInfos:
    def test_it_return_serialized_user_as_info_info(
        self, app: Flask, user_1: User
    ) -> None:
        exporter = UserDataExporter(user_1)

        user_data = exporter.get_user_info()

        assert user_data == user_1.serialize(current_user=user_1)


class TestUserDataExporterGetUserWorkoutsData:
    def test_it_returns_empty_list_when_user_has_no_workouts(
        self, app: Flask, user_1: User
    ) -> None:
        exporter = UserDataExporter(user_1)

        workouts_data = exporter.get_user_workouts_data()

        assert workouts_data == []

    def test_it_returns_data_for_workout_without_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        exporter = UserDataExporter(user_1)

        workouts_data = exporter.get_user_workouts_data()

        assert workouts_data == [
            {
                "id": workout_cycling_user_1.short_id,
                "sport_id": sport_1_cycling.id,
                "sport_label": sport_1_cycling.label,
                "title": workout_cycling_user_1.title,
                "creation_date": workout_cycling_user_1.creation_date,
                "modification_date": workout_cycling_user_1.modification_date,
                "workout_date": workout_cycling_user_1.workout_date,
                "duration": str(workout_cycling_user_1.duration),
                "pauses": None,
                "moving": str(workout_cycling_user_1.moving),
                "distance": workout_cycling_user_1.distance,
                "min_alt": None,
                "max_alt": None,
                "descent": None,
                "ascent": None,
                "max_speed": workout_cycling_user_1.max_speed,
                "ave_speed": workout_cycling_user_1.ave_speed,
                "gpx": None,
                "original_file": None,
                "records": [
                    record.serialize()
                    for record in workout_cycling_user_1.records
                ],
                "segments": [],
                "source": workout_cycling_user_1.source,
                "weather_start": None,
                "weather_end": None,
                "notes": workout_cycling_user_1.notes,
                "equipments": [],
                "description": None,
                "liked": workout_cycling_user_1.liked_by(user_1),
                "likes_count": workout_cycling_user_1.likes.count(),
                "analysis_visibility": (
                    workout_cycling_user_1.calculated_analysis_visibility.value
                ),
                "map_visibility": (
                    workout_cycling_user_1.calculated_map_visibility.value
                ),
                "workout_visibility": (
                    workout_cycling_user_1.workout_visibility.value
                ),
                "ave_cadence": None,
                "max_cadence": None,
                "ave_hr": None,
                "max_hr": None,
            }
        ]

    def test_it_returns_data_for_workout_with_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        _, workout_short_id = post_a_workout(app, gpx_file)
        workout = Workout.query.one()
        exporter = UserDataExporter(user_1)

        workouts_data = exporter.get_user_workouts_data()

        assert workouts_data == [
            {
                "id": workout.short_id,
                "sport_id": sport_1_cycling.id,
                "sport_label": sport_1_cycling.label,
                "title": workout.title,
                "creation_date": workout.creation_date,
                "modification_date": workout.modification_date,
                "workout_date": workout.workout_date,
                "duration": str(workout.duration),
                "pauses": None,
                "moving": str(workout.moving),
                "distance": float(workout.distance),
                "min_alt": float(workout.min_alt),
                "max_alt": float(workout.max_alt),
                "descent": float(workout.descent),
                "ascent": float(workout.ascent),
                "max_speed": float(workout.max_speed),
                "ave_speed": float(workout.ave_speed),
                "gpx": workout.gpx.split("/")[-1],
                "original_file": workout.original_file.split("/")[-1],
                "records": [record.serialize() for record in workout.records],
                "segments": [
                    segment.serialize() for segment in workout.segments
                ],
                "source": workout.source,
                "weather_start": None,
                "weather_end": None,
                "notes": workout.notes,
                "equipments": [],
                "description": None,
                "liked": workout.liked_by(user_1),
                "likes_count": workout.likes.count(),
                "analysis_visibility": (
                    workout.calculated_analysis_visibility.value
                ),
                "map_visibility": workout.calculated_map_visibility.value,
                "workout_visibility": workout.workout_visibility.value,
                "ave_cadence": None,
                "max_cadence": None,
                "ave_hr": None,
                "max_hr": None,
            }
        ]

    def test_it_stores_only_user_workouts(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_2: Workout,
    ) -> None:
        exporter = UserDataExporter(user_1)

        workouts_data = exporter.get_user_workouts_data()

        assert [data["id"] for data in workouts_data] == [
            workout_cycling_user_1.short_id
        ]


class TestUserDataExporterGetUserEquipmentsData:
    def test_it_returns_empty_list_when_no_data_for_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        exporter = UserDataExporter(user_1)

        equipments_data = exporter.get_user_equipments_data()

        assert equipments_data == []

    def test_it_returns_data_for_equipments(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_2: Equipment,
    ) -> None:
        exporter = UserDataExporter(user_1)

        equipments_data = exporter.get_user_equipments_data()

        assert equipments_data == [
            equipment_bike_user_1.serialize(current_user=user_1)
        ]


class TestUserDataExporterGetUserCommentsData(CommentMixin):
    def test_it_returns_empty_list_when_user_has_no_comments(
        self, app: Flask, user_1: User
    ) -> None:
        exporter = UserDataExporter(user_1)

        comments_data = exporter.get_user_comments_data()

        assert comments_data == []

    def test_it_returns_user_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(user_1, workout_cycling_user_1)
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        exporter = UserDataExporter(user_1)

        comments_data = exporter.get_user_comments_data()

        assert comments_data == [
            {
                "created_at": comment.created_at,
                "id": comment.short_id,
                "modification_date": comment.modification_date,
                "text": comment.text,
                "text_visibility": comment.text_visibility.value,
                "workout_id": workout_cycling_user_1.short_id,
            },
        ]

    def test_it_returns_user_comment_without_workout(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)
        db.session.delete(workout_cycling_user_1)
        db.session.commit()
        exporter = UserDataExporter(user_1)

        comments_data = exporter.get_user_comments_data()

        assert comments_data == [
            {
                "created_at": comment.created_at,
                "id": comment.short_id,
                "modification_date": comment.modification_date,
                "text": comment.text,
                "text_visibility": comment.text_visibility.value,
                "workout_id": None,
            },
        ]


class TestUserDataExporterExportData(RandomMixin):
    def test_export_data_generates_json_file_in_user_directory(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        data = {"foo": "bar"}
        export = UserDataExporter(user_1)
        user_directory = os.path.join(
            app.config["UPLOAD_FOLDER"], "exports", str(user_1.id)
        )
        os.makedirs(user_directory, exist_ok=True)
        file_name = self.random_string()

        export.export_data(data, file_name)

        assert (
            os.path.isfile(os.path.join(user_directory, f"{file_name}.json"))
            is True
        )

    def test_it_returns_json_file_path(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        data = {"foo": "bar"}
        exporter = UserDataExporter(user_1)
        user_directory = os.path.join(
            app.config["UPLOAD_FOLDER"], "exports", str(user_1.id)
        )
        file_name = self.random_string()

        file_path = exporter.export_data(data, file_name)

        assert file_path == os.path.join(user_directory, f"{file_name}.json")


class TestUserDataExporterGenerateArchive(RandomMixin):
    @patch.object(secrets, "token_urlsafe", return_value="AOqFRRet8p4")
    @patch.object(UserDataExporter, "export_data")
    @patch("fittrackee.users.export_data.ZipFile")
    def test_it_gets_data_for_each_type(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        exporter = UserDataExporter(user_1)

        exporter.generate_archive()

        export_data.assert_has_calls(
            [
                call(exporter.get_user_info(), "user_data"),
                call(exporter.get_user_workouts_data(), "workouts_data"),
                call(exporter.get_user_equipments_data(), "equipments_data"),
                call(exporter.get_user_comments_data(), "comments_data"),
            ]
        )

    @patch.object(secrets, "token_urlsafe", return_value="AOqFRRet8p4")
    @patch.object(UserDataExporter, "export_data")
    @patch("fittrackee.users.export_data.ZipFile")
    def test_it_calls_zipfile_with_expected_patch(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        exporter = UserDataExporter(user_1)
        token_urlsafe = self.random_string()
        secrets_mock.return_value = token_urlsafe
        expected_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "exports",
            str(user_1.id),
            f"archive_{token_urlsafe}.zip",
        )

        exporter.generate_archive()

        zipfile_mock.assert_called_once_with(expected_path, "w")

    @patch.object(secrets, "token_urlsafe", return_value="AOqFRRet8p4")
    @patch.object(UserDataExporter, "export_data")
    @patch("fittrackee.users.export_data.ZipFile")
    def test_it_calls_zipfile_for_each_json_file(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        exporter = UserDataExporter(user_1)
        token_urlsafe = self.random_string()
        secrets_mock.return_value = token_urlsafe
        export_data.side_effect = [
            call("user_info"),
            call("workouts_data"),
            call("equipments_data"),
            call("comments_data"),
        ]

        exporter.generate_archive()

        # fmt: off
        zipfile_mock.return_value.__enter__\
            .return_value.write.assert_has_calls(
                [
                    call(call('user_info'), 'user_data.json'),
                    call(call('workouts_data'), 'user_workouts_data.json'),
                    call(call('equipments_data'), 'user_equipments_data.json'),
                    call(call('comments_data'), 'user_comments_data.json'),
                ]
            )
        # fmt: on

    @patch.object(secrets, "token_urlsafe", return_value="AOqFRRet8p4")
    @patch.object(UserDataExporter, "export_data")
    @patch("fittrackee.users.export_data.ZipFile")
    def test_it_calls_zipfile_for_gpx_file(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        _, workout_short_id = post_a_workout(app, gpx_file)
        workout = Workout.query.one()
        expected_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            workout.original_file,
        )
        exporter = UserDataExporter(user_1)

        exporter.generate_archive()

        # fmt: off
        zipfile_mock.return_value.__enter__.\
            return_value.write.assert_has_calls(
                [
                    call(
                        expected_path,
                        f"workout_files/{workout.original_file.split('/')[-1]}"
                    ),
                ]
            )
        # fmt: on

    @patch.object(secrets, "token_urlsafe", return_value="AOqFRRet8p4")
    @patch.object(UserDataExporter, "export_data")
    @patch("fittrackee.users.export_data.ZipFile")
    def test_it_calls_zipfile_for_file_different_than_gpx(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        kml_2_3_with_two_tracks: str,
    ) -> None:
        _, workout_short_id = post_a_workout(
            app, kml_2_3_with_two_tracks, extension="kml"
        )
        workout = Workout.query.one()
        kml_expected_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            workout.original_file,
        )
        gpx_expected_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            workout.gpx,
        )
        exporter = UserDataExporter(user_1)

        exporter.generate_archive()

        # fmt: off
        zipfile_mock.return_value.__enter__.\
            return_value.write.assert_has_calls(
                [
                    call(
                        kml_expected_path,
                        f"workout_files/{workout.original_file.split('/')[-1]}"
                    ),
                    call(
                        gpx_expected_path,
                        f"workout_files/{workout.gpx.split('/')[-1]}"
                    ),
                ], any_order=True
            )
        # fmt: on

    @patch.object(secrets, "token_urlsafe")
    @patch.object(UserDataExporter, "export_data")
    @patch("fittrackee.users.export_data.ZipFile")
    def test_it_does_not_call_zipfile_for_another_user_gpx_file(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        _, workout_short_id = post_a_workout(app, gpx_file)
        workout = Workout.query.one()
        expected_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            workout.gpx,
        )
        exporter = UserDataExporter(user_2)

        exporter.generate_archive()

        # fmt: off
        assert (
            call(expected_path, f"gpx/{workout.gpx.split('/')[-1]}")
            not in zipfile_mock.return_value.__enter__.
            return_value.write.call_args_list
        )
        # fmt: on

    @patch.object(secrets, "token_urlsafe")
    @patch.object(UserDataExporter, "export_data")
    @patch("fittrackee.users.export_data.ZipFile")
    def test_it_calls_zipfile_for_profile_image_when_exists(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        user_1.picture = self.random_string()
        expected_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            user_1.picture,
        )
        exporter = UserDataExporter(user_1)

        with patch(
            "fittrackee.users.export_data.os.path.isfile", return_value=True
        ):
            exporter.generate_archive()

        # fmt: off
        zipfile_mock.return_value.__enter__.\
            return_value.write.assert_has_calls(
                [
                    call(expected_path, user_1.picture.split('/')[-1]),
                ]
            )
        # fmt: on

    @patch.object(secrets, "token_urlsafe")
    @patch.object(UserDataExporter, "export_data")
    @patch("fittrackee.users.export_data.ZipFile")
    def test_it_does_not_call_zipfile_for_another_user_profile_image(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        user_1.picture = self.random_string()
        expected_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            user_1.picture,
        )
        exporter = UserDataExporter(user_2)

        with patch(
            "fittrackee.users.export_data.os.path.isfile", return_value=True
        ):
            exporter.generate_archive()

        # fmt: off
        assert (
            call(expected_path, user_1.picture.split('/')[-1])
            not in zipfile_mock.return_value.__enter__.
            return_value.write.call_args_list
        )
        # fmt: on

    @patch.object(secrets, "token_urlsafe")
    def test_it_test_it_generates_a_zip_archive(
        self,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        token_urlsafe = self.random_string()
        secrets_mock.return_value = token_urlsafe
        expected_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "exports",
            str(user_1.id),
            f"archive_{token_urlsafe}.zip",
        )
        exporter = UserDataExporter(user_1)

        exporter.generate_archive()

        assert os.path.isfile(expected_path)

    @patch.object(secrets, "token_urlsafe")
    def test_it_deletes_temporary_files(
        self,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        token_urlsafe = self.random_string()
        secrets_mock.return_value = token_urlsafe
        user_directory = os.path.join(
            app.config["UPLOAD_FOLDER"], "exports", str(user_1.id)
        )
        exporter = UserDataExporter(user_1)

        exporter.generate_archive()

        for file_name in [
            "user_data",
            "workouts_data",
            "equipments_data",
            "comments_data",
        ]:
            assert (
                os.path.isfile(
                    os.path.join(user_directory, f"{file_name}.json")
                )
                is False
            )


@patch("fittrackee.users.export_data.appLog")
@patch.object(UserDataExporter, "generate_archive")
class TestExportUserData(RandomMixin, UserTaskMixin):
    def test_it_logs_error_if_not_request_for_given_id(
        self,
        generate_archive: Mock,
        logger_mock: Mock,
        app: Flask,
    ) -> None:
        request_id = self.random_int()

        export_user_data(task_id=request_id)

        logger_mock.error.assert_called_once_with(
            f"No export to process for id '{request_id}'"
        )

    def test_it_logs_error_if_request_already_processed(
        self,
        generate_archive: Mock,
        logger_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        export_request = self.create_user_data_export_task(
            user_1, progress=100
        )

        export_user_data(task_id=export_request.id)

        logger_mock.info.assert_called_once_with(
            f"Export id '{export_request.id}' already processed"
        )

    def test_it_updates_export_request_when_export_is_successful(
        self,
        generate_archive_mock: Mock,
        logger_mock: Mock,
        export_data_send_email_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        export_request = self.create_user_data_export_task(user_1)
        archive_name = self.random_string()
        generate_archive_mock.return_value = (
            self.random_string(),
            archive_name,
        )
        archive_size = self.random_int()

        with patch(
            "fittrackee.users.export_data.os.path.getsize",
            return_value=archive_size,
        ):
            export_user_data(task_id=export_request.id)

        assert export_request.completed is True
        assert export_request.updated_at is not None
        assert export_request.file_path == (
            f"exports/{user_1.id}/{archive_name}"
        )
        assert export_request.file_size == archive_size

    def test_it_updates_export_request_when_export_fails(
        self,
        generate_archive_mock: Mock,
        logger_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        export_request = self.create_user_data_export_task(user_1)
        generate_archive_mock.return_value = (None, None)

        export_user_data(task_id=export_request.id)

        assert export_request.completed is False
        assert export_request.updated_at is not None
        assert export_request.file_path is None
        assert export_request.file_size is None

    def test_it_does_not_call_send_email_when_export_failed(
        self,
        generate_archive_mock: Mock,
        logger_mock: Mock,
        export_data_send_email_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        export_request = self.create_user_data_export_task(user_1)
        generate_archive_mock.return_value = (None, None)

        export_user_data(task_id=export_request.id)

        export_data_send_email_mock.send.assert_not_called()

    def test_it_calls_send_email_when_export_is_successful(
        self,
        generate_archive_mock: Mock,
        logger_mock: Mock,
        export_data_send_email_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        export_request = self.create_user_data_export_task(user_1)
        archive_name = self.random_string()
        generate_archive_mock.return_value = (
            self.random_string(),
            archive_name,
        )
        archive_size = self.random_int()

        with patch(
            "fittrackee.users.export_data.os.path.getsize",
            return_value=archive_size,
        ):
            export_user_data(task_id=export_request.id)

        export_data_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_1.email,
            },
            {
                "username": user_1.username,
                "account_url": "https://example.com/profile/edit/account",
                "fittrackee_url": "https://example.com",
            },
            template="data_export_ready",
        )


class UserDataExportTestCase(RandomMixin, UserTaskMixin):
    def create_user_request(
        self, user: User, days: int = 0, progress: int = 100
    ) -> UserTask:
        user_data_export = self.create_user_data_export_task(
            user,
            created_at=datetime.now(timezone.utc) - timedelta(days=days),
            progress=progress,
        )
        return user_data_export

    def generate_archive(self, user: User) -> Tuple[UserTask, Optional[str]]:
        user_data_export = self.create_user_request(user, days=7)
        exporter = UserDataExporter(user)
        archive_path, archive_file_name = exporter.generate_archive()
        user_data_export.file_path = f"exports/{user.id}/{archive_file_name}"
        user_data_export.file_size = self.random_int()
        db.session.commit()
        return user_data_export, archive_path


class TestCleanUserDataExport(UserDataExportTestCase):
    def test_it_returns_0_when_no_export_requests(self, app: Flask) -> None:
        counts = clean_user_data_export(days=7)

        assert counts["deleted_requests"] == 0

    def test_it_does_not_delete_when_workout_upload_tasks(
        self, app: Flask, user_1: User
    ) -> None:
        self.create_workouts_upload_task(user_1, progress=100)

        clean_user_data_export(days=0)

        assert UserTask.query.count() == 1

    def test_it_returns_0_when_export_request_is_not_completed(
        self, app: Flask, user_1: User
    ) -> None:
        self.create_user_request(user_1, days=7, progress=50)

        counts = clean_user_data_export(days=7)

        assert counts["deleted_requests"] == 0

    def test_it_returns_0_when_export_request_created_less_than_given_days(
        self, app: Flask, user_1: User
    ) -> None:
        self.create_user_request(user_1, days=1)

        counts = clean_user_data_export(days=7)

        assert counts["deleted_requests"] == 0

    def test_it_returns_export_requests_created_more_than_given_days_count(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        self.create_user_request(user_1, days=7)
        self.create_user_request(user_2, days=7)

        counts = clean_user_data_export(days=7)

        assert counts["deleted_requests"] == 2

    def test_it_returns_counts(
        self, app: Flask, user_1: User, user_2: User, user_3: User
    ) -> None:
        user_1_data_export, archive_path = self.generate_archive(user_1)
        user_2_data_export, archive_path = self.generate_archive(user_2)
        self.create_user_request(user_3, days=7)

        counts = clean_user_data_export(days=7)

        assert counts["deleted_requests"] == 3
        assert counts["deleted_archives"] == 2
        user_1_data_export_file_size = (
            user_1_data_export.file_size if user_1_data_export.file_size else 0
        )
        user_2_data_export_file_size = (
            user_2_data_export.file_size if user_2_data_export.file_size else 0
        )
        assert counts["freed_space"] == (
            user_1_data_export_file_size + user_2_data_export_file_size
        )

    def test_it_deletes_archive(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        _, archive_path = self.generate_archive(user_1)

        clean_user_data_export(days=7)

        assert os.path.exists(archive_path) is False  # type: ignore

    def test_it_deletes_requests(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        self.generate_archive(user_1)

        clean_user_data_export(days=7)

        assert UserTask.query.filter_by(user_id=user_1.id).first() is None


class TestGenerateUsersArchives(UserDataExportTestCase):
    def test_it_returns_0_when_no_request(
        self, app: Flask, user_1: "User"
    ) -> None:
        self.create_workouts_upload_task(user_1)
        count = generate_user_data_archives(max_count=1)

        assert count == 0

    def test_it_returns_0_when_request_request_completed(
        self, app: Flask, user_1: User
    ) -> None:
        self.create_user_request(user_1, progress=100)

        count = generate_user_data_archives(max_count=1)

        assert count == 0

    def test_it_returns_count_when_archive_is_generated_user_archive(
        self, app: Flask, user_1: User
    ) -> None:
        self.create_user_request(user_1, progress=0)

        count = generate_user_data_archives(max_count=1)

        assert count == 1

    @patch.object(secrets, "token_urlsafe")
    def test_it_generates_user_archive(
        self, secrets_mock: Mock, app: Flask, user_1: User
    ) -> None:
        token_urlsafe = self.random_string()
        secrets_mock.return_value = token_urlsafe
        archive_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "exports",
            str(user_1.id),
            f"archive_{token_urlsafe}.zip",
        )
        self.create_user_request(user_1, progress=0)

        generate_user_data_archives(max_count=1)

        assert os.path.exists(archive_path) is True  # type: ignore

    def test_it_generates_max_count_of_archives(
        self, app: Flask, user_1: User, user_2: User, user_3: User
    ) -> None:
        self.create_user_request(user_3, progress=0)
        self.create_user_request(user_1, progress=0)
        self.create_user_request(user_2, progress=0)

        count = generate_user_data_archives(max_count=2)

        assert count == 2
        assert (
            UserTask.query.filter_by(user_id=user_1.id).one().progress == 100
        )
        assert UserTask.query.filter_by(user_id=user_2.id).one().progress == 0
        assert (
            UserTask.query.filter_by(user_id=user_3.id).one().progress == 100
        )


class TestProcessQueuedDataExport(UserDataExportTestCase):
    def test_it_raises_error_when_task_id_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        with pytest.raises(UserTaskException, match="Invalid task id"):
            process_queued_data_export(task_short_id="invalid")

    def test_it_raises_error_when_task_is_not_user_data_export(
        self, app: Flask, user_1: User
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(user_1)

        with pytest.raises(UserTaskException, match="No task found"):
            process_queued_data_export(task_short_id=workouts_upload.short_id)

    def test_it_raises_error_when_task_does_not_exist(
        self, app: "Flask", user_1: "User"
    ) -> None:
        with pytest.raises(UserTaskException, match="No task found"):
            process_queued_data_export(task_short_id=self.random_short_id())

    @pytest.mark.parametrize(
        "input_status, input_task_data",
        [
            ("errored", {"errored": True}),
            ("successful", {"progress": 100}),
        ],
    )
    def test_it_raises_error_when_task_is_not_queued(
        self,
        app: "Flask",
        user_1: "User",
        input_status: str,
        input_task_data: Dict,
    ) -> None:
        data_export_task = self.create_user_data_export_task(
            user_1, **input_task_data
        )

        with pytest.raises(UserTaskException, match="Task is not queued"):
            process_queued_data_export(task_short_id=data_export_task.short_id)

    def test_it_process_queued_task(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        data_export_task = self.create_user_data_export_task(user_1)
        now = datetime.now(tz=timezone.utc)

        with travel(now, tick=False):
            process_queued_data_export(task_short_id=data_export_task.short_id)

        assert data_export_task.updated_at == now
