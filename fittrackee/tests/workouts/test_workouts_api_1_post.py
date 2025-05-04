import json
import os
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import TYPE_CHECKING, Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.database import PSQL_INTEGER_LIMIT
from fittrackee.equipments.models import Equipment
from fittrackee.reports.models import ReportActionAppeal
from fittrackee.users.models import User, UserTask
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.exceptions import (
    WorkoutExceedingValueException,
)
from fittrackee.workouts.models import Sport, Workout
from fittrackee.workouts.services.workout_from_file import (
    WorkoutGpxCreationService,
)

from ..mixins import BaseTestMixin, ReportMixin, UserTaskMixin
from ..utils import OAUTH_SCOPES, jsonify_dict
from .mixins import WorkoutApiTestCaseMixin, WorkoutGpxInfoMixin

if TYPE_CHECKING:
    from fittrackee.equipments.models import Equipment


def assert_workout_data_with_gpx(data: Dict, user: User) -> None:
    assert "creation_date" in data["data"]["workouts"][0]
    assert (
        "Tue, 13 Mar 2018 12:44:45 GMT"
        == data["data"]["workouts"][0]["workout_date"]
    )
    assert data["data"]["workouts"][0]["user"] == jsonify_dict(
        user.serialize()
    )
    assert 1 == data["data"]["workouts"][0]["sport_id"]
    assert "0:04:10" == data["data"]["workouts"][0]["duration"]
    assert data["data"]["workouts"][0]["ascent"] == 0.4
    assert data["data"]["workouts"][0]["ave_speed"] == 4.61
    assert data["data"]["workouts"][0]["descent"] == 23.4
    assert data["data"]["workouts"][0]["description"] is None
    assert data["data"]["workouts"][0]["distance"] == 0.32
    assert data["data"]["workouts"][0]["max_alt"] == 998.0
    assert data["data"]["workouts"][0]["max_speed"] == 5.12
    assert data["data"]["workouts"][0]["min_alt"] == 975.0
    assert data["data"]["workouts"][0]["moving"] == "0:04:10"
    assert data["data"]["workouts"][0]["pauses"] is None
    assert data["data"]["workouts"][0]["with_gpx"] is True
    assert data["data"]["workouts"][0]["map"] is not None
    assert data["data"]["workouts"][0]["weather_start"] is None
    assert data["data"]["workouts"][0]["weather_end"] is None
    assert data["data"]["workouts"][0]["notes"] is None
    assert len(data["data"]["workouts"][0]["segments"]) == 1

    segment = data["data"]["workouts"][0]["segments"][0]
    assert segment["workout_id"] == data["data"]["workouts"][0]["id"]
    assert segment["segment_id"] == 0
    assert segment["duration"] == "0:04:10"
    assert segment["ascent"] == 0.4
    assert segment["ave_speed"] == 4.61
    assert segment["descent"] == 23.4
    assert segment["distance"] == 0.32
    assert segment["max_alt"] == 998.0
    assert segment["max_speed"] == 5.12
    assert segment["min_alt"] == 975.0
    assert segment["moving"] == "0:04:10"
    assert segment["pauses"] is None

    records = data["data"]["workouts"][0]["records"]
    assert len(records) == 5
    assert records[0]["sport_id"] == 1
    assert records[0]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[0]["record_type"] == "AS"
    assert records[0]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
    assert records[0]["value"] == 4.61
    assert records[1]["sport_id"] == 1
    assert records[1]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[1]["record_type"] == "FD"
    assert records[1]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
    assert records[1]["value"] == 0.32
    assert records[2]["sport_id"] == 1
    assert records[2]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[2]["record_type"] == "HA"
    assert records[2]["value"] == 0.4
    assert records[2]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
    assert records[3]["sport_id"] == 1
    assert records[3]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[3]["record_type"] == "LD"
    assert records[3]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
    assert records[3]["value"] == "0:04:10"
    assert records[4]["sport_id"] == 1
    assert records[4]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[4]["record_type"] == "MS"
    assert records[4]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
    assert records[4]["value"] == 5.12


