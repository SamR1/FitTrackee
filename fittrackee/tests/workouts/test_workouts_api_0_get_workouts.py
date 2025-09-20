import json
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, List
from unittest.mock import patch

import pytest
from flask import Flask
from shapely import to_geojson
from shapely.geometry.multilinestring import MultiLineString

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout, WorkoutSegment

from ..mixins import WorkoutMixin
from ..utils import OAUTH_SCOPES, jsonify_dict
from .mixins import WorkoutApiTestCaseMixin

if TYPE_CHECKING:
    from werkzeug.test import TestResponse


class TestGetWorkouts(WorkoutApiTestCaseMixin):
    def test_it_gets_minimal_workout(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0] == jsonify_dict(
            workout_cycling_user_1.serialize(user=user_1)
        )
        assert "statistics" not in data["data"]

    def test_it_gets_all_workouts_for_authenticated_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_2: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert "creation_date" in data["data"]["workouts"][0]
        assert (
            "Mon, 02 Apr 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert data["data"]["workouts"][0]["user"] == jsonify_dict(
            user_1.serialize()
        )
        assert 2 == data["data"]["workouts"][0]["sport_id"]
        assert 12.0 == data["data"]["workouts"][0]["distance"]
        assert "1:40:00" == data["data"]["workouts"][0]["duration"]

        assert "creation_date" in data["data"]["workouts"][1]
        assert (
            "Mon, 01 Jan 2018 00:00:00 GMT"
            == data["data"]["workouts"][1]["workout_date"]
        )
        assert data["data"]["workouts"][1]["user"] == jsonify_dict(
            user_1.serialize()
        )
        assert 1 == data["data"]["workouts"][1]["sport_id"]
        assert 10.0 == data["data"]["workouts"][1]["distance"]
        assert "1:00:00" == data["data"]["workouts"][1]["duration"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_no_workouts_for_authenticated_user_with_no_workouts(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            "/api/workouts",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 0
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_401_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get("/api/workouts")

        data = json.loads(response.data.decode())
        assert response.status_code == 401
        assert "error" in data["status"]
        assert "provide a valid auth token" in data["message"]

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        suspended_user: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            "/api/workouts",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_gets_only_unsuspended_workouts_for_authenticated_user(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            data["data"]["workouts"][0]["id"]
            == workout_running_user_1.short_id
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
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

        response = client.get(
            "/api/workouts",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestGetWorkoutsWithPagination(WorkoutApiTestCaseMixin):
    def test_it_gets_workouts_with_default_pagination(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert "creation_date" in data["data"]["workouts"][0]
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert "1:00:00" == data["data"]["workouts"][0]["duration"]
        assert "creation_date" in data["data"]["workouts"][4]
        assert (
            "Mon, 01 Jan 2018 00:00:00 GMT"
            == data["data"]["workouts"][4]["workout_date"]
        )
        assert "0:17:04" == data["data"]["workouts"][4]["duration"]
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_first_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?page=1",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert "creation_date" in data["data"]["workouts"][0]
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert "1:00:00" == data["data"]["workouts"][0]["duration"]
        assert "creation_date" in data["data"]["workouts"][4]
        assert (
            "Mon, 01 Jan 2018 00:00:00 GMT"
            == data["data"]["workouts"][4]["workout_date"]
        )
        assert "0:17:04" == data["data"]["workouts"][4]["duration"]
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_second_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert "creation_date" in data["data"]["workouts"][0]
        assert (
            "Sun, 31 Dec 2017 23:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert "0:57:36" == data["data"]["workouts"][0]["duration"]
        assert "creation_date" in data["data"]["workouts"][1]
        assert (
            "Sun, 02 Apr 2017 22:00:00 GMT"
            == data["data"]["workouts"][1]["workout_date"]
        )
        assert "0:17:04" == data["data"]["workouts"][1]["duration"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_empty_third_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?page=3",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 0
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 3,
            "pages": 2,
            "total": 7,
        }

    def test_it_returns_error_on_invalid_page_value(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?page=A",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert "error" in data["status"]
        assert (
            "error, please try again or contact the administrator"
            in data["message"]
        )

    @patch("fittrackee.workouts.workouts.MAX_WORKOUTS_PER_PAGE", 6)
    def test_it_gets_max_workouts_per_page_if_per_page_exceeds_max(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?per_page=10",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 6
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Sun, 31 Dec 2017 23:00:00 GMT"
            == data["data"]["workouts"][5]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }

    @patch("fittrackee.workouts.workouts.MAX_WORKOUTS_PER_PAGE", 6)
    def test_it_gets_given_number_of_workouts_per_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?per_page=3",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 3
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Fri, 23 Feb 2018 10:00:00 GMT"
            == data["data"]["workouts"][2]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 3,
            "total": 7,
        }


class TestGetWorkoutsWithOrder(WorkoutApiTestCaseMixin):
    def test_it_gets_workouts_with_default_order(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Mon, 01 Jan 2018 00:00:00 GMT"
            == data["data"]["workouts"][4]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_workouts_with_ascending_order(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?order=asc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert (
            "Sun, 02 Apr 2017 22:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Fri, 23 Feb 2018 10:00:00 GMT"
            == data["data"]["workouts"][4]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_workouts_with_descending_order(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?order=desc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Mon, 01 Jan 2018 00:00:00 GMT"
            == data["data"]["workouts"][4]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }


class TestGetWorkoutsWithOrderBy(WorkoutApiTestCaseMixin):
    def test_it_gets_workouts_ordered_by_workout_date(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?order_by=workout_date",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Mon, 01 Jan 2018 00:00:00 GMT"
            == data["data"]["workouts"][4]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_workouts_ordered_by_distance(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?order_by=distance",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert 10 == data["data"]["workouts"][0]["distance"]
        assert 8 == data["data"]["workouts"][4]["distance"]
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_workouts_ordered_by_moving_time(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        seven_workouts_user_1[6].duration = seven_workouts_user_1[  # type: ignore
            6
        ].moving + timedelta(seconds=1000)
        db.session.commit()

        response = client.get(
            "/api/workouts?order_by=duration",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert "1:40:00" == data["data"]["workouts"][0]["duration"]
        assert "1:40:00" == data["data"]["workouts"][0]["moving"]
        assert (
            "Sun, 01 Apr 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert "0:57:36" == data["data"]["workouts"][1]["duration"]
        assert "0:57:36" == data["data"]["workouts"][1]["moving"]
        assert (
            "Sun, 31 Dec 2017 23:00:00 GMT"
            == data["data"]["workouts"][1]["workout_date"]
        )
        assert "1:06:40" == data["data"]["workouts"][2]["duration"]
        assert "0:50:00" == data["data"]["workouts"][2]["moving"]
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][2]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_workouts_ordered_by_average_speed(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?order_by=ave_speed",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert 36 == data["data"]["workouts"][0]["ave_speed"]
        assert 10.42 == data["data"]["workouts"][4]["ave_speed"]
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }


class TestGetWorkoutsWithFilters(WorkoutApiTestCaseMixin):
    def test_it_gets_workouts_with_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        equipment_bike_user_1: Equipment,
    ) -> None:
        seven_workouts_user_1[1].equipments = [equipment_bike_user_1]
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?from=2018-02-01&to=2018-02-28",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert "creation_date" in data["data"]["workouts"][0]
        assert (
            "Fri, 23 Feb 2018 10:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert "0:10:00" == data["data"]["workouts"][0]["duration"]
        assert "creation_date" in data["data"]["workouts"][1]
        assert (
            "Fri, 23 Feb 2018 00:00:00 GMT"
            == data["data"]["workouts"][1]["workout_date"]
        )
        assert "0:16:40" == data["data"]["workouts"][1]["duration"]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_no_workouts_with_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?from=2018-03-01&to=2018-03-30",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 0
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_if_gets_workouts_with_date_filter_from(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?from=2018-04-01",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert "creation_date" in data["data"]["workouts"][0]
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Sun, 01 Apr 2018 00:00:00 GMT"
            == data["data"]["workouts"][1]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_workouts_with_date_filter_to(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?to=2017-12-31",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert (
            "Sun, 31 Dec 2017 23:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Sun, 02 Apr 2017 22:00:00 GMT"
            == data["data"]["workouts"][1]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_workouts_with_distance_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?distance_from=5&distance_to=8.1",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert (
            "Sun, 01 Apr 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Sun, 02 Apr 2017 22:00:00 GMT"
            == data["data"]["workouts"][1]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_gets_workouts_with_duration_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?duration_from=00:52&duration_to=01:20",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            "Sun, 31 Dec 2017 23:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    @pytest.mark.parametrize(
        "input_duration",
        [
            "duration_from=00h52&duration_to=01:20",
            "duration_from=00:52&duration_to=01h20",
        ],
    )
    def test_it_returns_400_when_duration_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        input_duration: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts?{input_duration}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, error_message="invalid duration")

    def test_it_gets_workouts_with_average_speed_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?ave_speed_from=5&ave_speed_to=10",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            "Fri, 23 Feb 2018 10:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_gets_workouts_with_max_speed_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.max_speed = 25
        workout_running_user_1.max_speed = 11
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?max_speed_from=10&max_speed_to=20",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            "Mon, 02 Apr 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_gets_workouts_with_sport_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        sport_2_running: Sport,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?sport_id=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            "Mon, 02 Apr 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_gets_one_workout_with_title_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?title=3 of 7",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        workouts = data["data"]["workouts"]
        assert len(workouts) == 1
        assert "Workout 3 of 7" == workouts[0]["title"]
        assert "Mon, 01 Jan 2018 00:00:00 GMT" == workouts[0]["workout_date"]

    def test_it_gets_no_workouts_with_title_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?title=no_such_title",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        workouts = data["data"]["workouts"]
        assert len(workouts) == 0

    def test_it_gets_workouts_with_equipment_id_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        sport_2_running: Sport,
        workout_running_user_1: Workout,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        seven_workouts_user_1[1].equipments = [equipment_bike_user_1]
        seven_workouts_user_1[3].equipments = [equipment_shoes_user_1]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts?equipment_id={equipment_bike_user_1.short_id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            seven_workouts_user_1[1].short_id
            == data["data"]["workouts"][0]["id"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_gets_workouts_without_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        sport_2_running: Sport,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        seven_workouts_user_1[3].equipments = [equipment_bike_user_1]
        seven_workouts_user_1[5].equipments = [equipment_shoes_user_1]
        seven_workouts_user_1[6].equipments = [equipment_shoes_user_1]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?equipment_id=none",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 4
        assert (
            seven_workouts_user_1[4].short_id
            == data["data"]["workouts"][0]["id"]
        )
        assert (
            seven_workouts_user_1[2].short_id
            == data["data"]["workouts"][1]["id"]
        )

        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 4,
        }

    def test_it_gets_workouts_with_notes_filter(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        workout_cycling_user_2: Workout,
    ) -> None:
        notes = self.random_string()
        seven_workouts_user_1[1].notes = notes
        seven_workouts_user_1[3].notes = self.random_string()
        seven_workouts_user_1[
            5
        ].notes = (
            f"{self.random_string()} {notes.upper()} {self.random_string()}"
        )
        workout_cycling_user_2.notes = notes
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts?notes={notes}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        workouts = data["data"]["workouts"]
        assert len(workouts) == 2
        assert workouts[0]["id"] == seven_workouts_user_1[5].short_id
        assert workouts[1]["id"] == seven_workouts_user_1[1].short_id

    def test_it_returns_all_workouts_when_notes_filter_is_empty_string(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.notes = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?notes=",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        workouts = data["data"]["workouts"]
        assert len(workouts) == 2
        assert workouts[0]["id"] == workout_running_user_1.short_id
        assert workouts[1]["id"] == workout_cycling_user_1.short_id

    def test_it_gets_workouts_with_description_filter(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        workout_cycling_user_2: Workout,
    ) -> None:
        description = self.random_string()
        seven_workouts_user_1[1].description = description
        seven_workouts_user_1[3].description = self.random_string()
        seven_workouts_user_1[5].description = (
            f"{self.random_string()} {description.upper()} "
            f"{self.random_string()}"
        )
        workout_cycling_user_2.description = description
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts?description={description}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        workouts = data["data"]["workouts"]
        assert len(workouts) == 2
        assert workouts[0]["id"] == seven_workouts_user_1[5].short_id
        assert workouts[1]["id"] == seven_workouts_user_1[1].short_id

    def test_it_returns_all_workouts_when_description_filter_is_empty_string(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.description = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?description=",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        workouts = data["data"]["workouts"]
        assert len(workouts) == 2
        assert workouts[0]["id"] == workout_running_user_1.short_id
        assert workouts[1]["id"] == workout_cycling_user_1.short_id

    def test_it_filters_workouts_on_visibility(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        another_workout_cycling_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
    ) -> None:
        another_workout_cycling_user_1.workout_visibility = (
            VisibilityLevel.FOLLOWERS
        )
        workout_running_user_1.workout_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?workout_visibility=followers_only",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        workouts = data["data"]["workouts"]
        assert len(workouts) == 1
        assert workouts[0]["id"] == another_workout_cycling_user_1.short_id

    def test_it_returns_400_when_visibility_is_invalid(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?workout_visibility=invalid",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid value for visibility")


class TestGetWorkoutsWithLocationFilters(WorkoutApiTestCaseMixin):
    def test_it_does_not_return_workouts_when_to_far_from_given_coordinates(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?coordinates=44.564511,6.08716&radius=12",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["data"]["workouts"] == []

    def test_it_get_workout_matching_given_location_and_distance(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?coordinates=44.564511,6.087168&radius=20",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        workouts = data["data"]["workouts"]
        assert len(workouts) == 1
        assert (
            workouts[0]["id"]
            == workout_cycling_user_1_with_coordinates.short_id
        )

    def test_it_returns_400_when_radius_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?coordinates=44.564511,6.087168&radius=-1",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            error_message="invalid radius, must be an float greater than zero",
        )


class TestGetWorkoutsWithFiltersAndPagination(WorkoutApiTestCaseMixin):
    def test_it_gets_page_2_with_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?from=2017-01-01&page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert (
            "Sun, 31 Dec 2017 23:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Sun, 02 Apr 2017 22:00:00 GMT"
            == data["data"]["workouts"][1]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 7,
        }

    def test_it_get_page_2_with_date_filter_and_ascending_order(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?from=2017-01-01&page=2&order=asc",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert (
            "Sun, 01 Apr 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][1]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_all_workouts_with_title_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?title=of 7",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }


class TestGetWorkoutsWithEquipments(WorkoutApiTestCaseMixin):
    @pytest.mark.parametrize("input_params", ["", "?return_equipments=false"])
    def test_it_returns_workout_without_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
        input_params: str,
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts{input_params}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["data"]["workouts"][0]["equipments"] == []

    def test_it_returns_workout_with_equipments_when_flag_is_true(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?return_equipments=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["data"]["workouts"][0]["equipments"] == [
            jsonify_dict(equipment_bike_user_1.serialize(current_user=user_1))
        ]


class TestGetWorkoutsWithStatistics(WorkoutApiTestCaseMixin, WorkoutMixin):
    def test_it_gets_workouts_with_stats_when_no_workouts_for_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["data"]["workouts"] == []
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": None,
            "average_descent": None,
            "average_distance": None,
            "average_duration": None,
            "average_speed": None,
            "count": 0,
            "max_speed": None,
            "total_ascent": None,
            "total_descent": None,
            "total_distance": None,
            "total_duration": None,
            "total_sports": 0,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_when_only_one_workout_exists(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": workout_cycling_user_1.ascent,
            "average_descent": workout_cycling_user_1.descent,
            "average_distance": workout_cycling_user_1.distance,
            "average_duration": str(workout_cycling_user_1.moving),
            "average_speed": workout_cycling_user_1.ave_speed,
            "count": 1,
            "max_speed": workout_cycling_user_1.max_speed,
            "total_ascent": workout_cycling_user_1.ascent,
            "total_descent": workout_cycling_user_1.descent,
            "total_distance": workout_cycling_user_1.distance,
            "total_duration": str(workout_cycling_user_1.moving),
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_with_outdoor_tennis_workout(
        self,
        app: Flask,
        user_1: User,
        workout_outdoor_tennis_user_1_with_elevation_data: Workout,
    ) -> None:
        tennis_workout = workout_outdoor_tennis_user_1_with_elevation_data
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": None,
            "average_descent": None,
            "average_distance": tennis_workout.distance,
            "average_duration": str(tennis_workout.moving),
            "average_speed": tennis_workout.ave_speed,
            "count": 1,
            "max_speed": tennis_workout.max_speed,
            "total_ascent": None,
            "total_descent": None,
            "total_distance": tennis_workout.distance,
            "total_duration": str(tennis_workout.moving),
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_with_outdoor_tennis_and_cycling_workouts(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_5_outdoor_tennis: Sport,
        workout_cycling_user_1: Workout,
        workout_outdoor_tennis_user_1_with_elevation_data: Workout,
    ) -> None:
        workout_cycling_user_1 = self.update_workout_with_file_data(
            workout_cycling_user_1,
            ascent=50,
            descent=60,
            max_alt=300,
            min_alt=250,
        )
        tennis_workout = workout_outdoor_tennis_user_1_with_elevation_data
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": workout_cycling_user_1.ascent,
            "average_descent": workout_cycling_user_1.descent,
            "average_distance": (
                (workout_cycling_user_1.distance + tennis_workout.distance) / 2  # type: ignore[operator]
            ),
            "average_duration": str(
                (workout_cycling_user_1.duration + tennis_workout.duration) / 2
            ),
            "average_speed": None,
            "count": 2,
            "max_speed": None,
            "total_ascent": workout_cycling_user_1.ascent,
            "total_descent": workout_cycling_user_1.descent,
            "total_distance": (
                workout_cycling_user_1.distance + tennis_workout.distance  # type: ignore[operator]
            ),
            "total_duration": str(
                workout_cycling_user_1.duration + tennis_workout.duration
            ),
            "total_sports": 2,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_when_total_workouts_exceed_limit(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        app.config["stats_workouts_limit"] = 6
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": 85.0,
            "average_descent": 125.0,
            "average_distance": 7.8,
            "average_duration": "0:38:44",
            "average_speed": 18.79,
            "count": 5,
            "max_speed": 36.0,
            "total_ascent": 340.0,
            "total_descent": 500.0,
            "total_distance": 39.0,
            "total_duration": "3:13:44",
            "total_sports": 1,
        }
        assert data["data"]["statistics"]["all"] == {
            "average_ascent": 88.0,
            "average_descent": 116.0,
            "average_distance": 8.17,
            "average_duration": "0:41:53",
            "average_speed": 17.4,
            "count": 6,
            "max_speed": 36.00,
            "total_ascent": 440.0,
            "total_descent": 580.0,
            "total_distance": 49.0,
            "total_duration": "4:11:20",
            "total_sports": 1,
        }
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_workouts_with_stats_when_workouts_limit_below_per_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        app.config["stats_workouts_limit"] = 6
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?with_statistics=true&per_page=10",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 7
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": 93.33,
            "average_descent": 130.0,
            "average_distance": 7.71,
            "average_duration": "0:38:20",
            "average_speed": 17.42,
            "count": 7,
            "max_speed": 36.0,
            "total_ascent": 560.0,
            "total_descent": 780.0,
            "total_distance": 54.0,
            "total_duration": "4:28:24",
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 7,
        }

    def test_it_gets_page_2_with_stats(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?with_statistics=true&page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": 110.0,
            "average_descent": 140.0,
            "average_distance": 7.5,
            "average_duration": "0:37:20",
            "average_speed": 14.0,
            "count": 2,
            "max_speed": 17.58,
            "total_ascent": 220.0,
            "total_descent": 280.0,
            "total_distance": 15.0,
            "total_duration": "1:14:40",
            "total_sports": 1,
        }
        assert data["data"]["statistics"]["all"] == {
            "average_ascent": 93.33,
            "average_descent": 130.0,
            "average_distance": 7.71,
            "average_duration": "0:38:20",
            "average_speed": 17.42,
            "count": 7,
            "max_speed": 36.00,
            "total_ascent": 560.0,
            "total_descent": 780.0,
            "total_distance": 54.0,
            "total_duration": "4:28:24",
            "total_sports": 1,
        }
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_workouts_with_stats_and_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        equipment_bike_user_1: Equipment,
    ) -> None:
        seven_workouts_user_1[1].equipments = [equipment_bike_user_1]
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?from=2018-02-01&to=2018-02-28&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": 110.0,
            "average_descent": 190.0,
            "average_distance": 5.5,
            "average_duration": "0:13:20",
            "average_speed": 21.0,
            "count": 2,
            "max_speed": 36.0,
            "total_ascent": 220.0,
            "total_descent": 380.0,
            "total_distance": 11.0,
            "total_duration": "0:26:40",
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_distance_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?distance_from=5&distance_to=8.1&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": 80.0,
            "average_descent": 110.0,
            "average_distance": 6.5,
            "average_duration": "0:58:32",
            "average_speed": 11.19,
            "count": 2,
            "max_speed": 17.58,
            "total_ascent": 160.0,
            "total_descent": 220.0,
            "total_distance": 13.0,
            "total_duration": "1:57:04",
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_duration_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?duration_from=00:52&duration_to=01:20&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        workout = data["data"]["workouts"][0]
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": workout["ascent"],
            "average_descent": workout["descent"],
            "average_distance": workout["distance"],
            "average_duration": workout["duration"],
            "average_speed": workout["ave_speed"],
            "count": 1,
            "max_speed": workout["max_speed"],
            "total_ascent": workout["ascent"],
            "total_descent": workout["descent"],
            "total_distance": workout["distance"],
            "total_duration": workout["duration"],
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_and_average_speed_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?ave_speed_from=5&ave_speed_to=10&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        workout = data["data"]["workouts"][0]
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": workout["ascent"],
            "average_descent": workout["descent"],
            "average_distance": workout["distance"],
            "average_duration": workout["duration"],
            "average_speed": workout["ave_speed"],
            "count": 1,
            "max_speed": workout["max_speed"],
            "total_ascent": workout["ascent"],
            "total_descent": workout["descent"],
            "total_distance": workout["distance"],
            "total_duration": workout["duration"],
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_and_max_speed_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.max_speed = 25
        workout_running_user_1.max_speed = 11
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?max_speed_from=10&max_speed_to=20&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        workout = data["data"]["workouts"][0]
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": workout["ascent"],
            "average_descent": workout["descent"],
            "average_distance": workout["distance"],
            "average_duration": workout["duration"],
            "average_speed": workout["ave_speed"],
            "count": 1,
            "max_speed": workout["max_speed"],
            "total_ascent": workout["ascent"],
            "total_descent": workout["descent"],
            "total_distance": workout["distance"],
            "total_duration": workout["duration"],
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_and_sport_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        sport_2_running: Sport,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?sport_id=2&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        workout = data["data"]["workouts"][0]
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": workout["ascent"],
            "average_descent": workout["descent"],
            "average_distance": workout["distance"],
            "average_duration": workout["duration"],
            "average_speed": workout["ave_speed"],
            "count": 1,
            "max_speed": workout["max_speed"],
            "total_ascent": workout["ascent"],
            "total_descent": workout["descent"],
            "total_distance": workout["distance"],
            "total_duration": workout["duration"],
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_and_title_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?title=3 of 7&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        workout = data["data"]["workouts"][0]
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": workout["ascent"],
            "average_descent": workout["descent"],
            "average_distance": workout["distance"],
            "average_duration": workout["duration"],
            "average_speed": workout["ave_speed"],
            "count": 1,
            "max_speed": workout["max_speed"],
            "total_ascent": workout["ascent"],
            "total_descent": workout["descent"],
            "total_distance": workout["distance"],
            "total_duration": workout["duration"],
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_and_equipment_id_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        sport_2_running: Sport,
        workout_running_user_1: Workout,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        seven_workouts_user_1[1].equipments = [equipment_bike_user_1]
        seven_workouts_user_1[3].equipments = [equipment_shoes_user_1]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts?equipment_id={equipment_bike_user_1.short_id}&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        workout = data["data"]["workouts"][0]
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": workout["ascent"],
            "average_descent": workout["descent"],
            "average_distance": workout["distance"],
            "average_duration": workout["duration"],
            "average_speed": workout["ave_speed"],
            "count": 1,
            "max_speed": workout["max_speed"],
            "total_ascent": workout["ascent"],
            "total_descent": workout["descent"],
            "total_distance": workout["distance"],
            "total_duration": workout["duration"],
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_and_notes_filter(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        workout_cycling_user_2: Workout,
    ) -> None:
        notes = self.random_string()
        seven_workouts_user_1[1].notes = notes
        seven_workouts_user_1[3].notes = self.random_string()
        seven_workouts_user_1[
            5
        ].notes = (
            f"{self.random_string()} {notes.upper()} {self.random_string()}"
        )
        workout_cycling_user_2.notes = notes
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts?notes={notes}&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        workouts = data["data"]["workouts"]
        assert len(workouts) == 2
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": 70.0,
            "average_descent": 50.0,
            "average_distance": 9.0,
            "average_duration": "1:18:48",
            "average_speed": 7.61,
            "count": 2,
            "max_speed": 10.42,
            "total_ascent": 140.0,
            "total_descent": 100.0,
            "total_distance": 18.0,
            "total_duration": "2:37:36",
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_and_description_filter(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        workout_cycling_user_2: Workout,
    ) -> None:
        description = self.random_string()
        seven_workouts_user_1[1].description = description
        seven_workouts_user_1[3].description = self.random_string()
        seven_workouts_user_1[5].description = (
            f"{self.random_string()} {description.upper()} "
            f"{self.random_string()}"
        )
        workout_cycling_user_2.description = description
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts?description={description}&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        workouts = data["data"]["workouts"]
        assert len(workouts) == 2
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": 70.0,
            "average_descent": 50.0,
            "average_distance": 9.0,
            "average_duration": "1:18:48",
            "average_speed": 7.61,
            "count": 2,
            "max_speed": 10.42,
            "total_ascent": 140.0,
            "total_descent": 100.0,
            "total_distance": 18.0,
            "total_duration": "2:37:36",
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_and_filter_on_visibility(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        another_workout_cycling_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
    ) -> None:
        another_workout_cycling_user_1.workout_visibility = (
            VisibilityLevel.FOLLOWERS
        )
        workout_running_user_1.workout_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?workout_visibility=followers_only&with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        workout = data["data"]["workouts"][0]
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": workout["ascent"],
            "average_descent": workout["descent"],
            "average_distance": workout["distance"],
            "average_duration": workout["duration"],
            "average_speed": workout["ave_speed"],
            "count": 1,
            "max_speed": workout["max_speed"],
            "total_ascent": workout["ascent"],
            "total_descent": workout["descent"],
            "total_distance": workout["distance"],
            "total_duration": workout["duration"],
            "total_sports": 1,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_when_multiple_sports_and_one_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.ascent = 100
        workout_cycling_user_1.descent = 120
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 2
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": 100.0,
            "average_descent": 120.0,
            "average_distance": 11.0,
            "average_duration": "1:20:00",
            "average_speed": None,
            "count": 2,
            "max_speed": None,
            "total_ascent": float(workout_cycling_user_1.ascent),
            "total_descent": float(workout_cycling_user_1.descent),
            "total_distance": float(
                workout_cycling_user_1.distance  # type: ignore
                + workout_running_user_1.distance
            ),
            "total_duration": str(
                workout_cycling_user_1.duration  # type: ignore
                + workout_running_user_1.duration
            ),
            "total_sports": 2,
        }
        assert (
            data["data"]["statistics"]["all"]
            == data["data"]["statistics"]["current_page"]
        )

    def test_it_gets_workouts_with_stats_for_page_1_when_multiple_sports(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: List[Workout],
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?with_statistics=true",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 5
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": 86.67,
            "average_descent": 133.33,
            "average_distance": 8.2,
            "average_duration": "0:55:20",
            "average_speed": None,
            "count": 5,
            "max_speed": None,
            "total_ascent": 260.0,
            "total_descent": 400.0,
            "total_distance": 41.0,
            "total_duration": "4:36:40",
            "total_sports": 2,
        }
        assert data["data"]["statistics"]["all"] == {
            "average_ascent": 93.33,
            "average_descent": 130.0,
            "average_distance": 8.25,
            "average_duration": "0:46:03",
            "average_speed": None,
            "count": 8,
            "max_speed": None,
            "total_ascent": 560.0,
            "total_descent": 780.0,
            "total_distance": 66.0,
            "total_duration": "6:08:24",
            "total_sports": 2,
        }

    def test_it_gets_workouts_with_stats_for_page_2_when_multiple_sports(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: List[Workout],
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?with_statistics=true&page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 3
        assert data["data"]["statistics"]["current_page"] == {
            "average_ascent": 100.0,
            "average_descent": 126.67,
            "average_distance": 8.33,
            "average_duration": "0:30:34",
            "average_speed": 21.05,
            "count": 3,
            "max_speed": 35.16,
            "total_ascent": 300.0,
            "total_descent": 380.0,
            "total_distance": 25.0,
            "total_duration": "1:31:44",
            "total_sports": 1,
        }
        assert data["data"]["statistics"]["all"] == {
            "average_ascent": 93.33,
            "average_descent": 130.0,
            "average_distance": 8.25,
            "average_duration": "0:46:03",
            "average_speed": None,
            "count": 8,
            "max_speed": None,
            "total_ascent": 560.0,
            "total_descent": 780.0,
            "total_distance": 66.0,
            "total_duration": "6:08:24",
            "total_sports": 2,
        }


class TestGetWorkoutsFeatureCollection(WorkoutApiTestCaseMixin):
    """
    Since query generation is shared with `/workouts` endpoints, no need to
    test all filters
    """

    def test_it_returns_401_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get("/api/workouts/collection")

        data = json.loads(response.data.decode())
        assert response.status_code == 401
        assert "error" in data["status"]
        assert "provide a valid auth token" in data["message"]

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        suspended_user: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            "/api/workouts/collection",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_empty_collection_when_no_workouts(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts/collection",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == {
            "bbox": [],
            "features": [],
            "type": "FeatureCollection",
        }
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_empty_collection_when_only_workouts_without_files(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        another_workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts/collection",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == {
            "bbox": [],
            "features": [],
            "type": "FeatureCollection",
        }
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_returns_only_workouts_with_geometry_in_feature_collection(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        workout_cycling_user_1_segment_0_coordinates: List[List],
        workout_cycling_user_1_segment_1_with_coordinates: WorkoutSegment,
        workout_cycling_user_1_segment_1_coordinates: List[List],
        another_workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts/collection",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == {
            "bbox": [
                6.07355,
                44.67822,
                6.07442,
                44.68095,
            ],
            "features": [
                {
                    "type": "Feature",
                    "geometry": json.loads(
                        to_geojson(
                            MultiLineString(
                                [
                                    workout_cycling_user_1_segment_0_coordinates,
                                    workout_cycling_user_1_segment_1_coordinates,
                                ]
                            )
                        )
                    ),
                    "properties": {
                        "bounds": (
                            workout_cycling_user_1_with_coordinates.bounds
                        ),
                        "id": workout_cycling_user_1_with_coordinates.short_id,
                        "sport_id": (
                            workout_cycling_user_1_with_coordinates.sport_id
                        ),
                        "title": workout_cycling_user_1_with_coordinates.title,
                        "workout_visibility": (
                            workout_cycling_user_1_with_coordinates.workout_visibility
                        ),
                    },
                },
            ],
            "type": "FeatureCollection",
        }
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_filters_on_sport(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        workout_cycling_user_1_segment_0_coordinates: List[List],
        workout_cycling_user_1_segment_1_with_coordinates: WorkoutSegment,
        workout_cycling_user_1_segment_1_coordinates: List[List],
        another_workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/collection?sport_id={sport_2_running.id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == {
            "bbox": [],
            "features": [],
            "type": "FeatureCollection",
        }
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_returns_400_when_duration_is_invalid(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts/collection?duration_from=00h52&duration_to=01:20",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, error_message="invalid duration")

    def test_it_returns_400_when_radius_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts/collection?coordinates=44.564511,6.087168&radius=-1",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            error_message="invalid radius, must be an float greater than zero",
        )

    def test_it_returns_400_when_workout_visibility_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts/collection?workout_visibility=invalid",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, error_message="invalid value for visibility")

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
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

        response = client.get(
            "/api/workouts/collection",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestGetWorkoutsForGlobalMap(WorkoutApiTestCaseMixin):
    route = "/api/workouts/global-map"

    @staticmethod
    def assert_no_features(response: "TestResponse") -> None:
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            "data": {
                "bbox": [],
                "features": [],
                "limit_exceeded": False,
                "type": "FeatureCollection",
            },
            "status": "success",
        }

    def test_it_returns_401_if_user_is_not_authenticated(
        self, app: "Flask"
    ) -> None:
        client = app.test_client()

        response = client.get(self.route)

        data = json.loads(response.data.decode())
        assert response.status_code == 401
        assert "error" in data["status"]
        assert "provide a valid auth token" in data["message"]

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: "Flask",
        user_1: "User",
        suspended_user: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        workout_running_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            self.route, headers=dict(Authorization=f"Bearer {auth_token}")
        )

        self.assert_403(response)

    def test_it_returns_empty_collection_when_no_workouts_for_auth_user(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_0_coordinates: List[List],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route, headers=dict(Authorization=f"Bearer {auth_token}")
        )

        self.assert_no_features(response)

    def test_it_returns_empty_collection_when_only_workouts_without_files(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        another_workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route, headers=dict(Authorization=f"Bearer {auth_token}")
        )

        self.assert_no_features(response)

    def test_it_returns_workouts_with_start_point_as_feature_collection(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_0_coordinates: List[List],
        workout_cycling_user_1_segment_1_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_coordinates: List[List],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts/global-map",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == {
            "bbox": [
                6.07367,
                44.68095,
                6.07367,
                44.68095,
            ],
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "coordinates": [6.07367, 44.68095],
                        "type": "Point",
                    },
                    "properties": {
                        "bounds": (
                            workout_cycling_user_1_with_coordinates.bounds
                        ),
                        "id": workout_cycling_user_1_with_coordinates.short_id,
                        "sport_id": (
                            workout_cycling_user_1_with_coordinates.sport_id
                        ),
                        "title": workout_cycling_user_1_with_coordinates.title,
                        "workout_visibility": (
                            workout_cycling_user_1_with_coordinates.workout_visibility
                        ),
                    },
                },
            ],
            "limit_exceeded": False,
            "type": "FeatureCollection",
        }

    def test_it_does_return_suspended_workout(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_0_coordinates: List[List],
    ) -> None:
        workout_cycling_user_1_with_coordinates.suspended_at = datetime.now(
            tz=timezone.utc
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts/global-map",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_no_features(response)

    def test_it_filters_workouts_on_sport_ids(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        sport_3_cycling_transport: "Sport",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_0_coordinates: List[List],
        workout_cycling_user_1_segment_1_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_coordinates: List[List],
        workout_running_user_1_with_coordinates: "Workout",
        workout_running_user_1_segment_with_coordinates: "WorkoutSegment",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            (
                f"{self.route}?sport_ids="
                f"{sport_1_cycling.id},{sport_3_cycling_transport.id}"
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == {
            "bbox": [
                6.07367,
                44.68095,
                6.07367,
                44.68095,
            ],
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "coordinates": [6.07367, 44.68095],
                        "type": "Point",
                    },
                    "properties": {
                        "bounds": (
                            workout_cycling_user_1_with_coordinates.bounds
                        ),
                        "id": workout_cycling_user_1_with_coordinates.short_id,
                        "sport_id": (
                            workout_cycling_user_1_with_coordinates.sport_id
                        ),
                        "title": workout_cycling_user_1_with_coordinates.title,
                        "workout_visibility": (
                            workout_cycling_user_1_with_coordinates.workout_visibility
                        ),
                    },
                },
            ],
            "limit_exceeded": False,
            "type": "FeatureCollection",
        }

    def test_it_returns_400_when_sport_ids_are_invalid(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?sport_ids=1,invalid",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, error_message="invalid sport_ids")

    def test_it_returns_workouts_created_after_from_date(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        sport_3_cycling_transport: "Sport",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_0_coordinates: List[List],
        workout_cycling_user_1_segment_1_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_coordinates: List[List],
        workout_running_user_1_with_coordinates: "Workout",
        workout_running_user_1_segment_with_coordinates: "WorkoutSegment",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?from=2018-04-01",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["data"]["features"][0]["properties"]["id"] == (
            workout_running_user_1_with_coordinates.short_id
        )

    def test_it_returns_workouts_created_after_to_date(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        sport_3_cycling_transport: "Sport",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_0_coordinates: List[List],
        workout_cycling_user_1_segment_1_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_coordinates: List[List],
        workout_running_user_1_with_coordinates: "Workout",
        workout_running_user_1_segment_with_coordinates: "WorkoutSegment",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?to=2018-04-01",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["data"]["features"][0]["properties"]["id"] == (
            workout_cycling_user_1_with_coordinates.short_id
        )

    def test_it_returns_400_when_date_format_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?to=2018-04",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, error_message="invalid date format, expecting '%Y-%m-%d'"
        )

    def test_it_returns_most_recent_workouts_when_total_workouts_exceed_limit(
        self,
        app_with_global_map_workouts_limit_equal_to_1: Flask,
        user_1: User,
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_0_coordinates: List[List],
        workout_cycling_user_1_segment_1_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_coordinates: List[List],
        workout_running_user_1_with_coordinates: "Workout",
        workout_running_user_1_segment_with_coordinates: "WorkoutSegment",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_global_map_workouts_limit_equal_to_1, user_1.email
        )

        response = client.get(
            self.route,
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["data"]["limit_exceeded"] is True
        assert len(data["data"]["features"]) == 1
        assert data["data"]["features"][0]["properties"]["id"] == (
            workout_running_user_1_with_coordinates.short_id
        )

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
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

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)
