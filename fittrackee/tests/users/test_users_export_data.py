import os
import secrets
from unittest.mock import Mock, call, patch

from flask import Flask

from fittrackee import db
from fittrackee.users.export_data import UserDataExporter, export_user_data
from fittrackee.users.models import User, UserDataExport
from fittrackee.workouts.models import Sport, Workout

from ..mixins import CallArgsMixin
from ..utils import random_int, random_string
from ..workouts.utils import post_a_workout


class TestUserDataExporterGetData:
    def test_it_return_serialized_user_as_info_info(
        self, app: Flask, user_1: User
    ) -> None:
        exporter = UserDataExporter(user_1)

        user_data = exporter.get_user_info()

        assert user_data == user_1.serialize(user_1)

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
                'id': workout_cycling_user_1.short_id,
                'sport_id': sport_1_cycling.id,
                'sport_label': sport_1_cycling.label,
                'title': workout_cycling_user_1.title,
                'creation_date': workout_cycling_user_1.creation_date,
                'modification_date': workout_cycling_user_1.modification_date,
                'workout_date': workout_cycling_user_1.workout_date,
                'duration': str(workout_cycling_user_1.duration),
                'pauses': None,
                'moving': str(workout_cycling_user_1.moving),
                'distance': float(workout_cycling_user_1.distance),
                'min_alt': None,
                'max_alt': None,
                'descent': None,
                'ascent': None,
                'max_speed': float(workout_cycling_user_1.max_speed),
                'ave_speed': float(workout_cycling_user_1.ave_speed),
                'gpx': None,
                'records': [
                    record.serialize()
                    for record in workout_cycling_user_1.records
                ],
                'segments': [],
                'weather_start': None,
                'weather_end': None,
                'notes': workout_cycling_user_1.notes,
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
        workout = Workout.query.first()
        exporter = UserDataExporter(user_1)

        workouts_data = exporter.get_user_workouts_data()

        assert workouts_data == [
            {
                'id': workout.short_id,
                'sport_id': sport_1_cycling.id,
                'sport_label': sport_1_cycling.label,
                'title': workout.title,
                'creation_date': workout.creation_date,
                'modification_date': workout.modification_date,
                'workout_date': workout.workout_date,
                'duration': str(workout.duration),
                'pauses': None,
                'moving': str(workout.moving),
                'distance': float(workout.distance),
                'min_alt': float(workout.min_alt),
                'max_alt': float(workout.max_alt),
                'descent': float(workout.descent),
                'ascent': float(workout.ascent),
                'max_speed': float(workout.max_speed),
                'ave_speed': float(workout.ave_speed),
                'gpx': workout.gpx.split('/')[-1],
                'records': [record.serialize() for record in workout.records],
                'segments': [
                    segment.serialize() for segment in workout.segments
                ],
                'weather_start': None,
                'weather_end': None,
                'notes': workout.notes,
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

    def test_export_data_generates_json_file_in_user_directory(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        data = {"foo": "bar"}
        export = UserDataExporter(user_1)
        user_directory = os.path.join(
            app.config['UPLOAD_FOLDER'], 'exports', str(user_1.id)
        )
        os.makedirs(user_directory, exist_ok=True)
        file_name = random_string()

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
            app.config['UPLOAD_FOLDER'], 'exports', str(user_1.id)
        )
        file_name = random_string()

        file_path = exporter.export_data(data, file_name)

        assert file_path == os.path.join(user_directory, f"{file_name}.json")


class TestUserDataExporterArchive(CallArgsMixin):
    @patch.object(secrets, 'token_urlsafe')
    @patch.object(UserDataExporter, 'export_data')
    @patch('fittrackee.users.export_data.ZipFile')
    def test_it_calls_export_data_twice(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        exporter = UserDataExporter(user_1)

        exporter.generate_archive()

        export_data.assert_has_calls(
            [
                call(exporter.get_user_info(), 'user_data'),
                call(exporter.get_user_workouts_data(), 'workouts_data'),
            ]
        )

    @patch.object(secrets, 'token_urlsafe')
    @patch.object(UserDataExporter, 'export_data')
    @patch('fittrackee.users.export_data.ZipFile')
    def test_it_calls_zipfile_with_expected_patch(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        exporter = UserDataExporter(user_1)
        token_urlsafe = random_string()
        secrets_mock.return_value = token_urlsafe
        expected_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            'exports',
            str(user_1.id),
            f"archive_{token_urlsafe}.zip",
        )

        exporter.generate_archive()

        zipfile_mock.assert_called_once_with(expected_path, 'w')

    @patch.object(secrets, 'token_urlsafe')
    @patch.object(UserDataExporter, 'export_data')
    @patch('fittrackee.users.export_data.ZipFile')
    def test_it_calls_zipfile_for_each_json_file(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        exporter = UserDataExporter(user_1)
        token_urlsafe = random_string()
        secrets_mock.return_value = token_urlsafe
        export_data.side_effect = [call('user_info'), call('workouts_data')]

        exporter.generate_archive()

        # fmt: off
        zipfile_mock.return_value.__enter__\
            .return_value.write.assert_has_calls(
                [
                    call(call('user_info'), 'user_data.json'),
                    call(call('workouts_data'), 'user_workouts_data.json'),
                ]
            )
        # fmt: on

    @patch.object(secrets, 'token_urlsafe')
    @patch.object(UserDataExporter, 'export_data')
    @patch('fittrackee.users.export_data.ZipFile')
    def test_it_calls_zipfile_for_gpx_file(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        _, workout_short_id = post_a_workout(app, gpx_file)
        workout = Workout.query.first()
        expected_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            workout.gpx,
        )
        exporter = UserDataExporter(user_1)

        exporter.generate_archive()

        # fmt: off
        zipfile_mock.return_value.__enter__.\
            return_value.write.assert_has_calls(
                [
                    call(expected_path, f"gpx/{workout.gpx.split('/')[-1]}"),
                ]
            )
        # fmt: on

    @patch.object(secrets, 'token_urlsafe')
    @patch.object(UserDataExporter, 'export_data')
    @patch('fittrackee.users.export_data.ZipFile')
    def test_it_calls_zipfile_for_profile_image_when_exists(
        self,
        zipfile_mock: Mock,
        export_data: Mock,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        user_1.picture = random_string()
        expected_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            user_1.picture,
        )
        exporter = UserDataExporter(user_1)

        with patch(
            'fittrackee.users.export_data.os.path.isfile', return_value=True
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

    @patch.object(secrets, 'token_urlsafe')
    def test_it_test_it_generates_a_zip_archive(
        self,
        secrets_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        token_urlsafe = random_string()
        secrets_mock.return_value = token_urlsafe
        expected_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            'exports',
            str(user_1.id),
            f"archive_{token_urlsafe}.zip",
        )
        exporter = UserDataExporter(user_1)

        exporter.generate_archive()

        assert os.path.isfile(expected_path)


@patch('fittrackee.users.export_data.appLog')
@patch.object(UserDataExporter, 'generate_archive')
class TestExportUserData:
    def test_it_logs_error_if_not_request_for_given_id(
        self,
        generate_archive: Mock,
        logger_mock: Mock,
        app: Flask,
    ) -> None:
        request_id = random_int()

        export_user_data(export_request_id=request_id)

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
        export_request = UserDataExport(user_id=user_1.id)
        db.session.add(export_request)
        export_request.completed = True
        db.session.commit()

        export_user_data(export_request_id=export_request.id)

        logger_mock.info.assert_called_once_with(
            f"Export id '{export_request.id}' already processed"
        )

    def test_it_update_export_request_when_export_is_successful(
        self,
        generate_archive_mock: Mock,
        logger_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        export_request = UserDataExport(user_id=user_1.id)
        db.session.add(export_request)
        db.session.commit()
        archive_name = random_string()
        generate_archive_mock.return_value = (random_string(), archive_name)
        archive_size = random_int()

        with patch(
            'fittrackee.users.export_data.os.path.getsize',
            return_value=archive_size,
        ):
            export_user_data(export_request_id=export_request.id)

        assert export_request.completed is True
        assert export_request.updated_at is not None
        assert export_request.file_name == archive_name
        assert export_request.file_size == archive_size

    def test_it_update_export_request_when_export_fails(
        self,
        generate_archive_mock: Mock,
        logger_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        export_request = UserDataExport(user_id=user_1.id)
        db.session.add(export_request)
        db.session.commit()
        generate_archive_mock.return_value = (None, None)

        export_user_data(export_request_id=export_request.id)

        assert export_request.completed is True
        assert export_request.updated_at is not None
        assert export_request.file_name is None
        assert export_request.file_size is None
