from datetime import datetime
from typing import Optional
from unittest.mock import patch

from fittrackee import db
from fittrackee.administration.models import AdminAction
from fittrackee.comments.models import Comment
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
from fittrackee.workouts.models import Workout

from ..mixins import RandomMixin


class CommentMixin(RandomMixin):
    def create_comment(
        self,
        user: User,
        workout: Workout,
        /,
        text: Optional[str] = None,
        text_visibility: PrivacyLevel = PrivacyLevel.PRIVATE,
        created_at: Optional[datetime] = None,
        parent_comment: Optional[Comment] = None,
        with_mentions: bool = True,
    ) -> Comment:
        text = self.random_string() if text is None else text
        comment = Comment(
            user_id=user.id,
            workout_id=workout.id,
            text=text,
            text_visibility=text_visibility,
            created_at=created_at,
            reply_to=parent_comment.id if parent_comment else None,
        )
        db.session.add(comment)
        db.session.flush()
        if with_mentions:
            with patch('fittrackee.federation.utils.user.update_remote_user'):
                comment.create_mentions()
        actor = comment.user.actor
        comment.ap_id = (
            f'{actor.activitypub_id}/workouts/{workout.short_id}'
            f'/comments/{comment.short_id}'
        )
        comment.remote_url = (
            f'https://{actor.domain.name}/workouts/{workout.short_id}'
            f'/comments/{comment.short_id}'
        )
        db.session.commit()
        return comment

    @staticmethod
    def create_admin_comment_suspension_action(
        admin: User, user: User, comment: Comment
    ) -> AdminAction:
        admin_action = AdminAction(
            action_type="comment_suspension",
            admin_user_id=admin.id,
            comment_id=comment.id,
            user_id=user.id,
        )
        db.session.add(admin_action)
        comment.suspended_at = datetime.utcnow()
        return admin_action

    @staticmethod
    def create_admin_comment_actions(
        admin: User, user: User, comment: Comment
    ) -> AdminAction:
        for n in range(2):
            admin_action = AdminAction(
                action_type=(
                    "comment_suspension"
                    if n % 2 == 0
                    else "comment_unsuspension"
                ),
                admin_user_id=admin.id,
                comment_id=comment.id,
                user_id=user.id,
            )
            db.session.add(admin_action)
        admin_action = AdminAction(
            action_type="comment_suspension",
            admin_user_id=admin.id,
            comment_id=comment.id,
            user_id=user.id,
        )
        db.session.add(admin_action)
        return admin_action
