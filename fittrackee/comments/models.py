import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from flask import current_app
from sqlalchemy import and_, or_
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import Enum

from fittrackee import BaseModel, db
from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.objects.comment import WorkoutCommentObject
from fittrackee.federation.objects.tombstone import TombstoneObject
from fittrackee.privacy_levels import PrivacyLevel, can_view
from fittrackee.users.utils.following import get_following
from fittrackee.utils import encode_uuid

from .exceptions import CommentForbiddenException

if TYPE_CHECKING:
    from fittrackee.users.models import User


def get_comments(
    workout_id: int,
    user: Optional['User'],
    reply_to: Optional[int] = None,
) -> List['WorkoutComment']:
    if user:
        local_following_ids, remote_following_ids = get_following(user)
        comments_filter = WorkoutComment.query.filter(
            WorkoutComment.workout_id == workout_id,
            WorkoutComment.reply_to == reply_to,
            or_(
                WorkoutComment.text_visibility == PrivacyLevel.PUBLIC,
                or_(
                    WorkoutComment.user_id == user.id,
                    and_(
                        WorkoutComment.user_id.in_(local_following_ids),
                        WorkoutComment.text_visibility.in_(
                            [
                                PrivacyLevel.FOLLOWERS,
                                PrivacyLevel.FOLLOWERS_AND_REMOTE,
                            ]
                        ),
                    ),
                    and_(
                        WorkoutComment.user_id.in_(remote_following_ids),
                        WorkoutComment.text_visibility
                        == PrivacyLevel.FOLLOWERS_AND_REMOTE,
                    ),
                ),
            ),
        )
    else:
        comments_filter = WorkoutComment.query.filter(
            WorkoutComment.workout_id == workout_id,
            WorkoutComment.reply_to == reply_to,
            WorkoutComment.text_visibility == PrivacyLevel.PUBLIC,
        )
    return comments_filter.order_by(WorkoutComment.created_at.asc()).all()


class WorkoutComment(BaseModel):
    __tablename__ = 'workout_comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(
        postgresql.UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), index=True, nullable=False
    )
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id', ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    reply_to = db.Column(
        db.Integer,
        db.ForeignKey('workout_comments.id', ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modification_date = db.Column(db.DateTime, nullable=True)
    text = db.Column(db.String(), nullable=False)
    text_visibility = db.Column(
        Enum(PrivacyLevel, name='privacy_levels'),
        server_default='PRIVATE',
        nullable=False,
    )
    ap_id = db.Column(db.Text(), nullable=True)
    remote_url = db.Column(db.Text(), nullable=True)

    parent_comment = db.relationship(
        'WorkoutComment', remote_side=[id], lazy='joined'
    )

    def __repr__(self) -> str:
        return f'<WorkoutComment {self.id}>'

    def __init__(
        self,
        user_id: int,
        workout_id: int,
        workout_visibility: PrivacyLevel,
        text: str,
        text_visibility: PrivacyLevel = PrivacyLevel.PRIVATE,
        created_at: Optional[datetime.datetime] = None,
        reply_to: Optional[int] = None,
    ) -> None:
        self.user_id = user_id
        self.workout_id = workout_id
        self.text = text
        self.text_visibility = self._check_visibility(
            workout_visibility, text_visibility
        )
        self.created_at = (
            datetime.datetime.utcnow() if created_at is None else created_at
        )
        self.reply_to = reply_to

    @staticmethod
    def _check_visibility(
        workout_visibility: PrivacyLevel, text_visibility: PrivacyLevel
    ) -> PrivacyLevel:
        if (
            text_visibility == PrivacyLevel.FOLLOWERS_AND_REMOTE
            and not current_app.config['federation_enabled']
        ):
            raise InvalidVisibilityException(
                f'invalid visibility: {text_visibility},'
                f' federation is disabled.'
            )

        if (
            (
                workout_visibility == PrivacyLevel.PRIVATE
                and text_visibility != PrivacyLevel.PRIVATE
            )
            or (
                workout_visibility == PrivacyLevel.FOLLOWERS
                and text_visibility
                in [PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS_AND_REMOTE]
            )
            or (
                workout_visibility == PrivacyLevel.FOLLOWERS_AND_REMOTE
                and text_visibility == PrivacyLevel.PUBLIC
            )
        ):
            raise InvalidVisibilityException(
                f'invalid visibility: {text_visibility} '
                f'(workout visibility: {workout_visibility})'
            )
        return text_visibility

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    def handle_mentions(self) -> Tuple[str, Dict[str, Set['User']]]:
        from .utils import handle_mentions

        return handle_mentions(self.text)

    def create_mentions(self) -> Tuple[str, Dict[str, Set['User']]]:
        linkified_text, mentioned_users = self.handle_mentions()
        for user in mentioned_users["local"].union(mentioned_users["remote"]):
            mention = Mention(comment_id=self.id, user_id=user.id)
            db.session.add(mention)
            db.session.flush()
        return linkified_text, mentioned_users

    def update_mentions(self) -> None:
        from fittrackee.users.models import User

        existing_mentioned_users = set(
            db.session.query(User)
            .join(Mention, User.id == Mention.user_id)
            .all()
        )
        linkified_text, mentioned_users = self.handle_mentions()
        updated_mentioned_users = mentioned_users["local"].union(
            mentioned_users["remote"]
        )
        intersection = updated_mentioned_users.intersection(
            existing_mentioned_users
        )

        # delete removed mentions
        mentions_to_delete = {
            user.id for user in (existing_mentioned_users - intersection)
        }
        Mention.query.filter(
            Mention.comment_id == self.id,
            Mention.user_id.in_(mentions_to_delete),
        ).delete()
        db.session.flush()

        # create new mentions
        for user in updated_mentioned_users - intersection:
            mention = Mention(comment_id=self.id, user_id=user.id)
            db.session.add(mention)
            db.session.flush()

    def serialize(self, user: Optional['User'] = None) -> Dict:
        # TODO: mentions
        if not can_view(self, 'text_visibility', user):
            raise CommentForbiddenException

        return {
            'id': self.short_id,
            'user': self.user.serialize(),
            'workout_id': self.workout.short_id,
            'text': self.text,
            'text_html': self.handle_mentions()[0],
            'text_visibility': self.text_visibility,
            'created_at': self.created_at,
            'modification_date': self.modification_date,
            'reply_to': (
                self.parent_comment.short_id if self.reply_to else None
            ),
            'replies': [
                reply.serialize(user)
                for reply in get_comments(
                    workout_id=self.workout_id,
                    user=user,
                    reply_to=self.id,
                )
            ],
        }

    def get_activity(self, activity_type: str) -> Dict:
        if activity_type in ['Create', 'Update']:
            return WorkoutCommentObject(
                self, activity_type=activity_type
            ).get_activity()
        if activity_type == 'Delete':
            tombstone_object = TombstoneObject(self)
            delete_activity = tombstone_object.get_activity()
            return delete_activity
        return {}


class Mention(BaseModel):
    __tablename__ = 'mentions'

    comment_id = db.Column(
        db.Integer,
        db.ForeignKey('workout_comments.id', ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )

    def __init__(
        self,
        comment_id: int,
        user_id: int,
        created_at: Optional[datetime.datetime] = None,
    ):
        self.comment_id = comment_id
        self.user_id = user_id
        self.created_at = (
            datetime.datetime.utcnow() if created_at is None else created_at
        )
