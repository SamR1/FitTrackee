import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict

import pytest
from flask import Flask
from jsonschema import ValidationError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from time_machine import travel

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.files import get_absolute_file_path
from fittrackee.reports.models import ReportAction
from fittrackee.tests.comments.mixins import CommentMixin
from fittrackee.users.exceptions import (
    BlockUserException,
    FollowRequestAlreadyProcessedError,
    NotExistingFollowRequestError,
    UserTaskException,
    UserTaskForbiddenException,
)
from fittrackee.users.models import (
    BlacklistedToken,
    BlockedUser,
    FollowRequest,
    Notification,
    User,
    UserSportPreference,
    UserSportPreferenceEquipment,
    UserTask,
)
from fittrackee.users.roles import UserRole
from fittrackee.workouts.models import Sport, Workout

from ..mixins import RandomMixin, ReportMixin, UserTaskMixin

NOTIFICATION_TYPES_FOR_PREFERENCES = [
    "account_creation",
    "comment_like",
    "follow",
    "follow_request",
    "follow_request_approved",
    "mention",
    "workout_comment",
    "workout_like",
]


class TestUserModel:
    def test_it_returns_username_in_string_value(
        self, app: Flask, user_1: User
    ) -> None:
        assert "<User 'test'>" == str(user_1)


class TestUserModelRole(RandomMixin):
    def test_role_is_user_by_default(self, app: Flask) -> None:
        user = User(
            username=self.random_string(),
            email=self.random_email(),
            password=self.random_string(),
        )
        db.session.add(user)
        db.session.commit()

        assert user.role == UserRole.USER.value
        assert user.has_moderator_rights is False
        assert user.has_admin_rights is False

    def test_user_has_moderator_rights(self, app: Flask) -> None:
        user = User(
            username=self.random_string(),
            email=self.random_email(),
            password=self.random_string(),
        )
        db.session.add(user)
        db.session.flush()

        user.role = UserRole.MODERATOR.value
        db.session.commit()

        assert user.has_moderator_rights is True
        assert user.has_admin_rights is False

    def test_user_has_admin_rights(self, app: Flask) -> None:
        user = User(
            username=self.random_string(),
            email=self.random_email(),
            password=self.random_string(),
        )
        db.session.add(user)
        db.session.flush()

        user.role = UserRole.ADMIN.value
        db.session.commit()

        assert user.has_moderator_rights is True
        assert user.has_admin_rights is True

    def test_it_raises_error_when_role_is_auth_user(self, app: Flask) -> None:
        user = User(
            username=self.random_string(),
            email=self.random_email(),
            password=self.random_string(),
        )
        db.session.add(user)
        db.session.flush()

        with pytest.raises(
            IntegrityError,
            match=re.escape(
                "(psycopg2.errors.CheckViolation) new row for relation "
                '"users" violates check constraint "ck_users_role"'
            ),
        ):
            user.role = UserRole.AUTH_USER.value
            db.session.commit()


class UserModelAssertMixin:
    @staticmethod
    def assert_user_account(serialized_user: Dict, user: User) -> None:
        assert serialized_user["role"] == UserRole(user.role).name.lower()
        assert serialized_user["is_active"] == user.is_active
        assert serialized_user["username"] == user.username
        assert serialized_user["suspended_at"] is None
        assert "suspension_report_id" not in serialized_user

    @staticmethod
    def assert_user_profile(serialized_user: Dict, user: User) -> None:
        assert serialized_user["bio"] == user.bio
        assert serialized_user["birth_date"] == user.birth_date
        assert serialized_user["first_name"] == user.first_name
        assert serialized_user["last_name"] == user.last_name
        assert serialized_user["location"] == user.location
        assert serialized_user["picture"] is False

    @staticmethod
    def assert_workouts_keys_are_present(serialized_user: Dict) -> None:
        assert "nb_sports" in serialized_user
        assert "nb_workouts" in serialized_user
        assert "records" in serialized_user
        assert "sports_list" in serialized_user
        assert "total_ascent" in serialized_user
        assert "total_distance" in serialized_user
        assert "total_duration" in serialized_user