def assert_workout_data_with_gpx_segments(data: Dict, user: User) -> None:
    assert "creation_date" in data["data"]["workouts"][0]
    assert (
        "Tue, 13 Mar 2018 12:44:45 GMT"
        == data["data"]["workouts"][0]["workout_date"]
    )
    assert data["data"]["workouts"][0]["user"] == jsonify_dict(
        user.serialize()
    )
    assert 1 == data["data"]["workouts"][0]["sport_id"]
    assert "0:04:10" == data["data"]["workouts"][0]["duration"]
    assert data["data"]["workouts"][0]["ascent"] == 0.4
    assert data["data"]["workouts"][0]["ave_speed"] == 4.59
    assert data["data"]["workouts"][0]["descent"] == 23.4
    assert data["data"]["workouts"][0]["description"] is None
    assert data["data"]["workouts"][0]["distance"] == 0.3
    assert data["data"]["workouts"][0]["max_alt"] == 998.0
    assert data["data"]["workouts"][0]["max_speed"] == 5.25
    assert data["data"]["workouts"][0]["min_alt"] == 975.0
    assert data["data"]["workouts"][0]["moving"] == "0:03:55"
    assert data["data"]["workouts"][0]["pauses"] == "0:00:15"
    assert data["data"]["workouts"][0]["with_gpx"] is True
    assert data["data"]["workouts"][0]["map"] is not None
    assert data["data"]["workouts"][0]["weather_start"] is None
    assert data["data"]["workouts"][0]["weather_end"] is None
    assert data["data"]["workouts"][0]["notes"] is None
    assert len(data["data"]["workouts"][0]["segments"]) == 2

    segment = data["data"]["workouts"][0]["segments"][0]
    assert segment["workout_id"] == data["data"]["workouts"][0]["id"]
    assert segment["segment_id"] == 0
    assert segment["duration"] == "0:01:30"
    assert segment["ascent"] is None
    assert segment["ave_speed"] == 4.53
    assert segment["descent"] == 11.0
    assert segment["distance"] == 0.113
    assert segment["max_alt"] == 998.0
    assert segment["max_speed"] == 5.25
    assert segment["min_alt"] == 987.0
    assert segment["moving"] == "0:01:30"
    assert segment["pauses"] is None

    segment = data["data"]["workouts"][0]["segments"][1]
    assert segment["workout_id"] == data["data"]["workouts"][0]["id"]
    assert segment["segment_id"] == 1
    assert segment["duration"] == "0:02:25"
    assert segment["ascent"] == 0.4
    assert segment["ave_speed"] == 4.62
    assert segment["descent"] == 12.4
    assert segment["distance"] == 0.186
    assert segment["max_alt"] == 987.0
    assert segment["max_speed"] == 5.12
    assert segment["min_alt"] == 975.0
    assert segment["moving"] == "0:02:25"
    assert segment["pauses"] is None

    records = data["data"]["workouts"][0]["records"]
    assert len(records) == 5
    assert records[0]["sport_id"] == 1
    assert records[0]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[0]["record_type"] == "AS"
    assert records[0]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
    assert records[0]["value"] == 4.59
    assert records[1]["sport_id"] == 1
    assert records[1]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[1]["record_type"] == "FD"
    assert records[1]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
    assert records[1]["value"] == 0.3
    assert records[2]["sport_id"] == 1
    assert records[2]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[2]["record_type"] == "HA"
    assert records[2]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
    assert records[2]["value"] == 0.4
    assert records[3]["sport_id"] == 1
    assert records[3]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[3]["record_type"] == "LD"
    assert records[3]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
    assert records[3]["value"] == "0:03:55"
    assert records[4]["sport_id"] == 1
    assert records[4]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[4]["record_type"] == "MS"
    assert records[4]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
    assert records[4]["value"] == 5.25


def assert_workout_data_wo_gpx(data: Dict, user: User) -> None:
    assert "creation_date" in data["data"]["workouts"][0]
    assert (
        data["data"]["workouts"][0]["workout_date"]
        == "Tue, 15 May 2018 14:05:00 GMT"
    )
    assert data["data"]["workouts"][0]["user"] == jsonify_dict(
        user.serialize()
    )
    assert data["data"]["workouts"][0]["sport_id"] == 1
    assert data["data"]["workouts"][0]["duration"] == "1:00:00"
    assert (
        data["data"]["workouts"][0]["title"]
        == "Cycling (Sport) - 2018-05-15 14:05:00"
    )
    assert data["data"]["workouts"][0]["ascent"] is None
    assert data["data"]["workouts"][0]["ave_speed"] == 10.0
    assert data["data"]["workouts"][0]["descent"] is None
    assert data["data"]["workouts"][0]["description"] is None
    assert data["data"]["workouts"][0]["distance"] == 10.0
    assert data["data"]["workouts"][0]["max_alt"] is None
    assert data["data"]["workouts"][0]["max_speed"] == 10.0
    assert data["data"]["workouts"][0]["min_alt"] is None
    assert data["data"]["workouts"][0]["moving"] == "1:00:00"
    assert data["data"]["workouts"][0]["pauses"] is None
    assert data["data"]["workouts"][0]["with_gpx"] is False
    assert data["data"]["workouts"][0]["map"] is None
    assert data["data"]["workouts"][0]["weather_start"] is None
    assert data["data"]["workouts"][0]["weather_end"] is None
    assert data["data"]["workouts"][0]["notes"] is None

    assert len(data["data"]["workouts"][0]["segments"]) == 0

    records = data["data"]["workouts"][0]["records"]
    assert len(records) == 4
    assert records[0]["sport_id"] == 1
    assert records[0]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[0]["record_type"] == "AS"
    assert records[0]["workout_date"] == "Tue, 15 May 2018 14:05:00 GMT"
    assert records[0]["value"] == 10.0
    assert records[1]["sport_id"] == 1
    assert records[1]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[1]["record_type"] == "FD"
    assert records[1]["workout_date"] == "Tue, 15 May 2018 14:05:00 GMT"
    assert records[1]["value"] == 10.0
    assert records[2]["sport_id"] == 1
    assert records[2]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[2]["record_type"] == "LD"
    assert records[2]["workout_date"] == "Tue, 15 May 2018 14:05:00 GMT"
    assert records[2]["value"] == "1:00:00"
    assert records[3]["sport_id"] == 1
    assert records[3]["workout_id"] == data["data"]["workouts"][0]["id"]
    assert records[3]["record_type"] == "MS"
    assert records[3]["workout_date"] == "Tue, 15 May 2018 14:05:00 GMT"
    assert records[3]["value"] == 10.0


