from datetime import datetime
from typing import Optional

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.comments.models import Comment, CommentLike, Mention
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.exceptions import InvalidNotificationTypeException
from fittrackee.users.models import FollowRequest, Notification, User
from fittrackee.workouts.models import Sport, Workout, WorkoutLike

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
        reply_to: Optional[int] = None,
        text: Optional[str] = None,
        text_visibility: Optional[PrivacyLevel] = None,
    ) -> Comment:
        comment = Comment(
            user_id=user.id,
            workout_id=workout.id,
            text=random_string() if text is None else text,
            text_visibility=(
                text_visibility if text_visibility else PrivacyLevel.PUBLIC
            ),
        )
        db.session.add(comment)
        comment.reply_to = reply_to
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
                from_user_id=user_1,
                to_user_id=user_2,
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

    def test_it_deletes_notification_when_user_deletes_follow_request(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        user_1.send_follow_request_to(user_2)
        user_1.unfollows(user_2)

        notification = Notification.query.filter_by(
            from_user_id=user_1.id,
            to_user_id=user_2.id,
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

    def test_serialize_follow_request_notification(
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
        assert serialized_notification["id"] == notification.id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "follow_request"

    def test_serialize_follow_notification(
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
        assert serialized_notification["id"] == notification.id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "follow"


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

    def test_serialize_workout_like_notification(
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
        assert serialized_notification["id"] == notification.id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "workout_like"
        assert serialized_notification[
            "workout"
        ] == workout_cycling_user_1.serialize(user_1)


class TestNotificationForWorkoutComment(NotificationTestCase):
    def test_it_creates_notification_on_workout_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.comment_workout(
            user_2, workout_cycling_user_1, text_visibility=PrivacyLevel.PUBLIC
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.comment_workout(
            user_2, workout_cycling_user_1, text_visibility=PrivacyLevel.PUBLIC
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
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.FOLLOWERS),
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE),  # no mention
        ],
    )
    def test_it_does_not_create_notification_when_visibility_does_not_allowed_it(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_visibility: PrivacyLevel,
        text_visibility: PrivacyLevel,
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

    def test_serialize_workout_comment_notification(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
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
        assert serialized_notification["id"] == notification.id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "workout_comment"


class TestNotificationForCommentReply(NotificationTestCase):
    def test_it_creates_notification_on_comment_reply(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.comment_workout(user_2, workout_cycling_user_1)
        reply = self.comment_workout(
            user_3, workout_cycling_user_1, comment.id
        )

        notification = Notification.query.filter_by(
            from_user_id=reply.user_id,
            to_user_id=comment.user_id,
            event_object_id=reply.id,
        ).first()
        assert notification.created_at == reply.created_at
        assert notification.marked_as_read is False
        assert notification.event_type == 'comment_reply'

    def test_it_deletes_notification_on_comment_reply_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_2, workout_cycling_user_1)
        reply = self.comment_workout(
            user_3, workout_cycling_user_1, comment.id
        )
        reply_id = reply.id

        db.session.delete(comment)

        notification = Notification.query.filter_by(
            from_user_id=user_3.id,
            to_user_id=workout_cycling_user_1.user_id,
            event_object_id=reply_id,
            event_type='comment_reply',
        ).first()
        assert notification is None

    def test_it_does_not_create_notification_when_user_replies_to_his_comment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_1, workout_cycling_user_1)
        reply = self.comment_workout(
            user_1, workout_cycling_user_1, comment.id
        )

        notification = Notification.query.filter_by(
            from_user_id=reply.user_id,
            to_user_id=workout_cycling_user_1.user_id,
            event_object_id=reply.id,
        ).first()
        assert notification is None

    def test_it_does_not_raise_error_when_user_deletes_reply_on_his_own_comment(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_1, workout_cycling_user_1)
        reply = self.comment_workout(
            user_1, workout_cycling_user_1, comment.id
        )

        db.session.delete(reply)

    def test_serialize_comment_reply_notification(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.comment_workout(user_1, workout_cycling_user_1)
        reply = self.comment_workout(
            user_2, workout_cycling_user_1, comment.id
        )
        notification = Notification.query.filter_by(
            event_object_id=reply.id,
            event_type='comment_reply',
        ).first()

        serialized_notification = notification.serialize()

        assert serialized_notification["comment"] == reply.serialize(user_1)
        assert serialized_notification["created_at"] == notification.created_at
        assert serialized_notification["from"] == user_2.serialize(
            current_user=user_1
        )
        assert serialized_notification["id"] == notification.id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "comment_reply"


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

    def test_serialize_comment_like_notification(
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
        assert serialized_notification["id"] == notification.id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "comment_like"


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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.comment_workout(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_1.username}",
            text_visibility=PrivacyLevel.PUBLIC,
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

    def test_it_does_not_create_notification_when_mentioned_user_is_parent_comment_owner(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        parent_comment = self.comment_workout(
            user_2, workout_cycling_user_1, text_visibility=PrivacyLevel.PUBLIC
        )
        comment = self.comment_workout(
            user_3,
            workout_cycling_user_1,
            reply_to=parent_comment.id,
            text=f"@{user_2.username}",
            text_visibility=PrivacyLevel.PUBLIC,
        )
        self.create_mention(user_2, comment)

        notifications = Notification.query.filter_by(
            from_user_id=comment.user_id,
            to_user_id=user_2.id,
        ).all()
        assert len(notifications) == 1
        assert notifications[0].created_at == comment.created_at
        assert notifications[0].marked_as_read is False
        assert notifications[0].event_type == 'comment_reply'

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

    def test_serialize_mention_notification(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
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
        assert serialized_notification["id"] == notification.id
        assert serialized_notification["marked_as_read"] is False
        assert serialized_notification["type"] == "mention"


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

    def test_it_deletes_all_notifications_on_reply_with_mention_and_like_delete(  # noqa
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
        reply = self.comment_workout(
            user_1, workout_cycling_user_1, comment.id
        )

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
        # comment_reply notification is not deleted
        assert (
            Notification.query.filter_by(
                from_user_id=user_1.id,
                to_user_id=user_2.id,
                event_object_id=reply.id,
                event_type="comment_reply",
            ).first()
            is not None
        )
