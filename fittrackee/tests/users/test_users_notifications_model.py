from datetime import datetime
from typing import Optional

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.comments.models import Comment, CommentLike, Mention
from fittrackee.reports.models import (
    COMMENT_ACTION_TYPES,
    WORKOUT_ACTION_TYPES,
    Report,
)
from fittrackee.tests.comments.mixins import CommentMixin
from fittrackee.users.exceptions import InvalidNotificationTypeException
from fittrackee.users.models import FollowRequest, Notification, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout, WorkoutLike

from ..mixins import ReportMixin
from ..utils import random_int, random_string


class NotificationTestCase:
    @staticmethod
    def create_mention(user: User, comment: Comment) -> Mention:
        mention = Mention(comment.id, user.id)
        db.session.add(mention)
        db.session.commit()
        return mention

    @staticmethod
    def comment_workout(
        user: User,
        workout: Workout,
        text: Optional[str] = None,
        text_visibility: Optional[VisibilityLevel] = None,
    ) -> Comment:
        comment = Comment(
            user_id=user.id,
            workout_id=workout.id,
            text=random_string() if text is None else text,
            text_visibility=(
                text_visibility if text_visibility else VisibilityLevel.PUBLIC
            ),
        )
        db.session.add(comment)
        db.session.commit()
        return comment

    @staticmethod
    def like_comment(user: User, comment: Comment) -> CommentLike:
        like = CommentLike(user_id=user.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()
        return like

    @staticmethod
    def like_workout(user: User, workout: Workout) -> WorkoutLike:
        like = WorkoutLike(user_id=user.id, workout_id=workout.id)
        db.session.add(like)
        db.session.commit()
        return like


class TestNotification:
    def test_it_raises_exception_when_type_is_invalid(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        with pytest.raises(InvalidNotificationTypeException):
            Notification(
                from_user_id=user_1.id,
                to_user_id=user_2.id,
                created_at=datetime.utcnow(),
                event_type=random_string(),
                event_object_id=random_int(),
            )


class TestNotificationForFollowRequest:
    def test_it_creates_notification_on_follow_request(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        follow_request = user_1.send_follow_request_to(user_2)

        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
        ).first()
        assert notification.created_at == follow_request.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == 'follow_request'
        assert notification.event_object_id is None

    def test_it_creates_notification_on_follow_when_user_automatically_approves_request(  # noqa
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_2.manually_approves_followers = False

        follow_request = user_1.send_follow_request_to(user_2)

        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
        ).first()
        assert notification.created_at == follow_request.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == 'follow'
        assert notification.event_object_id is None

    def test_it_does_not_create_notification_for_follower_when_user_automatically_approves_request(  # noqa
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_2.manually_approves_followers = False

        user_1.send_follow_request_to(user_2)

        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
        ).first()
        assert notification is None

    def test_it_updates_notification_when_user_approves_follow_request(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        follow_request = user_1.send_follow_request_to(user_2)

        user_2.approves_follow_request_from(user_1)

        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
        ).first()
        assert notification.created_at == follow_request.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == 'follow'
        assert notification.event_object_id is None

    def test_it_creates_notification_for_follower_when_user_approves_follow_request(  # noqa
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.send_follow_request_to(user_2)
        now = datetime.utcnow()

        with travel(now, tick=False):
            user_2.approves_follow_request_from(user_1)

        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
        ).first()
        assert notification.created_at == now
        assert notification.marked_as_read is False
        assert notification.event_type == 'follow_request_approved'
        assert notification.event_object_id is None

    def test_it_deletes_notification_when_user_rejects_follow_request(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.send_follow_request_to(user_2)

        user_2.rejects_follow_request_from(user_1)

        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
        ).first()
        assert notification is None

    def test_it_deletes_notifications_when_user_deletes_follow_request(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.send_follow_request_to(user_2)
        user_1.unfollows(user_2)

        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
        ).first()
        assert notification is None
        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
        ).first()
        assert notification is None

    def test_it_deletes_notification_when_user_unfollows(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.send_follow_request_to(user_2)
        user_2.approves_follow_request_from(user_1)
        user_1.unfollows(user_2)

        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
        ).first()
        assert notification is None
        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
        ).first()
        assert notification is None

    def test_it_updates_notification_read_status_when_user_approves_follow_request(  # noqa
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        follow_request = user_1.send_follow_request_to(user_2)
        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
        ).first()
        notification.marked_as_read = True
        user_2.approves_follow_request_from(user_1)

        assert notification.created_at == follow_request.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == 'follow'
        assert notification.event_object_id is None

    @pytest.mark.parametrize('manually_approves_followers', [True, False])
    def test_it_deletes_notification_on_follow_request_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        manually_approves_followers: bool,
    ) -> None:
        follow_request = user_1.send_follow_request_to(user_2)
        db.session.delete(follow_request)

        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
        ).first()
        assert notification is None
        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
        ).first()
        assert notification is None

    def test_it_serializes_follow_request_notification(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.send_follow_request_to(user_2)
        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] == {
            **user_1.serialize(),
            "follows": user_1.follows(user_2),
            "is_followed_by": user_1.is_followed_by(user_2),
        }
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "follow_request"
        assert "report_action" not in serialized_notification
        assert "comment" not in serialized_notification
        assert "report" not in serialized_notification
        assert "workout" not in serialized_notification

    def test_it_serializes_follow_notification(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_2.manually_approves_followers = False
        user_1.send_follow_request_to(user_2)
        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] == {
            **user_1.serialize(),
            "follows": user_1.follows(user_2),
            "is_followed_by": user_1.is_followed_by(user_2),
        }
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "follow"
        assert "report_action" not in serialized_notification
        assert "comment" not in serialized_notification
        assert "report" not in serialized_notification
        assert "workout" not in serialized_notification

    def test_it_serializes_follow_request_approved_notification(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.send_follow_request_to(user_2)
        user_2.approves_follow_request_from(user_1)
        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1.id,
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] == {
            **user_2.serialize(),
            "blocked": False,
            "follows": 'false',
            "is_followed_by": 'true',
        }
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "follow_request_approved"
        assert "report_action" not in serialized_notification
        assert "comment" not in serialized_notification
        assert "report" not in serialized_notification
        assert "workout" not in serialized_notification