class TestUserSerializeAsAuthUser(UserModelAssertMixin):
    def test_it_returns_user_account_infos(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        self.assert_user_account(serialized_user, user_1)
        assert serialized_user["email"] == user_1.email
        assert serialized_user["email_to_confirm"] == user_1.email_to_confirm

    def test_it_returns_user_profile_infos(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        self.assert_user_profile(serialized_user, user_1)
        assert "blocked" not in serialized_user

    def test_it_returns_user_preferences(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.update_preferences({"mention": True})
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["imperial_units"] == user_1.imperial_units
        assert serialized_user["language"] == user_1.language
        assert serialized_user["timezone"] == user_1.timezone
        assert serialized_user["weekm"] == user_1.weekm
        assert serialized_user["display_ascent"] == user_1.display_ascent
        assert (
            serialized_user["start_elevation_at_zero"]
            == user_1.start_elevation_at_zero
        )
        assert serialized_user["use_raw_gpx_speed"] == user_1.use_raw_gpx_speed
        assert serialized_user["use_dark_mode"] == user_1.use_dark_mode
        assert (
            serialized_user["workouts_visibility"]
            == user_1.workouts_visibility
        )
        assert (
            serialized_user["analysis_visibility"]
            == user_1.analysis_visibility
        )
        assert serialized_user["map_visibility"] == user_1.map_visibility
        assert (
            serialized_user["manually_approves_followers"]
            == user_1.manually_approves_followers
        )
        assert (
            serialized_user["hide_profile_in_users_directory"]
            == user_1.hide_profile_in_users_directory
        )
        assert (
            serialized_user["notification_preferences"]
            == user_1.notification_preferences
        )
        assert serialized_user["hr_visibility"] == user_1.hr_visibility
        assert (
            serialized_user["segments_creation_event"]
            == user_1.segments_creation_event
        )

    def test_it_returns_empty_dict_when_notification_preferences_are_none(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["notification_preferences"] == {}

    def test_it_returns_workouts_infos(self, app: Flask, user_1: User) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        self.assert_workouts_keys_are_present(serialized_user)

    def test_it_returns_none_when_user_did_not_accept_default_privacy_policy(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.accepted_policy_date = None
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["accepted_privacy_policy"] is None

    def test_it_returns_true_user_did_accept_default_privacy_policy(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.accepted_policy_date = datetime.now(timezone.utc)
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["accepted_privacy_policy"] is True

    def test_it_returns_false_when_user_did_not_accept_last_default_policy(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.accepted_policy_date = datetime.strptime(
            app.config["DEFAULT_PRIVACY_POLICY_DATA"],
            "%Y-%m-%d %H:%M:%S",
        ).replace(tzinfo=timezone.utc) - timedelta(days=1)
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["accepted_privacy_policy"] is False

    def test_it_returns_false_when_user_did_not_accept_last_custom_policy(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.accepted_policy_date = datetime.now(timezone.utc)
        # custom privacy policy
        app.config["privacy_policy_date"] = datetime.now(timezone.utc)
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["accepted_privacy_policy"] is False

    def test_it_returns_user_did_accept_last_policy(
        self, app: Flask, user_1: User
    ) -> None:
        # custom privacy policy
        app.config["privacy_policy_date"] = datetime.now(timezone.utc)
        user_1.accepted_policy_date = datetime.now(timezone.utc)
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["accepted_privacy_policy"] is True

    def test_it_does_not_return_confirmation_token(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert "confirmation_token" not in serialized_user

    def test_it_does_not_return_reports_info(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert "created_reports_count" not in serialized_user
        assert "reported_count" not in serialized_user
        assert serialized_user["sanctions_count"] == 0

    def test_it_does_return_reports_info_when_user_has_admin_rights(
        self, app: Flask, user_1_admin: User
    ) -> None:
        serialized_user = user_1_admin.serialize(
            current_user=user_1_admin, light=False
        )

        assert serialized_user["created_reports_count"] == 0
        assert serialized_user["reported_count"] == 0
        assert serialized_user["sanctions_count"] == 0


class TestUserSerializeAsAdmin(UserModelAssertMixin, ReportMixin):
    def test_it_returns_user_account_infos(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        self.assert_user_account(serialized_user, user_2)
        assert serialized_user["email"] == user_2.email
        assert serialized_user["email_to_confirm"] == user_2.email_to_confirm

    def test_it_returns_user_profile_infos(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        self.assert_user_profile(serialized_user, user_1_admin)
        assert serialized_user["blocked"] is False

    def test_it_does_not_return_user_preferences(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        assert "imperial_units" not in serialized_user
        assert "language" not in serialized_user
        assert "timezone" not in serialized_user
        assert "weekm" not in serialized_user
        assert "start_elevation_at_zero" not in serialized_user
        assert "use_raw_gpx_speed" not in serialized_user
        assert "use_dark_mode" not in serialized_user
        assert "workouts_visibility" not in serialized_user
        assert "analysis_visibility" not in serialized_user
        assert "map_visibility" not in serialized_user
        assert "hr_visibility" not in serialized_user
        assert "manually_approves_followers" not in serialized_user
        assert "hide_profile_in_users_directory" not in serialized_user
        assert "notification_preferences" not in serialized_user
        assert "segments_creation_event" not in serialized_user

    def test_it_returns_workouts_infos(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        self.assert_workouts_keys_are_present(serialized_user)

    def test_it_does_not_return_accepted_privacy_policy_date(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        assert "accepted_privacy_policy" not in serialized_user

    def test_it_does_not_return_confirmation_token(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        assert "confirmation_token" not in serialized_user

    def test_it_returns_reports_info(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        self.create_user_report(user_2, user_3)
        self.create_user_report(user_1_admin, user_2)
        self.create_report_user_action(user_1_admin, user_2)

        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=False
        )

        assert serialized_user["created_reports_count"] == 1
        assert serialized_user["reported_count"] == 2
        assert serialized_user["sanctions_count"] == 1


class TestUserSerializeAsModerator(UserModelAssertMixin, ReportMixin):
    def test_it_returns_user_account_infos(
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_moderator, light=False
        )

        self.assert_user_account(serialized_user, user_2)
        assert serialized_user["email"] == user_2.email
        assert "email_to_confirm" not in serialized_user

    def test_it_returns_user_profile_infos(
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_moderator, light=False
        )

        self.assert_user_profile(serialized_user, user_1_moderator)
        assert serialized_user["blocked"] is False

    def test_it_does_not_return_user_preferences(
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_moderator, light=False
        )

        assert "imperial_units" not in serialized_user
        assert "language" not in serialized_user
        assert "timezone" not in serialized_user
        assert "weekm" not in serialized_user
        assert "start_elevation_at_zero" not in serialized_user
        assert "use_raw_gpx_speed" not in serialized_user
        assert "use_dark_mode" not in serialized_user
        assert "workouts_visibility" not in serialized_user
        assert "analysis_visibility" not in serialized_user
        assert "map_visibility" not in serialized_user
        assert "hr_visibility" not in serialized_user
        assert "manually_approves_followers" not in serialized_user
        assert "hide_profile_in_users_directory" not in serialized_user
        assert "notification_preferences" not in serialized_user
        assert "segments_creation_event" not in serialized_user

    def test_it_returns_workouts_infos(
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_moderator, light=False
        )

        self.assert_workouts_keys_are_present(serialized_user)

    def test_it_does_not_return_accepted_privacy_policy_date(
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_moderator, light=False
        )

        assert "accepted_privacy_policy" not in serialized_user

    def test_it_does_not_return_confirmation_token(
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_moderator, light=False
        )

        assert "confirmation_token" not in serialized_user

    def test_it_returns_reports_info(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        self.create_user_report(user_2, user_3)
        self.create_user_report(user_1_moderator, user_2)
        self.create_report_user_action(user_1_moderator, user_2)

        serialized_user = user_2.serialize(
            current_user=user_1_moderator, light=False
        )

        assert serialized_user["created_reports_count"] == 1
        assert serialized_user["reported_count"] == 2
        assert serialized_user["sanctions_count"] == 1


class TestUserSerializeAsUser(UserModelAssertMixin):
    def test_it_returns_user_account_infos(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert serialized_user["role"] == UserRole(user_2.role).name.lower()
        assert serialized_user["username"] == user_2.username
        assert "email" not in serialized_user
        assert "email_to_confirm" not in serialized_user
        assert "is_active" not in serialized_user

    def test_it_returns_user_profile_infos(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        self.assert_user_profile(serialized_user, user_1)
        assert serialized_user["blocked"] is False

    def test_it_does_not_return_user_preferences(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert "imperial_units" not in serialized_user
        assert "language" not in serialized_user
        assert "timezone" not in serialized_user
        assert "weekm" not in serialized_user
        assert "workouts_visibility" not in serialized_user
        assert "analysis_visibility" not in serialized_user
        assert "map_visibility" not in serialized_user
        assert "hr_visibility" not in serialized_user
        assert "manually_approves_followers" not in serialized_user
        assert "hide_profile_in_users_directory" not in serialized_user
        assert "notification_preferences" not in serialized_user
        assert "segments_creation_event" not in serialized_user

    def test_it_returns_workouts_infos(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        self.assert_workouts_keys_are_present(serialized_user)

    def test_it_does_not_return_confirmation_token(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert "confirmation_token" not in serialized_user

    def test_it_does_not_return_reports_info(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert "created_reports_count" not in serialized_user
        assert "reported_count" not in serialized_user
        assert "sanctions_count" not in serialized_user


class TestUserSerializeAsUnauthenticatedUser(UserModelAssertMixin):
    def test_it_returns_limited_user_infos_by_default(
        self, app: Flask, user_1: User
    ) -> None:
        serialized_user = user_1.serialize(light=False)

        assert serialized_user == {
            "created_at": user_1.created_at,
            "followers": user_1.followers.count(),
            "following": user_1.following.count(),
            "nb_workouts": user_1.workouts_count,
            "picture": user_1.picture is not None,
            "role": UserRole(user_1.role).name.lower(),
            "suspended_at": user_1.suspended_at,
            "username": user_1.username,
        }


class TestInactiveUserSerialize(UserModelAssertMixin):
    def test_it_returns_is_active_to_false_for_inactive_user(
        self,
        app: Flask,
        inactive_user: User,
    ) -> None:
        serialized_user = inactive_user.serialize(
            current_user=inactive_user, light=False
        )

        assert serialized_user["is_active"] is False


@pytest.mark.disable_autouse_update_records_patch
class TestUserRecords(UserModelAssertMixin):
    def test_it_returns_empty_list_when_no_workouts(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["records"] == []

    def test_it_returns_user_records(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)
        assert len(serialized_user["records"]) == 4
        records = sorted(
            serialized_user["records"], key=lambda r: r["record_type"]
        )
        assert records[0]["record_type"] == "AS"
        assert records[0]["sport_id"] == sport_1_cycling.id
        assert records[0]["user"] == user_1.username
        assert records[0]["value"] > 0
        assert records[0]["workout_id"] == workout_cycling_user_1.short_id
        assert records[0]["workout_date"]

    def test_it_returns_totals_when_workout_has_pauses(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.pauses = timedelta(minutes=5)
        workout_cycling_user_1.duration = (
            workout_cycling_user_1.pauses + workout_cycling_user_1.moving  # type: ignore
        )
        serialized_user = user_1.serialize(current_user=user_1, light=False)
        assert serialized_user["total_ascent"] == 0
        assert serialized_user["total_distance"] == 10
        assert serialized_user["total_duration"] == str(
            workout_cycling_user_1.moving
        )

    def test_it_returns_totals_when_user_has_workout_without_ascent(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)
        assert serialized_user["total_ascent"] == 0
        assert serialized_user["total_distance"] == 10
        assert serialized_user["total_duration"] == "1:00:00"

    def test_it_returns_totals_when_user_has_workout_with_ascent(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.ascent = 100
        serialized_user = user_1.serialize(current_user=user_1, light=False)
        assert serialized_user["total_ascent"] == 100
        assert serialized_user["total_distance"] == 10
        assert serialized_user["total_duration"] == "1:00:00"

    def test_it_returns_totals_when_user_has_multiple_workouts(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.ascent = 100
        serialized_user = user_1.serialize(current_user=user_1, light=False)
        assert serialized_user["total_ascent"] == 100
        assert serialized_user["total_distance"] == 22
        assert serialized_user["total_duration"] == "2:40:00"


class TestUserWorkouts(UserModelAssertMixin):
    def test_it_returns_infos_when_no_workouts(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["nb_sports"] == 0
        assert serialized_user["nb_workouts"] == 0
        assert serialized_user["sports_list"] == []
        assert serialized_user["total_distance"] == 0
        assert serialized_user["total_duration"] == "0:00:00"

    def test_it_returns_infos_when_only_one_workout_exists(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["nb_sports"] == 1
        assert serialized_user["nb_workouts"] == 1
        assert serialized_user["sports_list"] == [sport_1_cycling.id]
        assert (
            serialized_user["total_distance"]
            == workout_cycling_user_1.distance
        )
        assert serialized_user["total_duration"] == str(
            workout_cycling_user_1.duration
        )

    def test_it_returns_infos_when_several_sports(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        serialized_user = user_1.serialize(current_user=user_1, light=False)

        assert serialized_user["nb_sports"] == 2
        assert serialized_user["nb_workouts"] == 2
        assert serialized_user["sports_list"] == [
            sport_1_cycling.id,
            sport_2_running.id,
        ]
        assert serialized_user["total_distance"] == (
            workout_cycling_user_1.distance + workout_running_user_1.distance  # type: ignore
        )
        assert serialized_user["total_duration"] == str(
            workout_cycling_user_1.duration + workout_running_user_1.duration
        )


class TestUserModelToken(RandomMixin):
    def test_encode_auth_token(self, app: Flask, user_1: User) -> None:
        auth_token = user_1.encode_auth_token(user_1.id)
        assert isinstance(auth_token, str)

    def test_encode_password_token(self, app: Flask, user_1: User) -> None:
        password_token = user_1.encode_password_reset_token(user_1.id)
        assert isinstance(password_token, str)

    def test_decode_auth_token(self, app: Flask, user_1: User) -> None:
        auth_token = user_1.encode_auth_token(user_1.id)
        assert isinstance(auth_token, str)
        assert User.decode_auth_token(auth_token) == user_1.id

    def test_it_returns_error_when_token_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        assert (
            User.decode_auth_token(self.random_string())
            == "invalid token, please log in again"
        )

    def test_it_returns_error_when_token_is_expired(
        self, app: Flask, user_1: User
    ) -> None:
        auth_token = user_1.encode_auth_token(user_1.id)
        now = datetime.now(timezone.utc)
        with travel(now + timedelta(seconds=61), tick=False):
            assert (
                User.decode_auth_token(auth_token)
                == "signature expired, please log in again"
            )

    def test_it_returns_error_when_token_is_blacklisted(
        self, app: Flask, user_1: User
    ) -> None:
        auth_token = user_1.encode_auth_token(user_1.id)
        db.session.add(BlacklistedToken(token=auth_token))
        db.session.commit()

        assert (
            User.decode_auth_token(auth_token)
            == "blacklisted token, please log in again"
        )


class TestUserSportModel:
    def test_user_sport_preferences_model(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        serialized_user_sport = user_1_sport_1_preference.serialize()

        assert serialized_user_sport["user_id"] == user_1.id
        assert serialized_user_sport["sport_id"] == sport_1_cycling.id
        assert serialized_user_sport["color"] is None
        assert serialized_user_sport["is_active"]
        assert serialized_user_sport["stopped_speed_threshold"] == 1
        assert serialized_user_sport["default_equipments"] == []

    def test_user_sport_preferences_model_with_default_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    },
                    {
                        "equipment_id": equipment_shoes_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    },
                ]
            )
        )

        serialized_user_sport = user_1_sport_1_preference.serialize()

        assert serialized_user_sport["user_id"] == user_1.id
        assert serialized_user_sport["sport_id"] == sport_1_cycling.id
        assert serialized_user_sport["color"] is None
        assert serialized_user_sport["is_active"]
        assert serialized_user_sport["stopped_speed_threshold"] == 1
        assert len(serialized_user_sport["default_equipments"]) == 2
        assert (
            equipment_bike_user_1.serialize(current_user=user_1)
            in serialized_user_sport["default_equipments"]
        )
        assert (
            equipment_shoes_user_1.serialize(current_user=user_1)
            in serialized_user_sport["default_equipments"]
        )


class TestUserTaskModel:
    relative_path: str = ""
    absolute_path: str = ""

    def generate_file(self) -> None:
        self.relative_path = "temporary_file.txt"
        self.absolute_path = get_absolute_file_path(self.relative_path)
        export_file = Path(self.absolute_path)
        export_file.parent.mkdir(exist_ok=True, parents=True)
        export_file.write_text("some text")

    def test_it_instantiates_task_for_user_data_export(
        self, app: Flask, user_1: User
    ) -> None:
        created_at = datetime.now(timezone.utc)
        data_export = UserTask(
            user_id=user_1.id,
            created_at=created_at,
            task_type="user_data_export",
        )
        db.session.add(data_export)
        db.session.commit()

        assert data_export.aborted is False
        assert data_export.created_at == created_at
        assert data_export.data == {}
        assert data_export.errors == {}
        assert data_export.file_path is None
        assert data_export.file_size is None
        assert data_export.message_id is None
        assert data_export.progress == 0
        assert data_export.task_type == "user_data_export"
        assert data_export.updated_at is None
        assert data_export.user_id == user_1.id
        assert data_export.uuid is not None

    def test_it_instantiates_task_for_workouts_archive_upload(
        self, app: Flask, user_1: User
    ) -> None:
        created_at = datetime.now(timezone.utc)
        data_export = UserTask(
            user_id=user_1.id,
            created_at=created_at,
            task_type="workouts_archive_upload",
            file_path="some path",
            data={"some": "data"},
        )
        db.session.add(data_export)
        db.session.commit()

        assert data_export.aborted is False
        assert data_export.created_at == created_at
        assert data_export.data == {"some": "data"}
        assert data_export.errors == {
            "archive": None,
            "files": {},
        }
        assert data_export.file_path == "some path"
        assert data_export.file_size is None
        assert data_export.message_id is None
        assert data_export.progress == 0
        assert data_export.task_type == "workouts_archive_upload"
        assert data_export.updated_at is None
        assert data_export.user_id == user_1.id
        assert data_export.uuid is not None

    def test_it_instantiates_task_when_created_at_is_not_provided(
        self, app: Flask, user_1: User
    ) -> None:
        now = datetime.now(timezone.utc)
        with travel(now, tick=False):
            data_export = UserTask(
                user_id=user_1.id,
                task_type="workouts_archive_upload",
            )
        db.session.add(data_export)
        db.session.commit()

        assert data_export.created_at == now

    def test_it_deletes_file_on_data_export_task_deletion(
        self, app: Flask, user_1: User
    ) -> None:
        self.generate_file()
        data_export = UserTask(
            user_id=user_1.id,
            task_type="user_data_export",
            file_path=self.relative_path,
        )
        db.session.add(data_export)
        db.session.commit()

        db.session.delete(data_export)
        db.session.commit()

        assert os.path.isfile(self.absolute_path) is False

    def test_it_deletes_file_on_workouts_upload_task_deletion(
        self, app: Flask, user_1: User
    ) -> None:
        self.generate_file()
        workouts_upload = UserTask(
            user_id=user_1.id,
            task_type="workouts_archive_upload",
            file_path=self.absolute_path,
        )
        db.session.add(workouts_upload)
        db.session.commit()

        db.session.delete(workouts_upload)
        db.session.commit()

        assert os.path.isfile(self.absolute_path) is False

    def test_it_deletes_notification_on_user_task_deletion(
        self, app: Flask, user_1: User
    ) -> None:
        workouts_upload = UserTask(
            user_id=user_1.id, task_type="workouts_archive_upload"
        )
        db.session.add(workouts_upload)
        db.session.flush()
        notification = Notification(
            from_user_id=workouts_upload.user_id,
            to_user_id=workouts_upload.user_id,
            created_at=datetime.now(tz=timezone.utc),
            event_object_id=workouts_upload.id,
            event_type=workouts_upload.task_type,
        )
        db.session.add(notification)
        db.session.commit()

        db.session.delete(workouts_upload)
        db.session.commit()

        assert Notification.query.count() == 0


class TestUserTaskSerializerForUserDataExport(RandomMixin, UserTaskMixin):
    def test_it_returns_queued_export(self, app: Flask, user_1: User) -> None:
        data_export = self.create_user_data_export_task(user=user_1)

        serialized_data_export = data_export.serialize(current_user=user_1)

        assert serialized_data_export == {
            "id": data_export.short_id,
            "created_at": data_export.created_at,
            "file_name": None,
            "file_size": None,
            "status": "queued",
            "type": "user_data_export",
        }

    def test_it_returns_ongoing_export(self, app: Flask, user_1: User) -> None:
        data_export = self.create_user_data_export_task(
            user=user_1, progress=10
        )

        serialized_data_export = data_export.serialize(current_user=user_1)

        assert serialized_data_export == {
            "id": data_export.short_id,
            "created_at": data_export.created_at,
            "file_name": None,
            "file_size": None,
            "status": "in_progress",
            "type": "user_data_export",
        }

    def test_it_returns_successful_export(
        self, app: Flask, user_1: User
    ) -> None:
        file_name = self.random_string()
        data_export = self.create_user_data_export_task(
            user=user_1,
            progress=100,
            file_path=f"exports/{user_1.id}/{file_name}",
            file_size=self.random_int(),
        )

        serialized_data_export = data_export.serialize(current_user=user_1)

        assert serialized_data_export == {
            "id": data_export.short_id,
            "created_at": data_export.created_at,
            "file_name": file_name,
            "file_size": data_export.file_size,
            "status": "successful",
            "type": "user_data_export",
        }

    def test_it_returns_errored_export(self, app: Flask, user_1: User) -> None:
        data_export = self.create_user_data_export_task(
            user=user_1, progress=100, errored=True
        )

        serialized_data_export = data_export.serialize(current_user=user_1)

        assert serialized_data_export == {
            "id": data_export.short_id,
            "created_at": data_export.created_at,
            "file_name": None,
            "file_size": None,
            "status": "errored",
            "type": "user_data_export",
        }

    def test_it_returns_export_for_admin(
        self, app: Flask, user_1: User, user_2_admin: User
    ) -> None:
        data_export = self.create_user_data_export_task(
            user=user_1, message_id=self.random_short_id()
        )

        serialized_data_export = data_export.serialize(
            current_user=user_2_admin, for_admin=True
        )

        assert serialized_data_export == {
            "id": data_export.short_id,
            "created_at": data_export.created_at,
            "file_size": None,
            "message_id": data_export.message_id,
            "status": "queued",
            "type": "user_data_export",
        }

    def test_it_returns_export_for_admin_with_task_user(
        self, app: Flask, user_1: User, user_2_admin: User
    ) -> None:
        data_export = self.create_user_data_export_task(
            user=user_1, message_id=self.random_short_id()
        )

        serialized_data_export = data_export.serialize(
            current_user=user_2_admin, for_admin=True, task_user=user_1
        )

        assert serialized_data_export == {
            "id": data_export.short_id,
            "created_at": data_export.created_at,
            "file_size": None,
            "message_id": data_export.message_id,
            "status": "queued",
            "type": "user_data_export",
            "user": user_1.serialize(current_user=user_2_admin, light=True),
        }

    def test_it_raises_error_when_user_has_no_admin_right(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        data_export = self.create_user_data_export_task(
            user=user_1, message_id=self.random_short_id()
        )

        with pytest.raises(
            UserTaskForbiddenException, match="you do not have permissions"
        ):
            data_export.serialize(current_user=user_2)

    def test_it_raises_error_when_user_task_is_invalid(
        self, app: Flask, user_1: User, user_2_admin: User, user_3: User
    ) -> None:
        data_export = self.create_user_data_export_task(
            user=user_1, message_id=self.random_short_id()
        )

        with pytest.raises(UserTaskException, match="invalid tasks user"):
            data_export.serialize(current_user=user_2_admin, task_user=user_3)


class TestUserTaskSerializerForWorkoutArchiveUpload(
    RandomMixin, UserTaskMixin
):
    def test_it_returns_queued_import(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(
            user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx", "file_3.gpx"],
            file_path="some/path",
            file_size=1000,
        )

        serialized_workouts_upload = workouts_upload.serialize(
            current_user=user_1
        )

        assert serialized_workouts_upload == {
            "id": workouts_upload.short_id,
            "created_at": workouts_upload.created_at,
            "errored_files": {
                "archive": None,
                "files": {},
            },
            "file_size": workouts_upload.file_size,
            "files_count": 3,
            "new_workouts_count": 0,
            "original_file_name": None,
            "progress": 0,
            "status": "queued",
            "sport_id": sport_1_cycling.id,
            "type": "workouts_archive_upload",
            "updated_at": None,
        }

    def test_it_returns_ongoing_import(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(
            user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx", "file_3.gpx"],
            file_path="some/path",
            file_size=1000,
            original_file_name="workouts.zip",
            progress=50,
            updated_at=datetime.now(timezone.utc),
        )

        serialized_workouts_upload = workouts_upload.serialize(
            current_user=user_1
        )

        assert serialized_workouts_upload == {
            "id": workouts_upload.short_id,
            "created_at": workouts_upload.created_at,
            "errored_files": {
                "archive": None,
                "files": {},
            },
            "file_size": workouts_upload.file_size,
            "files_count": 3,
            "new_workouts_count": 0,
            "original_file_name": "workouts.zip",
            "progress": 50,
            "status": "in_progress",
            "sport_id": sport_1_cycling.id,
            "type": "workouts_archive_upload",
            "updated_at": workouts_upload.updated_at,
        }

    def test_it_returns_successful_import(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(
            user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx", "file_3.gpx"],
            new_workouts_count=3,
            file_path="some/path",
            file_size=1000,
            original_file_name="workouts.zip",
            progress=100,
            updated_at=datetime.now(timezone.utc),
        )

        serialized_workouts_upload = workouts_upload.serialize(
            current_user=user_1
        )

        assert serialized_workouts_upload == {
            "id": workouts_upload.short_id,
            "created_at": workouts_upload.created_at,
            "errored_files": {
                "archive": None,
                "files": {},
            },
            "file_size": workouts_upload.file_size,
            "files_count": 3,
            "new_workouts_count": 3,
            "original_file_name": "workouts.zip",
            "progress": 100,
            "status": "successful",
            "sport_id": sport_1_cycling.id,
            "type": "workouts_archive_upload",
            "updated_at": workouts_upload.updated_at,
        }

    def test_it_returns_errored_upload_when_some_file_is_errored(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(
            user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx", "file_3.gpx"],
            new_workouts_count=2,
            file_path="some/path",
            file_size=1000,
            original_file_name="workouts.zip",
            progress=100,
            errored=True,
            updated_at=datetime.now(timezone.utc),
        )
        workouts_upload.errors = {
            **workouts_upload.errors,
            "files": {"file_2.gpx": "some error"},
        }
        db.session.commit()
        serialized_workouts_upload = workouts_upload.serialize(
            current_user=user_1
        )

        assert serialized_workouts_upload == {
            "id": workouts_upload.short_id,
            "created_at": workouts_upload.created_at,
            "errored_files": {
                "archive": None,
                "files": {"file_2.gpx": "some error"},
            },
            "file_size": workouts_upload.file_size,
            "files_count": 3,
            "new_workouts_count": 2,
            "original_file_name": "workouts.zip",
            "progress": 100,
            "sport_id": sport_1_cycling.id,
            "status": "errored",
            "type": "workouts_archive_upload",
            "updated_at": workouts_upload.updated_at,
        }

    def test_it_returns_errored_upload_when_all_files_are_errored(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(
            user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx", "file_3.gpx"],
            file_path="some/path",
            file_size=1000,
            original_file_name="workouts.zip",
            progress=100,
            errored=True,
            updated_at=datetime.now(timezone.utc),
        )
        errors = {f"file_{n}.gpx": "some error" for n in range(1, 4)}
        workouts_upload.errors = {**workouts_upload.errors, "files": errors}
        db.session.commit()

        serialized_workouts_upload = workouts_upload.serialize(
            current_user=user_1
        )

        assert serialized_workouts_upload == {
            "id": workouts_upload.short_id,
            "created_at": workouts_upload.created_at,
            "errored_files": {
                "archive": None,
                "files": errors,
            },
            "file_size": workouts_upload.file_size,
            "files_count": 3,
            "new_workouts_count": 0,
            "original_file_name": "workouts.zip",
            "progress": 100,
            "sport_id": sport_1_cycling.id,
            "status": "errored",
            "type": "workouts_archive_upload",
            "updated_at": workouts_upload.updated_at,
        }

    def test_it_returns_errored_upload_when_archive_is_errored(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(
            user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx", "file_3.gpx"],
            file_path="some/path",
            file_size=1000,
            original_file_name="workouts.zip",
            progress=0,
            errored=True,
            updated_at=datetime.now(timezone.utc),
        )
        workouts_upload.errors = {
            **workouts_upload.errors,
            "archive": "some error",
        }
        db.session.commit()

        serialized_workouts_upload = workouts_upload.serialize(
            current_user=user_1
        )

        assert serialized_workouts_upload == {
            "id": workouts_upload.short_id,
            "created_at": workouts_upload.created_at,
            "errored_files": {
                "archive": "some error",
                "files": {},
            },
            "file_size": workouts_upload.file_size,
            "files_count": 3,
            "new_workouts_count": 0,
            "original_file_name": "workouts.zip",
            "progress": 0,
            "sport_id": sport_1_cycling.id,
            "status": "errored",
            "type": "workouts_archive_upload",
            "updated_at": workouts_upload.updated_at,
        }

    def test_it_returns_aborted_upload(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(
            user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx", "file_3.gpx"],
            file_path="some/path",
            file_size=1000,
            original_file_name="workouts.zip",
            progress=10,
            aborted=True,
            updated_at=datetime.now(timezone.utc),
        )

        serialized_workouts_upload = workouts_upload.serialize(
            current_user=user_1
        )

        assert serialized_workouts_upload == {
            "id": workouts_upload.short_id,
            "created_at": workouts_upload.created_at,
            "errored_files": {
                "archive": None,
                "files": {},
            },
            "file_size": workouts_upload.file_size,
            "files_count": 3,
            "new_workouts_count": 0,
            "original_file_name": "workouts.zip",
            "progress": 10,
            "sport_id": sport_1_cycling.id,
            "status": "aborted",
            "type": "workouts_archive_upload",
            "updated_at": workouts_upload.updated_at,
        }

    def test_it_returns_export_for_admin(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2_admin: User,
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(
            user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx", "file_3.gpx"],
            file_path="some/path",
            file_size=1000,
            message_id=self.random_short_id(),
        )

        serialized_workouts_upload = workouts_upload.serialize(
            current_user=user_2_admin, for_admin=True
        )

        assert serialized_workouts_upload == {
            "id": workouts_upload.short_id,
            "created_at": workouts_upload.created_at,
            "files_count": 3,
            "file_size": workouts_upload.file_size,
            "message_id": workouts_upload.message_id,
            "status": "queued",
            "type": "workouts_archive_upload",
        }

    def test_it_returns_export_for_admin_with_task_user(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2_admin: User,
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(
            user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx", "file_3.gpx"],
            file_path="some/path",
            file_size=1000,
            message_id=self.random_short_id(),
        )

        serialized_workouts_upload = workouts_upload.serialize(
            current_user=user_2_admin, for_admin=True, task_user=user_1
        )

        assert serialized_workouts_upload == {
            "id": workouts_upload.short_id,
            "created_at": workouts_upload.created_at,
            "files_count": 3,
            "file_size": workouts_upload.file_size,
            "message_id": workouts_upload.message_id,
            "status": "queued",
            "type": "workouts_archive_upload",
            "user": user_1.serialize(current_user=user_2_admin, light=True),
        }

    def test_it_raises_error_when_user_has_no_admin_right(
        self, app: Flask, sport_1_cycling: Sport, user_1: User, user_2: User
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(user=user_1)

        with pytest.raises(
            UserTaskForbiddenException, match="you do not have permissions"
        ):
            workouts_upload.serialize(current_user=user_2)

    def test_it_raises_error_when_user_task_is_invalid(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2_admin: User,
        user_3: User,
    ) -> None:
        workouts_upload = self.create_workouts_upload_task(user=user_1)

        with pytest.raises(UserTaskException, match="invalid tasks user"):
            workouts_upload.serialize(
                current_user=user_2_admin, task_user=user_3
            )


class TestFollowRequestModel:
    def test_follow_request_model(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        assert "<FollowRequest from user '1' to user '2'>" == str(
            follow_request_from_user_1_to_user_2
        )

        serialized_follow_request = (
            follow_request_from_user_1_to_user_2.serialize()
        )
        assert serialized_follow_request["from_user"] == user_1.serialize()
        assert serialized_follow_request["to_user"] == user_2.serialize()

    def test_it_deletes_follow_request_on_followed_user_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        followed_user_id = user_2.id

        db.session.delete(user_2)

        assert (
            FollowRequest.query.filter_by(
                follower_user_id=user_1.id,
                followed_user_id=followed_user_id,
            ).first()
            is None
        )

    def test_it_deletes_follow_request_on_follower_user_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follower_user_id = user_1.id

        db.session.delete(user_1)

        assert (
            FollowRequest.query.filter_by(
                follower_user_id=follower_user_id,
                followed_user_id=user_2.id,
            ).first()
            is None
        )


class TestUserFollowingModel:
    def test_user_2_sends_follow_requests_to_user_1(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        follow_request = user_2.send_follow_request_to(user_1)

        assert follow_request in user_2.sent_follow_requests.all()

    def test_user_1_receives_follow_requests_from_user_2(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        follow_request = user_2.send_follow_request_to(user_1)

        assert follow_request in user_1.received_follow_requests.all()

    def test_user_has_pending_follow_request(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        assert (
            follow_request_from_user_2_to_user_1
            in user_1.pending_follow_requests
        )

    def test_user_has_no_pending_follow_request(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.updated_at = datetime.now(
            timezone.utc
        )
        assert user_1.pending_follow_requests == []

    def test_user_approves_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        follow_request = user_1.approves_follow_request_from(user_2)

        assert follow_request.is_approved
        assert user_1.pending_follow_requests == [
            follow_request_from_user_3_to_user_1
        ]

    def test_user_refuses_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request = user_1.rejects_follow_request_from(user_2)

        assert not follow_request.is_approved
        assert user_1.pending_follow_requests == []

    def test_it_raises_error_if_follow_request_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        with pytest.raises(NotExistingFollowRequestError):
            user_1.approves_follow_request_from(user_2)

    def test_it_raises_error_if_user_approves_follow_request_already_processed(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.updated_at = datetime.now(
            timezone.utc
        )

        with pytest.raises(FollowRequestAlreadyProcessedError):
            user_1.approves_follow_request_from(user_2)

    def test_follow_request_is_automatically_accepted_if_manually_approved_if_false(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.manually_approves_followers = False
        follow_request = user_2.send_follow_request_to(user_1)

        assert follow_request in user_2.sent_follow_requests.all()
        assert follow_request.is_approved is True
        assert follow_request.updated_at is not None


class TestUserUnfollowModel:
    def test_it_raises_error_if_follow_request_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        with pytest.raises(NotExistingFollowRequestError):
            user_1.unfollows(user_2)

    def test_user_1_unfollows_user_2(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = True
        follow_request_from_user_1_to_user_2.updated_at = datetime.now(
            timezone.utc
        )

        user_1.unfollows(user_2)

        assert user_1.following.count() == 0
        assert user_2.followers.count() == 0

    def test_it_removes_pending_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_1.unfollows(user_2)

        assert user_1.sent_follow_requests.all() == []


class TestUserFollowers:
    def test_it_returns_empty_list_if_no_followers(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        assert user_1.followers.all() == []

    def test_it_returns_empty_list_if_follow_request_is_not_approved(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        assert user_1.followers.all() == []

    def test_it_returns_follower_if_follow_request_is_approved(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.is_approved = True
        follow_request_from_user_2_to_user_1.updated_at = datetime.now(
            timezone.utc
        )

        assert user_1.followers.all() == [user_2]

    def test_it_does_not_return_suspended_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.is_approved = True
        follow_request_from_user_2_to_user_1.updated_at = datetime.now(
            timezone.utc
        )
        user_2.suspended_at = datetime.now(timezone.utc)

        assert user_1.followers.all() == []


class TestUserFollowing:
    def test_it_returns_empty_list_if_no_following(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        assert user_1.following.all() == []

    def test_it_returns_empty_list_if_follow_request_is_not_approved(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        assert user_1.following.all() == []

    def test_it_returns_following_if_follow_request_is_approved(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = True
        follow_request_from_user_1_to_user_2.updated_at = datetime.now(
            timezone.utc
        )

        assert user_1.following.all() == [user_2]

    def test_it_does_not_return_suspended_following_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = True
        follow_request_from_user_1_to_user_2.updated_at = datetime.now(
            timezone.utc
        )
        user_2.suspended_at = datetime.now(timezone.utc)

        assert user_1.following.all() == []


class TestUserFollowRequestStatus(UserModelAssertMixin):
    def test_it_returns_user_1_and_user_2_dont_not_follow_each_other(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert serialized_user["followers"] == 0
        assert serialized_user["following"] == 0
        assert serialized_user["follows"] == "false"
        assert serialized_user["is_followed_by"] == "false"

    def test_status_when_follow_request_is_pending(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.send_follow_request_to(user_2)

        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert serialized_user["followers"] == 0
        assert serialized_user["following"] == 0
        assert serialized_user["follows"] == "false"
        assert serialized_user["is_followed_by"] == "pending"

    def test_status_when_user_rejects_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.send_follow_request_to(user_2)
        user_2.rejects_follow_request_from(user_1)

        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert serialized_user["followers"] == 0
        assert serialized_user["following"] == 0
        assert serialized_user["follows"] == "false"
        assert serialized_user["is_followed_by"] == "pending"

    def test_followed_user_status_when_follow_request_is_approved(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.send_follow_request_to(user_2)
        user_2.approves_follow_request_from(user_1)

        serialized_user = user_2.serialize(current_user=user_1, light=False)

        assert serialized_user["followers"] == 1
        assert serialized_user["following"] == 0
        assert serialized_user["follows"] == "false"
        assert serialized_user["is_followed_by"] == "true"

    def test_follower_status_when_follow_request_is_approved(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        user_1.send_follow_request_to(user_2)
        user_2.approves_follow_request_from(user_1)

        serialized_user = user_1.serialize(current_user=user_2, light=False)

        assert serialized_user["followers"] == 0
        assert serialized_user["following"] == 1
        assert serialized_user["follows"] == "true"
        assert serialized_user["is_followed_by"] == "false"


class TestUserLinkifyMention:
    def test_it_returns_linkified_mention_with_username(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        assert user_1.linkify_mention() == (
            f'<a href="{user_1.get_user_url()}" target="_blank" '
            f'rel="noopener noreferrer">@{user_1.username}</a>'
        )


class TestBlocksUser:
    def test_it_blocks_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.blocks_user(user_2)

        assert (
            BlockedUser.query.filter_by(
                user_id=user_2.id,
                by_user_id=user_1.id,
            ).first()
            is not None
        )
        serialized_user = user_2.serialize(current_user=user_1, light=False)
        assert serialized_user["blocked"] is True

    def test_it_inits_created_at(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        now = datetime.now(timezone.utc)
        with travel(now, tick=False):
            user_1.blocks_user(user_2)

        blocked_user = BlockedUser.query.filter_by(
            user_id=user_2.id,
            by_user_id=user_1.id,
        ).one()
        assert blocked_user.created_at == now

    def test_it_does_not_raises_error_when_user_is_already_blocked(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.blocks_user(user_2)

        user_1.blocks_user(user_2)

        assert (
            BlockedUser.query.filter_by(
                user_id=user_2.id,
                by_user_id=user_1.id,
            ).first()
            is not None
        )

    def test_user_can_not_block_itself(self, app: Flask, user_1: User) -> None:
        with pytest.raises(BlockUserException):
            user_1.blocks_user(user_1)

    def test_it_blocks_a_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)

        user_1.blocks_user(user_2)

        assert (
            BlockedUser.query.filter_by(
                user_id=user_2.id,
                by_user_id=user_1.id,
            ).first()
            is not None
        )
        serialized_user = user_2.serialize(current_user=user_1, light=False)
        assert serialized_user["blocked"] is True

    def test_it_deletes_follow_request_when_a_follow_request_exists(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.blocks_user(user_2)

        assert (
            FollowRequest.query.filter_by(
                follower_user_id=user_2.id,
                followed_user_id=user_1.id,
            ).first()
            is None
        )

    def test_it_deletes_follow_request_notification_when_a_follow_request_exists(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.blocks_user(user_2)

        assert (
            Notification.query.filter_by(
                from_user_id=user_2.id,
                to_user_id=user_1.id,
            ).first()
            is None
        )

    def test_it_deletes_follow_request_when_user_blocks_a_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)

        user_1.blocks_user(user_2)

        assert (
            FollowRequest.query.filter_by(
                follower_user_id=user_2.id,
                followed_user_id=user_1.id,
            ).first()
            is None
        )

    def test_it_deletes_follow_request_notification_when_user_blocks_a_follower(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)

        user_1.blocks_user(user_2)

        assert (
            Notification.query.filter_by(
                from_user_id=user_2.id,
                to_user_id=user_1.id,
            ).first()
            is None
        )


class TestUnBlocksUser:
    def test_it_unblocks_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.blocks_user(user_2)

        user_1.unblocks_user(user_2)

        assert (
            BlockedUser.query.filter_by(
                user_id=user_2.id,
                by_user_id=user_1.id,
            ).first()
            is None
        )
        serialized_user = user_2.serialize(current_user=user_1, light=False)
        assert serialized_user["blocked"] is False

    def test_it_does_not_raises_error_when_user_is_not_blocked(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.unblocks_user(user_2)

        assert (
            BlockedUser.query.filter_by(
                user_id=user_2.id,
                by_user_id=user_1.id,
            ).first()
            is None
        )


class TestIsBlockedBy:
    def test_it_returns_false_when_user_is_not_blocked(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        assert user_1.is_blocked_by(user_2) is False

    def test_it_returns_true_when_user_is_blocked(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_2.blocks_user(user_1)

        user_1.is_blocked_by(user_2)

        assert user_1.is_blocked_by(user_2) is True


class TestBlockedUsers:
    def test_it_returns_empty_list_when_no_user_blocked(
        self, app: Flask, user_1: User
    ) -> None:
        assert user_1.blocked_users.all() == []

    def test_it_returns_blocked_users(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
    ) -> None:
        user_1.blocks_user(user_2)
        user_1.blocks_user(user_4)

        assert set(user_1.get_blocked_user_ids()) == {user_2.id, user_4.id}


class TestBlockedByUsers:
    def test_it_returns_empty_list_when_not_blocked(
        self, app: Flask, user_1: User
    ) -> None:
        assert user_1.blocked_by_users.all() == []

    def test_it_returns_blocked_by_users_ids(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
    ) -> None:
        user_2.blocks_user(user_1)
        user_3.blocks_user(user_1)

        assert set(user_1.get_blocked_by_user_ids()) == {user_2.id, user_3.id}


class TestUsersWithSuspensions(ReportMixin):
    def test_suspension_action_is_none_when_no_suspension_for_given_user(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        action_type = "user_suspension"
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type=action_type,
            report_id=self.create_report_user_action(
                user_1_admin, user_2, action_type
            ).id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()

        assert user_3.suspension_action is None

    def test_suspension_action_is_last_suspension_action_when_user_is_suspended(  # noqa
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        report_id = self.create_user_report(user_1_admin, user_2).id
        for n in range(2):
            action_type = (
                "user_suspension" if n % 2 == 0 else "user_unsuspension"
            )
            report_action = ReportAction(
                moderator_id=user_1_admin.id,
                action_type=action_type,
                report_id=report_id,
                user_id=user_2.id,
            )
            db.session.add(report_action)
            db.session.flush()
        expected_report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="user_suspension",
            report_id=report_id,
            user_id=user_2.id,
        )
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.add(expected_report_action)
        db.session.commit()

        assert user_2.suspension_action == expected_report_action

    def test_suspension_action_is_none_when_user_is_unsuspended(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        report_id = self.create_report(
            reporter=user_1_admin, reported_object=user_2
        ).id
        for n in range(2):
            action_type = (
                "user_suspension" if n % 2 == 0 else "user_unsuspension"
            )
            report_action = ReportAction(
                moderator_id=user_1_admin.id,
                action_type=action_type,
                report_id=report_id,
                user_id=user_2.id,
            )
            db.session.add(report_action)
        db.session.commit()

        assert user_2.suspension_action is None

    def test_serializer_returns_related_report_id_when_user_is_admin(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        action_type = "user_suspension"
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type=action_type,
            report_id=self.create_report_user_action(
                user_1_admin, user_2, action_type
            ).id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()

        serialized_user = user_2.serialize(current_user=user_1_admin)

        assert (
            serialized_user["suspension_report_id"] == report_action.report_id
        )

    def test_serializer_does_not_return_related_report_id_when_user_is_not_admin(  # noqa
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        action_type = "user_suspension"
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type=action_type,
            report_id=self.create_report_user_action(
                user_1_admin, user_2, action_type
            ).id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()

        serialized_user = user_2.serialize(current_user=user_3)

        assert "suspension_report_id" not in serialized_user


class TestUserLightSerializer(UserModelAssertMixin):
    def test_it_returns_limited_user_infos_by_default(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1_admin)

        assert serialized_user == {
            "blocked": user_2.is_blocked_by(user_1_admin),
            "created_at": user_2.created_at,
            "email": user_2.email,
            "followers": user_2.followers.count(),
            "following": user_2.following.count(),
            "follows": user_2.follows(user_1_admin),
            "is_active": True,
            "is_followed_by": user_2.is_followed_by(user_1_admin),
            "nb_workouts": user_2.workouts_count,
            "picture": user_2.picture is not None,
            "role": UserRole(user_2.role).name.lower(),
            "suspended_at": None,
            "username": user_2.username,
        }

    def test_it_returns_limited_user_infos_as_admin(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(
            current_user=user_1_admin, light=True
        )

        assert serialized_user == {
            "blocked": user_2.is_blocked_by(user_1_admin),
            "created_at": user_2.created_at,
            "email": user_2.email,
            "followers": user_2.followers.count(),
            "following": user_2.following.count(),
            "follows": user_2.follows(user_1_admin),
            "is_active": True,
            "is_followed_by": user_2.is_followed_by(user_1_admin),
            "nb_workouts": user_2.workouts_count,
            "picture": user_2.picture is not None,
            "role": UserRole(user_2.role).name.lower(),
            "suspended_at": None,
            "username": user_2.username,
        }

    def test_it_returns_limited_user_infos_as_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=user_1, light=True)

        assert serialized_user == {
            "blocked": user_2.is_blocked_by(user_1),
            "created_at": user_2.created_at,
            "followers": user_2.followers.count(),
            "following": user_2.following.count(),
            "follows": user_2.follows(user_1),
            "is_followed_by": user_2.is_followed_by(user_1),
            "nb_workouts": user_2.workouts_count,
            "picture": user_2.picture is not None,
            "role": UserRole(user_2.role).name.lower(),
            "suspended_at": user_2.suspended_at,
            "username": user_2.username,
        }

    def test_it_returns_limited_user_infos_as_unauthenticated_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        serialized_user = user_2.serialize(current_user=None, light=True)

        assert serialized_user == {
            "created_at": user_2.created_at,
            "followers": user_2.followers.count(),
            "following": user_2.following.count(),
            "nb_workouts": user_2.workouts_count,
            "picture": user_2.picture is not None,
            "role": UserRole(user_2.role).name.lower(),
            "suspended_at": user_2.suspended_at,
            "username": user_2.username,
        }


class TestUserAllReportsCount(ReportMixin, CommentMixin):
    def test_it_returns_0_when_user_has_not_been_reported(
        self, app: Flask, user_1: User
    ) -> None:
        assert user_1.all_reports_count == {
            "created_reports_count": 0,
            "reported_count": 0,
            "sanctions_count": 0,
        }

    def test_it_returns_number_of_reports(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        self.create_user_report(user_1_admin, user_2)
        self.create_user_report(user_2, user_3)
        self.create_user_report(user_3, user_2)
        self.create_report_user_action(user_1_admin, user_2)

        assert user_2.all_reports_count == {
            "created_reports_count": 1,
            "reported_count": 3,
            "sanctions_count": 1,
        }

    @pytest.mark.parametrize(
        "input_action_type", ["user_unsuspension", "user_warning_lifting"]
    )
    def test_it_does_not_count_user_report_action_that_is_not_a_sanction(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        input_action_type: str,
    ) -> None:
        self.create_report_user_action(
            user_2_admin, user_1, action_type=input_action_type
        )

        assert user_1.all_reports_count["sanctions_count"] == 0

    def test_it_does_not_count_workout_unsuspension(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.create_report_workout_action(
            user_2_admin,
            user_1,
            workout_cycling_user_1,
            "workout_unsuspension",
        )

        assert user_1.all_reports_count["sanctions_count"] == 0

    def test_it_does_not_count_comment_unsuspension(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)
        self.create_report_comment_action(
            user_2_admin, user_1, comment, "comment_unsuspension"
        )

        assert user_1.all_reports_count["sanctions_count"] == 0


class TestUserSanctionsCount(ReportMixin, CommentMixin):
    def test_it_returns_sanctions_count(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        self.create_report_user_action(user_1_admin, user_2)
        self.create_report_user_action(user_1_admin, user_3)

        assert user_2.sanctions_count == 1

    @pytest.mark.parametrize(
        "input_action_type", ["user_unsuspension", "user_warning_lifting"]
    )
    def test_it_does_not_count_user_report_action_that_is_not_a_sanction(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        input_action_type: str,
    ) -> None:
        self.create_report_user_action(
            user_2_admin, user_1, action_type=input_action_type
        )

        assert user_1.sanctions_count == 0

    def test_it_does_not_count_workout_unsuspension(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.create_report_workout_action(
            user_2_admin,
            user_1,
            workout_cycling_user_1,
            "workout_unsuspension",
        )

        assert user_1.sanctions_count == 0

    def test_it_does_not_count_comment_unsuspension(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)
        self.create_report_comment_action(
            user_2_admin, user_1, comment, "comment_unsuspension"
        )

        assert user_1.sanctions_count == 0


class TestUserNotificationsPreferencesUpdate:
    def test_it_raises_error_when_notification_type_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.notification_preferences = {}

        with pytest.raises(ValidationError):
            user_1.update_preferences({"invalid": True})

    def test_it_raises_error_when_value_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.notification_preferences = {}

        with pytest.raises(ValidationError):
            user_1.update_preferences({"mention": "invalid"})

    @pytest.mark.parametrize("input_value", [True, False])
    def test_it_updates_preference_for_given_type(
        self, app: Flask, user_1: User, input_value: bool
    ) -> None:
        user_1.notification_preferences = {}

        user_1.update_preferences({"mention": input_value})

        assert user_1.notification_preferences == {"mention": input_value}

    def test_it_updates_preferences_when_preferences_exist(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.notification_preferences = {
            "mention": True,
            "follow_request": False,
        }

        user_1.update_preferences(
            {"mention": False, "workout_like": True, "comment_like": True}
        )

        assert user_1.notification_preferences == {
            "mention": False,
            "follow_request": False,
            "workout_like": True,
            "comment_like": True,
        }

    def test_it_updates_all_preferences(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.notification_preferences = {
            "mention": True,
            "follow_request": False,
        }
        updated_preferences = {
            "account_creation": True,
            "comment_like": True,
            "follow": True,
            "follow_request": True,
            "follow_request_approved": True,
            "mention": False,
            "workout_comment": False,
            "workout_like": False,
        }

        user_1.update_preferences(updated_preferences)

        assert user_1.notification_preferences == updated_preferences


class TestUserNotificationsPreferencesIsEnabled:
    @pytest.mark.parametrize(
        "input_notif_type", NOTIFICATION_TYPES_FOR_PREFERENCES
    )
    def test_it_returns_true_when_notification_type_is_not_in_preferences(
        self, app: Flask, user_1: User, input_notif_type: str
    ) -> None:
        user_1.notification_preferences = {}

        assert user_1.is_notification_enabled(input_notif_type) is True

    def test_it_returns_true_when_preferences_is_none(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.notification_preferences = None

        assert user_1.is_notification_enabled("mention") is True

    def test_it_returns_true_when_notification_type_is_not_in_schema(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.notification_preferences = {
            "account_creation": True,
            "comment_like": True,
            "follow": True,
            "follow_request": True,
            "follow_request_approved": True,
            "mention": False,
            "workout_comment": False,
            "workout_like": False,
        }

        assert user_1.is_notification_enabled("report") is True

    def test_it_returns_if_notification_is_enabled(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.notification_preferences = {
            "account_creation": True,
            "comment_like": True,
            "follow": True,
            "follow_request": True,
            "follow_request_approved": True,
            "mention": False,
            "workout_comment": False,
            "workout_like": False,
        }

        assert user_1.is_notification_enabled("mention") is False
