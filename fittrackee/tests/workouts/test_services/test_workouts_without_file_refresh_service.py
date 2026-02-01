from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import TYPE_CHECKING, Dict
from unittest.mock import MagicMock, call, patch

import pytest

from fittrackee import db
from fittrackee.workouts.services.workout_update_service import (
    WorkoutUpdateService,
)
from fittrackee.workouts.services.workouts_without_file_refresh_service import (  # noqa
    WorkoutsWithoutFileRefreshService,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout, WorkoutSegment


test_logger = getLogger("test logger")


class TestWorkoutsWithoutFileRefreshServiceInstantiation:
    def test_it_instantiates_service_when_no_values_provided(
        self, app: "Flask"
    ) -> None:
        service = WorkoutsWithoutFileRefreshService(logger=test_logger)

        assert service.per_page == 10
        assert service.page == 1
        assert service.order == "asc"
        assert service.username is None
        assert service.sport_id is None
        assert service.new_sport_id is None
        assert service.date_from is None
        assert service.date_to is None
        assert service.logger == test_logger
        assert service.verbose is False

    def test_it_instantiates_service_with_given_values(
        self, app: "Flask"
    ) -> None:
        date_from = datetime(2018, 8, 1, 0, 0, tzinfo=timezone.utc)
        date_to = datetime(2018, 8, 12, 0, 0, tzinfo=timezone.utc)
        service = WorkoutsWithoutFileRefreshService(
            logger=test_logger,
            per_page=50,
            page=2,
            order="desc",
            user="Test",
            sport_id=1,
            new_sport_id=2,
            date_from=date_from,
            date_to=date_to,
            verbose=True,
        )

        assert service.per_page == 50
        assert service.page == 2
        assert service.order == "desc"
        assert service.username == "Test"
        assert service.sport_id == 1
        assert service.new_sport_id == 2
        assert service.date_from == date_from
        assert service.date_to == date_to
        assert service.logger == test_logger
        assert service.verbose is True


class TestWorkoutsWithoutFileRefreshServiceRefresh:
    def test_it_instantiates_workout_update_service(
        self, app: "Flask", user_1: "User", workout_cycling_user_1: "Workout"
    ) -> None:
        workout_cycling_user_1.ave_pace = None
        workout_cycling_user_1.best_pace = None
        service = WorkoutsWithoutFileRefreshService(
            logger=test_logger,
        )

        with patch.object(
            WorkoutUpdateService, "__init__", return_value=None
        ) as service_init_mock:
            service.refresh()

        service_init_mock.assert_called_once_with(
            user_1, workout_cycling_user_1, {}
        )

    def test_it_returns_0_when_no_workouts_without_file(
        self,
        app: "Flask",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        service = WorkoutsWithoutFileRefreshService(logger=test_logger)

        count = service.refresh()

        assert count == 0

    def test_it_returns_0_when_workout_without_file_has_pace(
        self,
        app: "Flask",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        service = WorkoutsWithoutFileRefreshService(logger=test_logger)

        count = service.refresh()

        assert count == 0

    def test_it_calls_workout_update_service_for_each_file(
        self,
        app: "Flask",
        workout_running_user_1: "Workout",
        workout_cycling_user_2: "Workout",
    ) -> None:
        workout_running_user_1.ave_pace = None
        workout_running_user_1.best_pace = None
        workout_cycling_user_2.ave_pace = None
        workout_cycling_user_2.best_pace = None
        service = WorkoutsWithoutFileRefreshService(logger=test_logger)

        with patch.object(WorkoutUpdateService, "update") as refresh_mock:
            service.refresh()

        assert refresh_mock.call_count == 2

    def test_it_refreshes_only_user_1_workout(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_2: "Workout",
    ) -> None:
        workout_cycling_user_1.ave_pace = None
        workout_cycling_user_1.best_pace = None
        db.session.commit()
        service = WorkoutsWithoutFileRefreshService(
            logger=test_logger, user=user_1.username
        )

        count = service.refresh()

        assert count == 1
        db.session.refresh(workout_cycling_user_1)
        assert (
            workout_cycling_user_1.sport_id == sport_1_cycling.id
        )  # unchanged
        assert workout_cycling_user_1.ave_pace == timedelta(minutes=6)
        assert workout_cycling_user_1.best_pace == timedelta(minutes=6)

    def test_it_refreshes_workout_associated_to_given_sport(
        self,
        app: "Flask",
        workout_cycling_user_1: "Workout",
        workout_running_user_1: "Workout",
        sport_2_running: "Sport",
    ) -> None:
        workout_cycling_user_1.ave_pace = None
        workout_cycling_user_1.best_pace = None
        workout_running_user_1.ave_pace = None
        workout_running_user_1.best_pace = None
        service = WorkoutsWithoutFileRefreshService(
            logger=test_logger, sport_id=sport_2_running.id
        )

        count = service.refresh()

        assert count == 1

    def test_it_updates_sport_and_refreshes_workout(
        self,
        app: "Flask",
        sport_5_outdoor_tennis: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.ave_pace = None
        workout_cycling_user_1.best_pace = None
        service = WorkoutsWithoutFileRefreshService(
            logger=test_logger, new_sport_id=sport_5_outdoor_tennis.id
        )

        count = service.refresh()

        assert count == 1
        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.sport_id == sport_5_outdoor_tennis.id
        assert workout_cycling_user_1.ave_pace == timedelta(minutes=6)

    def test_it_refreshes_workout_date_from_given_date(
        self,
        app: "Flask",
        workout_cycling_user_1: "Workout",
        workout_running_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.ave_pace = None
        workout_cycling_user_1.best_pace = None
        workout_running_user_1.ave_pace = None
        workout_running_user_1.best_pace = None
        service = WorkoutsWithoutFileRefreshService(
            logger=test_logger,
            date_from=datetime(2018, 4, 2, 0, 0, tzinfo=timezone.utc),
        )

        count = service.refresh()

        assert count == 1
        db.session.refresh(workout_running_user_1)
        assert workout_running_user_1.ave_pace == timedelta(
            minutes=8, seconds=20
        )

    def test_it_refreshes_workout_to_given_date(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        workout_running_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.ave_pace = None
        workout_cycling_user_1.best_pace = None
        workout_running_user_1.ave_pace = None
        workout_running_user_1.best_pace = None
        service = WorkoutsWithoutFileRefreshService(
            logger=test_logger,
            date_to=datetime(2018, 1, 1, 0, 0, tzinfo=timezone.utc),
        )

        count = service.refresh()

        assert count == 1
        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.ave_pace == timedelta(minutes=6)

    @pytest.mark.parametrize(
        "input_params",
        [
            {"page": 1, "per_page": 1, "order": "asc"},
            {"page": 2, "per_page": 1, "order": "desc"},
        ],
    )
    def test_it_refreshes_workout_depending_on_given_pagination_parameters(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        workout_running_user_1: "Workout",
        input_params: Dict,
    ) -> None:
        workout_cycling_user_1.ave_pace = None
        workout_cycling_user_1.best_pace = None
        workout_running_user_1.ave_pace = None
        workout_running_user_1.best_pace = None
        service = WorkoutsWithoutFileRefreshService(
            logger=test_logger, **input_params
        )

        count = service.refresh()

        assert count == 1
        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.ave_pace == timedelta(minutes=6)

    def test_it_displays_logs_when_verbose_is_true(
        self,
        app: "Flask",
        workout_cycling_user_1: "Workout",
        workout_running_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.ave_pace = None
        workout_cycling_user_1.best_pace = None
        workout_running_user_1.ave_pace = None
        workout_running_user_1.best_pace = None
        logger_mock = MagicMock()
        service = WorkoutsWithoutFileRefreshService(
            logger=logger_mock, verbose=True
        )

        service.refresh()

        assert logger_mock.info.call_count == 4
        logger_mock.info.assert_has_calls(
            [
                call("Number of workouts to refresh: 2"),
                call("Refreshing workout 1/2..."),
                call("Refreshing workout 2/2..."),
                call(
                    "\nRefresh done:\n"
                    "- updated workouts: 2\n"
                    "- errored workouts: 0"
                ),
            ]
        )

    def test_it_displays_message_when_logger_is_provided_and_no_workouts_to_refresh(  # noqa
        self, app: "Flask"
    ) -> None:
        """A message will be displayed by CLI"""
        logger_mock = MagicMock()
        service = WorkoutsWithoutFileRefreshService(logger=logger_mock)

        service.refresh()

        assert logger_mock.info.call_count == 1
        logger_mock.info.assert_has_calls([call("No workouts to refresh.")])

    def test_it_continues_on_error(
        self,
        app: "Flask",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        workout_running_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.ave_pace = None
        workout_cycling_user_1.best_pace = None
        workout_running_user_1.ave_pace = None
        workout_running_user_1.best_pace = None
        # should not happen
        workout_cycling_user_1.distance = 999.99
        workout_running_user_1.ave_pace = None
        db.session.commit()
        logger_mock = MagicMock()

        service = WorkoutsWithoutFileRefreshService(
            logger=logger_mock, verbose=True
        )

        count = service.refresh()

        assert count == 1
        assert workout_running_user_1.ave_pace == timedelta(
            minutes=8, seconds=20
        )
        assert logger_mock.info.call_count == 4
        logger_mock.info.assert_has_calls(
            [
                call("Number of workouts to refresh: 2"),
                call("Refreshing workout 1/2..."),
                call("Refreshing workout 2/2..."),
                call(
                    "\nRefresh done:\n"
                    "- updated workouts: 1\n"
                    "- errored workouts: 1"
                ),
            ]
        )
        logger_mock.error.assert_has_calls(
            [
                call(
                    "Error when refreshing workout "
                    f"'{workout_cycling_user_1.short_id}' "
                    f"(user: {user_1.username}): "
                    "one or more values, entered or calculated, "
                    "exceed the limits"
                )
            ]
        )