class TestNotificationForWorkoutLike(NotificationTestCase):
    def test_it_creates_notification_on_workout_like(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_cycling_user_1: Workout,
    ) -> None:
        like = self.like_workout(user_2, workout_cycling_user_1)

        notification = Notification.query.filter_by(
            from_user_id=like.user_id,
            to_user_id=workout_cycling_user_1.user_id,
            event_object_id=workout_cycling_user_1.id,
        ).first()
        assert notification.created_at == like.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == 'workout_like'

    def test_it_deletes_notification_on_workout_like_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_cycling_user_1: Workout,
    ) -> None:
        like = self.like_workout(user_2, workout_cycling_user_1)

        db.session.delete(like)

        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=workout_cycling_user_1.user_id,
            event_object_id=workout_cycling_user_1.id,
            event_type='workout_like',
        ).first()
        assert notification is None

    def test_it_does_not_create_notification_when_user_likes_his_own_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.like_workout(user_1, workout_cycling_user_1)

        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=workout_cycling_user_1.user_id,
            event_object_id=workout_cycling_user_1.id,
        ).first()
        assert notification is None

    def test_it_does_not_raise_error_when_user_unlike_his_own_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_cycling_user_1: Workout,
    ) -> None:
        like = self.like_workout(user_1, workout_cycling_user_1)

        db.session.delete(like)

    def test_it_serializes_workout_like_notification(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.like_workout(user_2, workout_cycling_user_1)
        notification = Notification.query.filter_by(
            event_object_id=workout_cycling_user_1.id,
            event_type='workout_like',
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] == user_2.serialize(
            current_user=user_1
        )
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "workout_like"
        assert serialized_notification[
            "workout"
        ] == workout_cycling_user_1.serialize(user=user_1)
        assert "report_action" not in serialized_notification
        assert "comment" not in serialized_notification
        assert "report" not in serialized_notification


class TestNotificationForWorkoutComment(NotificationTestCase):
    def test_it_creates_notification_on_workout_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.comment_workout(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )

        notification = Notification.query.filter_by(
            from_user_id=comment.user_id,
            to_user_id=workout_cycling_user_1.user_id,
            event_object_id=comment.id,
        ).first()
        assert notification.created_at == comment.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == 'workout_comment'

    def test_it_deletes_notification_on_workout_comment_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.comment_workout(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        comment_id = comment.id

        db.session.delete(comment)

        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=workout_cycling_user_1.user_id,
            event_object_id=comment_id,
            event_type='workout_comment',
        ).first()
        assert notification is None

    def test_it_does_not_create_notification_when_user_comments_his_own_workout(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_1, workout_cycling_user_1)

        notification = Notification.query.filter_by(
            from_user_id=comment.user_id,
            to_user_id=workout_cycling_user_1.user_id,
            event_object_id=comment.id,
        ).first()
        assert notification is None

    @pytest.mark.parametrize(
        'workout_visibility, text_visibility',
        [
            (VisibilityLevel.FOLLOWERS, VisibilityLevel.FOLLOWERS),
            (VisibilityLevel.FOLLOWERS, VisibilityLevel.PRIVATE),  # no mention
        ],
    )
    def test_it_does_not_create_notification_when_visibility_does_not_allowed_it(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_visibility: VisibilityLevel,
        text_visibility: VisibilityLevel,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        # user_1 does not follow user_2, user_2 follows user_1
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = workout_visibility
        comment = self.comment_workout(
            user_2, workout_cycling_user_1, text_visibility=text_visibility
        )

        notification = Notification.query.filter_by(
            from_user_id=comment.user_id,
            to_user_id=workout_cycling_user_1.user_id,
            event_object_id=comment.id,
        ).first()
        assert notification is None

    def test_it_does_not_raise_error_when_user_unlike_his_own_workout(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_1, workout_cycling_user_1)

        db.session.delete(comment)

    def test_it_serializes_workout_comment_notification(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.comment_workout(user_2, workout_cycling_user_1)
        notification = Notification.query.filter_by(
            event_object_id=comment.id,
            event_type='workout_comment',
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["comment"] == comment.serialize(user_1)
        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] == user_2.serialize(
            current_user=user_1
        )
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "workout_comment"
        assert "report_action" not in serialized_notification
        assert "report" not in serialized_notification
        assert "workout" not in serialized_notification


class TestNotificationForWorkoutReportAction(
    NotificationTestCase, ReportMixin
):
    @pytest.mark.parametrize("input_report_action", WORKOUT_ACTION_TYPES)
    def test_it_creates_notification_on_comment_report_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_report_action: str,
    ) -> None:
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )

        report_action = self.create_report_action(
            user_1_moderator,
            user_2,
            action_type=input_report_action,
            report_id=report.id,
            workout_id=workout_cycling_user_2.id,
        )

        notification = Notification.query.filter_by(
            from_user_id=user_1_moderator.id,
            to_user_id=user_2.id,
            event_object_id=workout_cycling_user_2.id,
        ).first()
        assert notification.created_at == report_action.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == input_report_action

    @pytest.mark.parametrize("input_report_action", WORKOUT_ACTION_TYPES)
    def test_it_serializes_comment_action_notification(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_report_action: str,
    ) -> None:
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        report_action = self.create_report_action(
            user_1_moderator,
            user_2,
            action_type=input_report_action,
            report_id=report.id,
            workout_id=workout_cycling_user_2.id,
        )
        notification = Notification.query.filter_by(
            from_user_id=user_1_moderator.id,
            to_user_id=user_2.id,
            event_object_id=workout_cycling_user_2.id,
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification[
            "report_action"
        ] == report_action.serialize(user_2)
        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] is None
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == input_report_action
        assert serialized_notification[
            "workout"
        ] == workout_cycling_user_2.serialize(user=user_2)
        assert "comment" not in serialized_notification
        assert "report" not in serialized_notification


class TestNotificationForCommentLike(NotificationTestCase):
    def test_it_creates_notification_on_comment_like(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_2, workout_cycling_user_1)
        like = self.like_comment(user_3, comment)

        notification = Notification.query.filter_by(
            from_user_id=like.user_id,
            to_user_id=comment.user_id,
            event_object_id=like.id,
        ).first()
        assert notification.created_at == like.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == 'comment_like'

    def test_it_deletes_notification_on_comment_like_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_2, workout_cycling_user_1)
        like = self.like_comment(user_3, comment)
        like_id = like.id

        db.session.delete(like)

        notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=comment.user_id,
            event_object_id=like_id,
            event_type='comment_like',
        ).first()
        assert notification is None

    def test_it_does_not_create_notification_when_user_likes_to_his_comment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_1, workout_cycling_user_1)
        like = self.like_comment(user_1, comment)

        notification = Notification.query.filter_by(
            from_user_id=like.user_id,
            to_user_id=comment.user_id,
            event_object_id=like.id,
        ).first()
        assert notification is None

    def test_it_does_not_raise_error_when_user_unlikes_on_his_own_comment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_1, workout_cycling_user_1)
        like = self.like_comment(user_1, comment)

        db.session.delete(like)

    def test_it_serializes_comment_like_notification(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_1, workout_cycling_user_1)
        like = self.like_comment(user_2, comment)
        notification = Notification.query.filter_by(
            event_object_id=like.id,
            event_type='comment_like',
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["comment"] == comment.serialize(user_1)
        assert serialized_notification["from"] == user_2.serialize(
            current_user=user_1
        )
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "comment_like"
        assert "report_action" not in serialized_notification
        assert "report" not in serialized_notification
        assert "workout" not in serialized_notification


class TestNotificationForCommentReportAction(
    NotificationTestCase, ReportMixin
):
    @pytest.mark.parametrize("input_report_action", COMMENT_ACTION_TYPES)
    def test_it_creates_notification_on_comment_report_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_report_action: str,
    ) -> None:
        comment = self.comment_workout(user_3, workout_cycling_user_2)
        report = self.create_report(reporter=user_2, reported_object=comment)

        report_action = self.create_report_action(
            user_1_moderator,
            user_3,
            action_type=input_report_action,
            report_id=report.id,
            comment_id=comment.id,
        )

        notification = Notification.query.filter_by(
            from_user_id=user_1_moderator.id,
            to_user_id=user_3.id,
            event_object_id=comment.id,
        ).first()
        assert notification.created_at == report_action.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == input_report_action

    @pytest.mark.parametrize("input_report_action", COMMENT_ACTION_TYPES)
    def test_it_serializes_comment_action_notification(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_report_action: str,
    ) -> None:
        comment = self.comment_workout(user_3, workout_cycling_user_2)
        report = self.create_report(reporter=user_2, reported_object=comment)
        report_action = self.create_report_action(
            user_1_moderator,
            user_3,
            action_type=input_report_action,
            report_id=report.id,
            comment_id=comment.id,
        )
        notification = Notification.query.filter_by(
            from_user_id=user_1_moderator.id,
            to_user_id=user_3.id,
            event_object_id=comment.id,
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification[
            "report_action"
        ] == report_action.serialize(user_3)
        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["comment"] == comment.serialize(user_3)
        assert serialized_notification["from"] is None
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == input_report_action
        assert "report" not in serialized_notification
        assert "workout" not in serialized_notification


class TestNotificationForMention(NotificationTestCase):
    def test_it_creates_notification_on_mention(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(
            user_2, workout_cycling_user_1, text=f"@{user_3.username}"
        )
        mention = self.create_mention(user_3, comment)

        notification = Notification.query.filter_by(
            from_user_id=comment.user_id,
            to_user_id=user_3.id,
            event_object_id=comment.id,
        ).first()
        assert notification.created_at == mention.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == 'mention'

    def test_it_does_not_create_notification_when_mentioned_user_is_workout_owner(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        """comment is visible to user"""
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.comment_workout(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_1.username}",
            text_visibility=VisibilityLevel.PUBLIC,
        )
        self.create_mention(user_1, comment)

        notifications = Notification.query.filter_by(
            from_user_id=comment.user_id,
            to_user_id=user_1.id,
        ).all()
        assert len(notifications) == 1
        assert notifications[0].created_at == comment.created_at
        assert notifications[0].marked_as_read is False
        assert notifications[0].event_type == 'workout_comment'

    @pytest.mark.parametrize(
        'input_visibility_level',
        [VisibilityLevel.FOLLOWERS, VisibilityLevel.PRIVATE],
    )
    def test_it_creates_notification_when_mentioned_user_is_workout_owner(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility_level: VisibilityLevel,
    ) -> None:
        """comment is visible to user thanks to the mention"""
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.comment_workout(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_1.username}",
            text_visibility=input_visibility_level,
        )
        mention = self.create_mention(user_1, comment)

        notifications = Notification.query.filter_by(
            from_user_id=comment.user_id,
            to_user_id=user_1.id,
        ).all()
        assert len(notifications) == 1
        assert notifications[0].created_at == mention.created_at
        assert notifications[0].marked_as_read is False
        assert notifications[0].event_type == 'mention'

    def test_it_deletes_notification_on_mention_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(
            user_2, workout_cycling_user_1, text=f"@{user_3.username}"
        )
        mention = self.create_mention(user_3, comment)
        comment_id = comment.id

        db.session.delete(mention)

        notification = Notification.query.filter_by(
            from_user_id=comment.user_id,
            to_user_id=user_3.id,
            event_object_id=comment_id,
            event_type='mention',
        ).first()
        assert notification is None

    def test_it_does_not_create_notification_on_own_mention(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(
            user_2, workout_cycling_user_1, text=f"@{user_2.username}"
        )
        self.create_mention(user_2, comment)

        notification = Notification.query.filter_by(
            from_user_id=comment.user_id,
            to_user_id=user_2.id,
            event_object_id=comment.id,
            event_type='mention',
        ).first()
        assert notification is None

    def test_it_serializes_mention_notification(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.comment_workout(
            user_1, workout_cycling_user_1, text=f"@{user_2.username}"
        )
        self.create_mention(user_2, comment)
        notification = Notification.query.filter_by(
            from_user_id=comment.user_id,
            to_user_id=user_2.id,
            event_object_id=comment.id,
            event_type='mention',
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["comment"] == comment.serialize(user_2)
        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] == user_1.serialize(
            current_user=user_2
        )
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "mention"
        assert "report_action" not in serialized_notification
        assert "report" not in serialized_notification
        assert "workout" not in serialized_notification


class TestMultipleNotificationsForComment(NotificationTestCase):
    def test_it_deletes_all_notifications_on_comment_with_mention_and_like_delete(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(
            user_2, workout_cycling_user_1, text=f"@{user_3.username}"
        )
        comment_id = comment.id
        self.create_mention(user_3, comment)
        self.like_comment(user_3, comment)

        db.session.delete(comment)

        # workout_comment notification is deleted
        assert (
            Notification.query.filter_by(
                from_user_id=user_2.id,
                to_user_id=user_1.id,
                event_object_id=comment_id,
                event_type="workout_comment",
            ).first()
            is None
        )
        # mention notification is deleted
        assert (
            Notification.query.filter_by(
                from_user_id=user_2.id,
                to_user_id=user_3.id,
                event_object_id=comment_id,
                event_type="mention",
            ).first()
            is None
        )
        # like notification is deleted
        assert (
            Notification.query.filter_by(
                from_user_id=user_2.id,
                to_user_id=user_3.id,
                event_object_id=comment_id,
                event_type="comment_like",
            ).first()
            is None
        )


class TestNotificationForReport(NotificationTestCase):
    def test_it_does_not_create_notifications_when_no_admin(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        report = Report(
            note=random_string(),
            reported_by=user_1.id,
            reported_object=user_2,
        )
        db.session.add(report)
        db.session.commit()

        notification = Notification.query.filter_by(
            event_type='report', event_object_id=report.id
        ).first()

        assert notification is None

    def test_it_does_not_create_notification_when_admin_is_reporter(
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        report = Report(
            note=random_string(),
            reported_by=user_1_moderator.id,
            reported_object=user_2,
        )
        db.session.add(report)
        db.session.commit()

        notification = Notification.query.filter_by(
            event_type='report', event_object_id=report.id
        ).first()

        assert notification is None

    def test_it_does_not_create_notification_when_admin_is_inactive(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = Report(
            note=random_string(),
            reported_by=user_3.id,
            reported_object=user_2,
        )
        db.session.add(report)
        user_1_moderator.is_active = False
        db.session.commit()

        notification = Notification.query.filter_by(
            event_type='report', event_object_id=report.id
        ).first()
        assert notification is None

    def test_it_creates_notification_on_report_creation(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = Report(
            note=random_string(),
            reported_by=user_3.id,
            reported_object=user_2,
        )
        db.session.add(report)
        db.session.commit()

        notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=user_1_moderator.id,
        ).first()
        assert notification.created_at == report.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == 'report'
        assert notification.event_object_id == report.id

    def test_it_creates_notifications_for_all_admins_and_moderators(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2_admin: User,
        user_3: User,
        user_4: User,
    ) -> None:
        report = Report(
            note=random_string(),
            reported_by=user_3.id,
            reported_object=user_4,
        )
        db.session.add(report)
        db.session.commit()

        notifications = Notification.query.filter_by(
            from_user_id=user_3.id,
        ).all()
        assert len(notifications) == 2
        assert {notifications[0].to_user_id, notifications[1].to_user_id} == {
            user_1_moderator.id,
            user_2_admin.id,
        }

    def test_it_serializes_report_notification(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.comment_workout(user_3, workout_cycling_user_2)
        report = Report(
            note=random_string(),
            reported_by=user_2.id,
            reported_object=comment,
        )
        db.session.add(report)
        db.session.commit()
        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1_moderator.id,
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] == user_2.serialize(
            current_user=user_1_moderator
        )
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["report"] == report.serialize(
            user_1_moderator
        )
        assert serialized_notification["type"] == "report"


class TestNotificationForSuspensionAppeal(CommentMixin, ReportMixin):
    def test_it_does_not_create_notification_when_admin_is_inactive(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        suspension_action = self.create_report_user_action(
            user_1_moderator, user_2
        )
        self.create_action_appeal(
            suspension_action.id, user_2, with_commit=False
        )
        user_1_moderator.is_active = False
        db.session.commit()

        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1_moderator.id,
        ).first()
        assert notification is None

    def test_it_creates_notification_on_user_appeal(
        self, app: Flask, user_1_moderator: User, user_2: User
    ) -> None:
        suspension_action = self.create_report_user_action(
            user_1_moderator, user_2
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)

        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1_moderator.id,
        ).first()
        assert notification.created_at == appeal.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == "suspension_appeal"
        assert notification.event_object_id == appeal.id

    def test_it_creates_notification_on_workout_suspension_appeal(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_suspension = self.create_report_workout_action(
            user_1_moderator, user_2, workout_cycling_user_2
        )
        db.session.add(workout_suspension)
        db.session.flush()

        # appeal = ReportActionAppeal(
        #     workout_suspension.id, user_2.id, self.random_string()
        # )

        appeal = self.create_action_appeal(workout_suspension.id, user_2)
        db.session.add(appeal)
        db.session.commit()

        notifications = Notification.query.filter_by(
            event_type='suspension_appeal'
        ).all()
        assert len(notifications) == 1
        assert notifications[0].from_user_id == user_2.id
        assert notifications[0].to_user_id == user_1_moderator.id
        assert notifications[0].event_object_id == workout_suspension.id

    def test_it_creates_notification_on_comment_suspension_appeal(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        comment_suspension = self.create_report_comment_action(
            user_1_moderator, user_2, comment
        )
        db.session.add(comment_suspension)
        db.session.flush()

        # appeal = ReportActionAppeal(
        #     comment_suspension.id, user_2.id, self.random_string()
        # )
        appeal = self.create_action_appeal(comment_suspension.id, user_2)
        db.session.add(appeal)
        db.session.commit()

        notifications = Notification.query.filter_by(
            event_type='suspension_appeal'
        ).all()
        assert len(notifications) == 1
        assert notifications[0].from_user_id == user_2.id
        assert notifications[0].to_user_id == user_1_moderator.id
        assert notifications[0].event_object_id == comment_suspension.id

    def test_it_serializes_suspension_appeal_notification(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_3, reported_object=user_2)
        suspension_action = self.create_report_user_action(
            user_1_moderator, user_2, report_id=report.id
        )
        self.create_action_appeal(suspension_action.id, user_2)
        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1_moderator.id,
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] == user_2.serialize(
            current_user=user_1_moderator
        )
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["report"] == report.serialize(
            user_1_moderator
        )
        assert serialized_notification["type"] == "suspension_appeal"


class TestNotificationForUserWarning(NotificationTestCase, ReportMixin):
    @pytest.mark.parametrize(
        'input_action_type', ['user_warning', 'user_warning_lifting']
    )
    def test_it_creates_notification_on_user_action_on_user_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)

        report_action = self.create_report_action(
            user_1_moderator,
            user_3,
            action_type=input_action_type,
            report_id=report.id,
        )

        notification = Notification.query.filter_by(
            from_user_id=user_1_moderator.id,
            to_user_id=user_3.id,
        ).first()
        assert notification.created_at == report_action.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == input_action_type

    @pytest.mark.parametrize(
        'input_action_type', ['user_warning', 'user_warning_lifting']
    )
    def test_it_serializes_user_action_notification_on_user_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        report_action = self.create_report_action(
            user_1_moderator,
            user_3,
            action_type=input_action_type,
            report_id=report.id,
        )
        notification = Notification.query.filter_by(
            from_user_id=user_1_moderator.id,
            to_user_id=user_3.id,
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification[
            "report_action"
        ] == report_action.serialize(user_3)
        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] is None
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == input_action_type
        assert "comment" not in serialized_notification
        assert "report" not in serialized_notification
        assert "workout" not in serialized_notification

    @pytest.mark.parametrize(
        'input_action_type', ['user_warning', 'user_warning_lifting']
    )
    def test_it_creates_notification_on_user_action_on_workout_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )

        report_action = self.create_report_action(
            user_1_moderator,
            user_2,
            action_type=input_action_type,
            report_id=report.id,
        )

        notification = Notification.query.filter_by(
            from_user_id=user_1_moderator.id,
            to_user_id=user_2.id,
        ).first()
        assert notification.created_at == report_action.created_at
        assert notification.marked_as_read is False
        assert notification.event_object_id == workout_cycling_user_2.id
        assert notification.event_type == input_action_type

    @pytest.mark.parametrize(
        'input_action_type', ['user_warning', 'user_warning_lifting']
    )
    def test_it_serializes_user_action_notification_on_workout_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        report_action = self.create_report_action(
            user_1_moderator,
            user_2,
            action_type=input_action_type,
            report_id=report.id,
        )
        notification = Notification.query.filter_by(
            from_user_id=user_1_moderator.id,
            to_user_id=user_2.id,
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification[
            "report_action"
        ] == report_action.serialize(user_2)
        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] is None
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == input_action_type
        assert serialized_notification[
            "workout"
        ] == workout_cycling_user_2.serialize(user=user_2)
        assert "comment" not in serialized_notification
        assert "report" not in serialized_notification

    @pytest.mark.parametrize(
        'input_action_type', ['user_warning', 'user_warning_lifting']
    )
    def test_it_creates_notification_on_user_action_on_comment_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        comment = self.comment_workout(user_3, workout_cycling_user_2)
        report = self.create_report(reporter=user_2, reported_object=comment)

        report_action = self.create_report_action(
            user_1_moderator,
            user_3,
            action_type=input_action_type,
            report_id=report.id,
        )

        notification = Notification.query.filter_by(
            from_user_id=user_1_moderator.id,
            to_user_id=user_3.id,
        ).first()
        assert notification.created_at == report_action.created_at
        assert notification.marked_as_read is False
        assert notification.event_object_id == comment.id
        assert notification.event_type == input_action_type

    @pytest.mark.parametrize(
        'input_action_type', ['user_warning', 'user_warning_lifting']
    )
    def test_it_serializes_user_action_notification_on_comment_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        comment = self.comment_workout(user_3, workout_cycling_user_2)
        report = self.create_report(reporter=user_2, reported_object=comment)
        report_action = self.create_report_action(
            user_1_moderator,
            user_3,
            action_type=input_action_type,
            report_id=report.id,
        )
        notification = Notification.query.filter_by(
            from_user_id=user_1_moderator.id,
            to_user_id=user_3.id,
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification[
            "report_action"
        ] == report_action.serialize(user_3)
        assert serialized_notification["comment"] == comment.serialize(user_3)
        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] is None
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == input_action_type
        assert "report" not in serialized_notification
        assert "workout" not in serialized_notification


class TestNotificationForUserWarningAppeal(NotificationTestCase, ReportMixin):
    def test_it_does_not_create_notification_when_admin_is_inactive(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        report_action = self.create_report_action(
            user_1_moderator,
            user_2,
            action_type="user_warning",
            report_id=report.id,
        )
        self.create_action_appeal(report_action.id, user_2, with_commit=False)
        user_1_moderator.is_active = False
        db.session.commit()

        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1_moderator.id,
            event_type='user_warning_appeal',
        ).first()
        assert notification is None

    def test_it_creates_notification_on_appeal(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        report_action = self.create_report_action(
            user_1_moderator,
            user_2,
            action_type="user_warning",
            report_id=report.id,
        )
        appeal = self.create_action_appeal(report_action.id, user_2)

        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1_moderator.id,
            event_type='user_warning_appeal',
        ).first()
        assert notification.created_at == appeal.created_at
        assert notification.marked_as_read is False
        assert notification.event_object_id == appeal.id

    def test_it_serializes_user_warning_appeal_notification(
        self, app: Flask, user_1_moderator: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        report_action = self.create_report_action(
            user_1_moderator,
            user_2,
            action_type="user_warning",
            report_id=report.id,
        )
        self.create_action_appeal(report_action.id, user_2)
        notification = Notification.query.filter_by(
            from_user_id=user_2.id,
            to_user_id=user_1_moderator.id,
            event_type='user_warning_appeal',
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] == user_2.serialize(
            current_user=user_1_moderator
        )
        assert serialized_notification["id"] == notification.short_id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["report"] == report.serialize(
            user_1_moderator
        )
        assert serialized_notification["type"] == "user_warning_appeal"