def assert_files_are_deleted(
    app: "Flask", user: User, expected_count: Optional[int] = 0
) -> None:
    upload_directory = os.path.join(
        app.config["UPLOAD_FOLDER"], f"workouts/{user.id}"
    )
    assert (
        len(
            [
                name
                for name in os.listdir(upload_directory)
                if os.path.isfile(os.path.join(upload_directory, name))
            ]
        )
        == expected_count
    )


class TestPostWorkoutWithGpx(
    WorkoutGpxInfoMixin, WorkoutApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: "Flask", sport_1_cycling: "Sport", gpx_file: str
    ) -> None:
        client = app.test_client()

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(content_type="multipart/form-data"),
        )

        self.assert_401(response)

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: "Flask",
        suspended_user: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_403(response)

    def test_it_returns_error_when_parsed_value_from_gpx_exceeds_limit(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch.object(
            WorkoutGpxCreationService, "get_gpx_info"
        ) as get_gpx_info_mock:
            get_gpx_info_mock.return_value = (
                self.generate_get_gpx_info_return_value(
                    {"moving_time": PSQL_INTEGER_LIMIT + 1}
                )
            )
            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

        self.assert_400(
            response,
            error_message=(
                "one or more values, entered or calculated, exceed the limits"
            ),
        )

    def test_it_adds_a_workout_with_gpx_file(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert "just a workout" == data["data"]["workouts"][0]["title"]
        assert_workout_data_with_gpx(data, user_1)

    def test_it_returns_400_when_quotes_are_not_escaped_in_notes(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{{"sport_id": 1, "notes": "test "workout""}}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response)

    def test_it_returns_400_when_quotes_are_not_escaped_in_description(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{{"sport_id": 1, "description": "test "workout""}}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response)

    def test_it_returns_500_if_gpx_file_has_not_tracks(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file_wo_track: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file_wo_track)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        data = self.assert_500(response, "no tracks in gpx file")
        assert "data" not in data

    def test_it_returns_500_if_gpx_has_invalid_xml(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file_invalid_xml: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_invalid_xml)),
                    "example.gpx",
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        data = self.assert_500(response, "error when parsing gpx file")
        assert "data" not in data

    def test_it_returns_500_if_gpx_has_no_time(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file_without_time: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_without_time)),
                    "example.gpx",
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        data = self.assert_500(response, "<time> is missing in gpx file")
        assert "data" not in data

    def test_it_returns_400_if_workout_gpx_has_invalid_extension(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.png"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response, "file extension not allowed", "fail")

    def test_it_returns_400_if_sport_id_is_not_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"), data="{}"
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response)

    def test_it_returns_400_if_sport_id_does_not_exist(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 2}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response, "Sport id: 2 does not exist", "invalid")

    def test_returns_400_if_no_gpx_file_is_provided(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(data="{}"),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_400(response, "no file part", "fail")

    def test_it_returns_error_when_file_size_exceeds_limit(
        self,
        app_with_max_file_size: Flask,
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_file_size, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        data = self.assert_413(
            response,
            match=(
                r"Error during workout upload, "
                r"file size \((.*)\) exceeds 1.0KB."
            ),
        )
        assert "data" not in data

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: "Flask",
        user_1: "User",
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            "/api/workouts",
            data=dict(),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {access_token}",
            ),
        )

        self.assert_response_scope(response, can_access)


class TestPostWorkoutWithKml(WorkoutApiTestCaseMixin):
    def test_it_adds_a_workout_with_kml_file(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        kml_2_3_with_one_track: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(
                    BytesIO(str.encode(kml_2_3_with_one_track)),
                    "example.kml",
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["title"] == "just a workout"
        assert data["data"]["workouts"][0]["sport_id"] == 1
        assert data["data"]["workouts"][0]["duration"] == "0:04:10"
        assert data["data"]["workouts"][0]["ascent"] == 0.4
        assert data["data"]["workouts"][0]["ave_speed"] == 4.61
        assert data["data"]["workouts"][0]["descent"] == 23.4
        assert data["data"]["workouts"][0]["description"] == "some description"
        assert data["data"]["workouts"][0]["distance"] == 0.32
        assert data["data"]["workouts"][0]["max_alt"] == 998.0
        assert data["data"]["workouts"][0]["max_speed"] == 5.25
        assert data["data"]["workouts"][0]["min_alt"] == 975.0
        assert data["data"]["workouts"][0]["moving"] == "0:04:10"
        assert data["data"]["workouts"][0]["pauses"] is None
        assert data["data"]["workouts"][0]["with_gpx"] is True
        assert data["data"]["workouts"][0]["map"] is not None
        assert data["data"]["workouts"][0]["weather_start"] is None
        assert data["data"]["workouts"][0]["weather_end"] is None
        assert data["data"]["workouts"][0]["notes"] is None
        assert len(data["data"]["workouts"][0]["segments"]) == 1


class TestPostWorkoutWithKmz(WorkoutApiTestCaseMixin):
    def test_it_adds_a_workout_with_kmz_file(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        file_path = os.path.join(app.root_path, "tests/files/example.kmz")
        with open(file_path, "rb") as kmz_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(kmz_file, "example.kmz"), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["title"] == "just a workout"
        assert data["data"]["workouts"][0]["sport_id"] == 1
        assert data["data"]["workouts"][0]["duration"] == "0:04:10"
        assert data["data"]["workouts"][0]["ascent"] == 0.4
        assert data["data"]["workouts"][0]["ave_speed"] == 4.59
        assert data["data"]["workouts"][0]["descent"] == 23.4
        assert data["data"]["workouts"][0]["description"] == "some description"
        assert data["data"]["workouts"][0]["distance"] == 0.299
        assert data["data"]["workouts"][0]["max_alt"] == 998.0
        assert data["data"]["workouts"][0]["max_speed"] == 5.41
        assert data["data"]["workouts"][0]["min_alt"] == 975.0
        assert data["data"]["workouts"][0]["moving"] == "0:03:55"
        assert data["data"]["workouts"][0]["pauses"] == "0:00:15"
        assert data["data"]["workouts"][0]["with_gpx"] is True
        assert data["data"]["workouts"][0]["map"] is not None
        assert data["data"]["workouts"][0]["weather_start"] is None
        assert data["data"]["workouts"][0]["weather_end"] is None
        assert data["data"]["workouts"][0]["notes"] is None
        assert len(data["data"]["workouts"][0]["segments"]) == 2


class TestPostWorkoutWithTcx(WorkoutApiTestCaseMixin):
    def test_it_adds_a_workout_with_tcx_file(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        tcx_with_one_lap_and_one_track: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(
                    BytesIO(str.encode(tcx_with_one_lap_and_one_track)),
                    "example.tcx",
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["title"] is not None
        assert data["data"]["workouts"][0]["sport_id"] == 1
        assert data["data"]["workouts"][0]["duration"] == "0:04:10"
        assert data["data"]["workouts"][0]["ascent"] == 0.0
        assert data["data"]["workouts"][0]["ave_speed"] == 4.58
        assert data["data"]["workouts"][0]["descent"] == 21.0
        assert data["data"]["workouts"][0]["description"] is None
        assert data["data"]["workouts"][0]["distance"] == 0.318
        assert data["data"]["workouts"][0]["max_alt"] == 997.0
        assert data["data"]["workouts"][0]["max_speed"] == 5.11
        assert data["data"]["workouts"][0]["min_alt"] == 976.0
        assert data["data"]["workouts"][0]["moving"] == "0:04:10"
        assert data["data"]["workouts"][0]["pauses"] is None
        assert data["data"]["workouts"][0]["with_gpx"] is True
        assert data["data"]["workouts"][0]["map"] is not None
        assert data["data"]["workouts"][0]["weather_start"] is None
        assert data["data"]["workouts"][0]["weather_end"] is None
        assert data["data"]["workouts"][0]["notes"] is None
        assert len(data["data"]["workouts"][0]["segments"]) == 1


class TestPostWorkoutWithoutGpx(WorkoutApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: "Flask", sport_1_cycling: "Sport", gpx_file: str
    ) -> None:
        client = app.test_client()

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-05-15 14:05",
                    distance=10,
                )
            ),
            headers=dict(content_type="multipart/form-data"),
        )

        self.assert_401(response)

    def test_it_adds_a_workout_without_gpx(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-05-15 14:05",
                    distance=10,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert_workout_data_wo_gpx(data, user_1)

    def test_it_returns_error_when_user_is_suspended(
        self, app: "Flask", suspended_user: "User", sport_1_cycling: "Sport"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-05-15 14:05",
                    distance=10,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_error_when_value_exceeds_limit(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            json={
                "sport_id": sport_1_cycling.id,
                "duration": 36,
                "workout_date": "2023-07-26 12:00",
                "distance": 100,
                "ascent": 120,
                "descent": 80,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        self.assert_400(
            response,
            error_message=(
                "one or more values, entered or calculated, exceed the limits"
            ),
        )

    def test_it_adds_a_workout_without_gpx_and_title(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        title = self.random_string()

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-05-15 14:05",
                    distance=10,
                    title=title,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["title"] == title

    @pytest.mark.parametrize(
        "description,input_data",
        [
            (
                "'sport_id' is missing",
                {
                    "duration": 3600,
                    "workout_date": "2018-05-15 14:05",
                    "distance": 10,
                },
            ),
            (
                "'duration' is missing",
                {
                    "sport_id": 1,
                    "workout_date": "2018-05-15 14:05",
                    "distance": 10,
                },
            ),
            (
                "'workout_date' is missing",
                {"sport_id": 1, "duration": 3600, "distance": 10},
            ),
            (
                "'distance' is missing",
                {
                    "sport_id": 1,
                    "duration": 3600,
                    "workout_date": "2018-05-15 14:05",
                },
            ),
        ],
    )
    def test_it_returns_400_if_key_is_missing(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        description: str,
        input_data: Dict,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(input_data),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_returns_400_when_ascent_or_descent_are_provided_together(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                {
                    "sport_id": 1,
                    "duration": 3600,
                    "workout_date": "2018-05-15 14:05",
                    "distance": 10,
                    "ascent": 100,
                }
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid ascent or descent", "invalid")

    @pytest.mark.parametrize(
        "description,input_data",
        [
            ("ascent is below 0", {"ascent": -100, "descent": 100}),
            ("descent is None", {"ascent": 150, "descent": None}),
        ],
    )
    def test_it_returns_400_when_ascent_or_descent_are_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        description: str,
        input_data: Dict,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                {
                    "sport_id": 1,
                    "duration": 3600,
                    "workout_date": "2018-05-15 14:05",
                    "distance": 10,
                    **input_data,
                }
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid ascent or descent", "invalid")

    def test_it_returns_500_if_workout_date_format_is_invalid(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="15/2018",
                    distance=10,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(
            response, "invalid format for workout date", status="error"
        )

    @pytest.mark.parametrize("input_distance", [0, "", None])
    def test_it_returns_400_when_distance_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        input_distance: Any,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-05-15 14:05",
                    distance=input_distance,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    @pytest.mark.parametrize("input_duration", [0, "", None])
    def test_it_returns_400_when_duration_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        input_duration: Any,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=input_duration,
                    workout_date="2018-05-15 14:05",
                    distance=10,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_adds_a_workout_with_notes(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        notes = "test"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-05-15 14:05",
                    distance=10,
                    notes=notes,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["notes"] == notes

    def test_it_adds_a_workout_with_description(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        description = "test"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-05-15 14:05",
                    distance=10,
                    description=description,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["description"] == description

    def test_it_adds_a_workout_with_equipments(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            json={
                "sport_id": sport_1_cycling.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 10,
                "equipment_ids": [
                    equipment_bike_user_1.short_id,
                ],
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["equipments"] == [
            jsonify_dict(equipment_bike_user_1.serialize(current_user=user_1))
        ]
        assert equipment_bike_user_1.total_workouts == 1
        assert equipment_bike_user_1.total_distance == 10
        assert equipment_bike_user_1.total_duration == timedelta(seconds=3600)
        assert equipment_bike_user_1.total_moving == timedelta(seconds=3600)

    def test_it_returns_400_when_equipment_is_invalid_for_given_sport(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            json={
                "sport_id": sport_1_cycling.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 10,
                "equipment_ids": [
                    equipment_shoes_user_1.short_id,
                ],
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data["equipment_id"] == equipment_shoes_user_1.short_id
        assert data["message"] == (
            f"invalid equipment id {equipment_shoes_user_1.short_id} "
            f"for sport {sport_1_cycling.label}"
        )
        assert data["status"] == "invalid"

    def test_it_returns_400_when_equipment_is_inactive_for_given_sport(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        equipment_bike_user_1.is_active = False
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            json={
                "sport_id": sport_1_cycling.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 10,
                "equipment_ids": [equipment_bike_user_1.short_id],
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data["equipment_id"] == equipment_bike_user_1.short_id
        assert data["message"] == (
            f"equipment with id {equipment_bike_user_1.short_id} is inactive"
        )
        assert data["status"] == "inactive"

    def test_it_returns_400_when_multiple_equipments_are_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_2_running: Sport,
        equipment_shoes_user_1: "Equipment",
        equipment_another_shoes_user_1: "Equipment",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            json={
                "sport_id": sport_2_running.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 5,
                "equipment_ids": [
                    equipment_shoes_user_1.short_id,
                    equipment_another_shoes_user_1.short_id,
                ],
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "only one equipment can be added")

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: "Flask",
        user_1: "User",
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            "/api/workouts/no_gpx",
            data=dict(),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {access_token}",
            ),
        )

        self.assert_response_scope(response, can_access)


class TestPostWorkoutWithZipArchive(UserTaskMixin, WorkoutApiTestCaseMixin):
    def test_it_adds_workouts_synchronously_with_zip_archive(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        file_path = os.path.join(app.root_path, "tests/files/gpx_test.zip")
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(zip_file, "gpx_test.zip"), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

            assert response.status_code == 201
            data = json.loads(response.data.decode())
            assert "created" in data["status"]
            assert len(data["data"]["workouts"]) == 3
            assert "creation_date" in data["data"]["workouts"][0]
            assert (
                "Tue, 13 Mar 2018 12:44:45 GMT"
                == data["data"]["workouts"][0]["workout_date"]
            )
            assert data["data"]["workouts"][0]["user"] == jsonify_dict(
                user_1.serialize()
            )
            assert 1 == data["data"]["workouts"][0]["sport_id"]
            assert "0:04:10" == data["data"]["workouts"][0]["duration"]
            assert data["data"]["workouts"][0]["ascent"] == 0.4
            assert data["data"]["workouts"][0]["ave_speed"] == 4.61
            assert data["data"]["workouts"][0]["descent"] == 23.4
            assert data["data"]["workouts"][0]["description"] is None
            assert data["data"]["workouts"][0]["distance"] == 0.32
            assert data["data"]["workouts"][0]["max_alt"] == 998.0
            assert data["data"]["workouts"][0]["max_speed"] == 5.12
            assert data["data"]["workouts"][0]["min_alt"] == 975.0
            assert data["data"]["workouts"][0]["moving"] == "0:04:10"
            assert data["data"]["workouts"][0]["pauses"] is None
            assert data["data"]["workouts"][0]["with_gpx"] is True
            assert data["data"]["workouts"][0]["map"] is not None
            assert data["data"]["workouts"][0]["weather_start"] is None
            assert data["data"]["workouts"][0]["weather_end"] is None
            assert data["data"]["workouts"][0]["notes"] is None
            assert len(data["data"]["workouts"][0]["segments"]) == 1

            segment = data["data"]["workouts"][0]["segments"][0]
            assert segment["workout_id"] == data["data"]["workouts"][0]["id"]
            assert segment["segment_id"] == 0
            assert segment["duration"] == "0:04:10"
            assert segment["ascent"] == 0.4
            assert segment["ave_speed"] == 4.61
            assert segment["descent"] == 23.4
            assert segment["distance"] == 0.32
            assert segment["max_alt"] == 998.0
            assert segment["max_speed"] == 5.12
            assert segment["min_alt"] == 975.0
            assert segment["moving"] == "0:04:10"
            assert segment["pauses"] is None

    def test_it_adds_valid_workout_when_one_file_in_zip_archive_is_invalid(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        # 'gpx_test_incorrect.zip' contains 2 gpx files, one is incorrect
        file_path = os.path.join(
            app.root_path, "tests/files/gpx_test_incorrect.zip"
        )
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(zip_file, "gpx_test_incorrect.zip"),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

            assert response.status_code == 400
            data = json.loads(response.data.decode())
            assert data["status"] == "fail"
            assert data["new_workouts"] == 1
            assert data["errored_workouts"] == {
                "test_4.gpx": "no tracks in gpx file",
            }

    def test_it_returns_400_when_all_files_in_zip_archive_are_invalid(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        # 'gpx_test_incorrect.zip' contains 2 incorrect gpx files
        file_path = os.path.join(
            app.root_path, "tests/files/gpx_test_all_incorrect.zip"
        )
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(zip_file, "gpx_test_incorrect.zip"),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

            assert response.status_code == 400
            data = json.loads(response.data.decode())
            assert data["status"] == "fail"
            assert data["new_workouts"] == 0
            assert data["errored_workouts"] == {
                "test_4.gpx": "no tracks in gpx file",
                "test_5.gpx": "no tracks in gpx file",
            }

    def test_it_adds_valid_workout_when_one_file_has_invalid_calculated_value(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        file_path = os.path.join(app.root_path, "tests/files/gpx_test.zip")
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            with patch.object(
                WorkoutGpxCreationService,
                "check_gpx_info",
                side_effect=[
                    # 1st gpx files
                    None,
                    None,
                    # 2nd gpx files
                    WorkoutExceedingValueException(
                        "'distance' exceeds max value (999999.9)"
                    ),
                    None,
                    # 3rd gpx files
                    None,
                    None,
                ],
            ):
                response = client.post(
                    "/api/workouts",
                    data=dict(
                        file=(zip_file, "gpx_test_incorrect.zip"),
                        data='{"sport_id": 1}',
                    ),
                    headers=dict(
                        content_type="multipart/form-data",
                        Authorization=f"Bearer {auth_token}",
                    ),
                )

            assert response.status_code == 400
            data = json.loads(response.data.decode())
            assert data["status"] == "fail"
            assert data["new_workouts"] == 2
            assert data["errored_workouts"] == {
                "test_2.gpx": "one or more values, entered or calculated, "
                "exceed the limits"
            }

    def test_it_creates_task_to_add_workouts_asynchronously_when_files_exceed_limit(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        upload_workouts_archive_mock: "MagicMock",
    ) -> None:
        app.config.update(
            {"file_limit_import": 3, "file_sync_limit_import": 2}
        )
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        file_path = os.path.join(app.root_path, "tests/files/gpx_test.zip")
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(zip_file, "gpx_test.zip"), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

            assert response.status_code == 200
            data = json.loads(response.data.decode())
            assert "in_progress" in data["status"]
            upload_task = UserTask.query.filter_by(
                user_id=user_1.id, task_type="workouts_archive_upload"
            ).one()
            upload_workouts_archive_mock.send.assert_called_once_with(
                task_id=upload_task.id
            )
            assert data["data"] == {"task_id": upload_task.short_id}

    def test_it_returns_error_when_ongoing_task_exists(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        upload_workouts_archive_mock: "MagicMock",
    ) -> None:
        self.create_workouts_upload_task(user_1)
        app.config.update(
            {"file_limit_import": 3, "file_sync_limit_import": 2}
        )
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        file_path = os.path.join(app.root_path, "tests/files/gpx_test.zip")
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(zip_file, "gpx_test.zip"), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

            self.assert_400(response, "ongoing upload task exists", "invalid")

    def test_it_returns_400_when_files_in_archive_exceed_limit(
        self,
        app_with_max_workouts: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        file_path = os.path.join(
            app_with_max_workouts.root_path, "tests/files/gpx_test.zip"
        )
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app_with_max_workouts, user_1.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(zip_file, "gpx_test.zip"), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

            self.assert_400(
                response,
                "the number of files in the archive exceeds the limit",
                "fail",
            )

    def test_it_returns_413_if_archive_size_exceeds_limit(
        self,
        app_with_max_zip_file_size: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        file_path = os.path.join(
            app_with_max_zip_file_size.root_path, "tests/files/gpx_test.zip"
        )
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app_with_max_zip_file_size, user_1.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(zip_file, "gpx_test.zip"), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

            data = self.assert_413(
                response,
                "Error during workout upload, "
                "file size (2.5KB) exceeds 1.0KB.",
            )
            assert "data" not in data

    def test_it_adds_a_workouts_with_equipments(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        file_path = os.path.join(app.root_path, "tests/files/gpx_test.zip")
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(zip_file, "gpx_test.zip"),
                    data=(
                        f'{{"sport_id": 1, "equipment_ids":'
                        f' ["{equipment_bike_user_1.short_id}"]}}'
                    ),
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 3
        assert data["data"]["workouts"][0]["equipments"] == [
            jsonify_dict(equipment_bike_user_1.serialize(current_user=user_1))
        ]
        assert data["data"]["workouts"][1]["equipments"] == [
            jsonify_dict(equipment_bike_user_1.serialize(current_user=user_1))
        ]
        assert data["data"]["workouts"][2]["equipments"] == [
            jsonify_dict(equipment_bike_user_1.serialize(current_user=user_1))
        ]
        assert equipment_bike_user_1.total_workouts == 3
        assert float(equipment_bike_user_1.total_distance) == 0.96
        assert equipment_bike_user_1.total_duration == timedelta(seconds=750)
        assert equipment_bike_user_1.total_moving == timedelta(seconds=750)

    def test_it_adds_workouts_when_zip_contains_files_with_multiple_extensions(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        # 'gpx_multiple_extensions.zip' contains:
        # - a gpx file
        # - a kml file
        # - a kmz file
        file_path = os.path.join(
            app.root_path, "tests/files/gpx_multiple_extensions.zip"
        )
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(zip_file, "gpx_test.zip"), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 3
        assert Workout.query.count() == 3


class TestPostAndGetWorkoutWithGpx(WorkoutApiTestCaseMixin):
    def workout_assertion(
        self, app: "Flask", user_1: "User", gpx_file: str, with_segments: bool
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert "just a workout" == data["data"]["workouts"][0]["title"]
        if with_segments:
            assert_workout_data_with_gpx_segments(data, user_1)
        else:
            assert_workout_data_with_gpx(data, user_1)
        map_id = data["data"]["workouts"][0]["map"]
        workout_short_id = data["data"]["workouts"][0]["id"]

        response = client.get(
            f"/api/workouts/{workout_short_id}/gpx",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert "" in data["message"]
        assert len(data["data"]["gpx"]) != ""

        response = client.get(
            f"/api/workouts/{workout_short_id}/gpx/segment/1",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert "success" in data["status"]
        assert "" in data["message"]
        assert len(data["data"]["gpx"]) != ""

        response = client.get(
            f"/api/workouts/map/{map_id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        assert response.status_code == 200

    def test_it_gets_a_workout_created_with_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        return self.workout_assertion(app, user_1, gpx_file, False)

    def test_it_gets_a_workout_created_with_gpx_with_segments(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file_with_segments: str,
    ) -> None:
        return self.workout_assertion(
            app, user_1, gpx_file_with_segments, True
        )

    def test_it_gets_chart_data_for_a_workout_created_with_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data["data"]["workouts"][0]["id"]
        response = client.get(
            f"/api/workouts/{workout_short_id}/chart_data",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["message"] == ""
        assert len(data["data"]["chart_data"]) == gpx_file.count("</trkpt>")
        assert data["data"]["chart_data"][0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": "Tue, 13 Mar 2018 12:44:45 GMT",
        }

    def test_it_gets_chart_data_for_a_workout_created_with_gpx_without_elevation(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file_without_elevation: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_without_elevation)),
                    "example.gpx",
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data["data"]["workouts"][0]["id"]
        response = client.get(
            f"/api/workouts/{workout_short_id}/chart_data",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["message"] == ""
        assert len(
            data["data"]["chart_data"]
        ) == gpx_file_without_elevation.count("</trkpt>")
        # no 'elevation' key in data
        assert data["data"]["chart_data"][0] == {
            "distance": 0.0,
            "duration": 0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": "Tue, 13 Mar 2018 12:44:45 GMT",
        }

    def test_it_gets_segment_chart_data_for_a_workout_created_with_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data["data"]["workouts"][0]["id"]
        response = client.get(
            f"/api/workouts/{workout_short_id}/chart_data/segment/1",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["message"] == ""
        assert data["data"]["chart_data"] != ""
        assert len(data["data"]["chart_data"]) == gpx_file.count("</trkpt>")
        assert data["data"]["chart_data"][0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": "Tue, 13 Mar 2018 12:44:45 GMT",
        }

    def test_it_returns_404_on_getting_chart_data_if_workout_belongs_to_another_user(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        user_2: User,
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data["data"]["workouts"][0]["id"]
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            f"/api/workouts/{workout_short_id}/chart_data",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_500_on_invalid_segment_id(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data["data"]["workouts"][0]["id"]
        response = client.get(
            f"/api/workouts/{workout_short_id}/chart_data/segment/0",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response, "Incorrect segment id")

    def test_it_returns_404_if_segment_id_does_not_exist(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts",
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), "example.gpx"),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type="multipart/form-data",
                Authorization=f"Bearer {auth_token}",
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data["data"]["workouts"][0]["id"]
        response = client.get(
            f"/api/workouts/{workout_short_id}/chart_data/segment/999999",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404_with_message(
            response, "No segment with id '999999'"
        )
        assert "data" not in data


class TestPostAndGetWorkoutWithoutGpx(WorkoutApiTestCaseMixin):
    def test_it_add_and_gets_a_workout_wo_gpx(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-05-15 14:05",
                    distance=10,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data["data"]["workouts"][0]["id"]
        response = client.get(
            f"/api/workouts/{workout_short_id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert_workout_data_wo_gpx(data, user_1)

    def test_it_adds_and_gets_a_workout_wo_gpx_notes(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-05-15 14:05",
                    distance=10,
                    notes="new test with notes",
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data["data"]["workouts"][0]["id"]
        response = client.get(
            f"/api/workouts/{workout_short_id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert "new test with notes" == data["data"]["workouts"][0]["notes"]


class TestPostAndGetWorkoutUsingTimezones(WorkoutApiTestCaseMixin):
    def test_it_add_and_gets_a_workout_wo_gpx_with_timezone(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        user_1.timezone = "Europe/Paris"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-05-15 14:05",
                    distance=10,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data["data"]["workouts"][0]["id"]
        response = client.get(
            f"/api/workouts/{workout_short_id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            data["data"]["workouts"][0]["workout_date"]
            == "Tue, 15 May 2018 12:05:00 GMT"
        )
        assert (
            data["data"]["workouts"][0]["title"]
            == f"{sport_1_cycling.label} - 2018-05-15 14:05:00"
        )

    def test_it_adds_and_gets_workouts_date_filter_with_timezone_new_york(
        self, app: "Flask", user_1_full: "User", sport_1_cycling: "Sport"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_full.email
        )

        client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-01-01 00:00",
                    distance=10,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        response = client.get(
            "/api/workouts?from=2018-01-01&to=2018-01-31",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            "Mon, 01 Jan 2018 05:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            f"{sport_1_cycling.label} - 2018-01-01 00:00:00"
            == data["data"]["workouts"][0]["title"]
        )

    def test_it_adds_and_gets_workouts_date_filter_with_timezone_paris(
        self,
        app: "Flask",
        user_1_paris: User,
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_paris.email
        )

        client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2017-31-12 23:59",
                    distance=10,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-01-01 00:00",
                    distance=10,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        workout_cycling_user_1.workout_date = datetime(
            2018, 1, 31, 21, 59, 59, tzinfo=timezone.utc
        )
        workout_cycling_user_1.title = "Test"

        client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date="2018-02-01 00:00",
                    distance=10,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        response = client.get(
            "/api/workouts?from=2018-01-01&to=2018-01-31",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert (
            "Wed, 31 Jan 2018 21:59:59 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert "Test" == data["data"]["workouts"][0]["title"]
        assert (
            "Sun, 31 Dec 2017 23:00:00 GMT"
            == data["data"]["workouts"][1]["workout_date"]
        )
        assert (
            f"{sport_1_cycling.label} - 2018-01-01 00:00:00"
            == data["data"]["workouts"][1]["title"]
        )


class TestPostWorkoutSuspensionAppeal(
    WorkoutApiTestCaseMixin, ReportMixin, BaseTestMixin
):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client = app.test_client()

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
        )

        self.assert_401(response)

    def test_it_returns_404_if_workout_does_not_exist(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        workout_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    def test_it_returns_403_if_user_is_not_workout_owner(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_2: "Workout",
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_400_if_workout_is_not_suspended(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, error_message="workout is not suspended")

    def test_it_returns_400_if_suspended_workout_has_no_report_action(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, error_message="workout has no suspension")

    @pytest.mark.parametrize(
        "input_data", [{}, {"text": ""}, {"comment": "some text"}]
    )
    def test_it_returns_400_when_appeal_text_is_missing(
        self,
        app: "Flask",
        user_1: "User",
        user_2_admin: User,
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        input_data: Dict,
    ) -> None:
        workout_cycling_user_1.suspended_at = datetime.now(timezone.utc)
        self.create_report_workout_action(
            user_2_admin, user_1, workout_cycling_user_1
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(input_data),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "no text provided")

    def test_user_can_appeal_comment_suspension(
        self,
        app: "Flask",
        user_1: "User",
        user_2_admin: User,
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.suspended_at = datetime.now(timezone.utc)
        action = self.create_report_workout_action(
            user_2_admin, user_1, workout_cycling_user_1
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        text = self.random_string()
        now = datetime.now(timezone.utc)

        with travel(now, tick=False):
            response = client.post(
                f"/api/workouts/{workout_cycling_user_1.short_id}/suspension/appeal",
                content_type="application/json",
                data=json.dumps(dict(text=text)),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 201
        assert response.json == {"status": "success"}
        appeal = ReportActionAppeal.query.filter_by(action_id=action.id).one()
        assert appeal.moderator_id is None
        assert appeal.approved is None
        assert appeal.created_at == now
        assert appeal.user_id == user_1.id
        assert appeal.updated_at is None

    def test_user_can_appeal_comment_suspension_only_once(
        self,
        app: "Flask",
        user_1: "User",
        user_2_admin: User,
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.suspended_at = datetime.now(timezone.utc)
        action = self.create_report_workout_action(
            user_2_admin, user_1, workout_cycling_user_1
        )
        db.session.flush()
        appeal = ReportActionAppeal(
            action_id=action.id,
            user_id=user_1.id,
            text=self.random_string(),
        )
        db.session.add(appeal)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/suspension/appeal",
            content_type="application/json",
            data=json.dumps(dict(text=self.random_string())),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, error_message="you can appeal only once")

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/suspension/appeal",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)
