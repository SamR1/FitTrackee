import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from sqlalchemy import and_, or_
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import Enum

from fittrackee import BaseModel, db
from fittrackee.privacy_levels import PrivacyLevel, can_view
from fittrackee.users.utils.following import get_following
from fittrackee.utils import encode_uuid

from .exceptions import CommentForbiddenException

if TYPE_CHECKING:
    from fittrackee.users.models import User


def get_comments(
    workout_id: int, user: Optional['User'], reply_to: Optional[int] = None
) -> List['Comment']:
    if user:
        following_ids = get_following(user)
        comments_filter = Comment.query.join(
            Mention, Mention.comment_id == Comment.id, isouter=True
        ).filter(
            Comment.workout_id == workout_id,
            Comment.reply_to == reply_to,
            or_(
                Comment.text_visibility == PrivacyLevel.PUBLIC,
                or_(user.id == Mention.user_id),
                or_(
                    Comment.user_id == user.id,
                    and_(
                        Comment.user_id.in_(following_ids),
                        Comment.text_visibility == PrivacyLevel.FOLLOWERS,
                    ),
                ),
            ),
        )
    else:
        comments_filter = Comment.query.filter(
            Comment.workout_id == workout_id,
            Comment.reply_to == reply_to,
            Comment.text_visibility == PrivacyLevel.PUBLIC,
        )
    return comments_filter.order_by(Comment.created_at.asc()).all()


class Comment(BaseModel):
    __tablename__ = 'comments'
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
        db.ForeignKey('comments.id', ondelete="SET NULL"),
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

    parent_comment = db.relationship(
        'Comment', remote_side=[id], lazy='joined'
    )
    mentions = db.relationship(
        "User",
        secondary="mentions",
        primaryjoin="Comment.id == Mention.comment_id",
        secondaryjoin="Mention.user_id == User.id",
        lazy="dynamic",
        viewonly=True,
    )
    likes = db.relationship(
        "User",
        secondary="comment_likes",
        primaryjoin="Comment.id == CommentLike.comment_id",
        secondaryjoin="CommentLike.user_id == User.id",
        lazy="dynamic",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f'<Comment {self.id}>'

    def __init__(
        self,
        user_id: int,
        workout_id: int,
        text: str,
        text_visibility: PrivacyLevel,
        created_at: Optional[datetime.datetime] = None,
        reply_to: Optional[int] = None,
    ) -> None:
        self.user_id = user_id
        self.workout_id = workout_id
        self.text = text
        self.text_visibility = text_visibility
        self.created_at = (
            datetime.datetime.utcnow() if created_at is None else created_at
        )
        self.reply_to = reply_to

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    def handle_mentions(self) -> Tuple[str, Set['User']]:
        from .utils import handle_mentions

        return handle_mentions(self.text)

    def create_mentions(self) -> Tuple[str, Set['User']]:
        linkified_text, mentioned_users = self.handle_mentions()
        for user in mentioned_users:
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
        linkified_text, updated_mentioned_users = self.handle_mentions()
        unchanged_mentions = updated_mentioned_users.intersection(
            existing_mentioned_users
        )

        # delete removed mentions
        deleted_mentioned_users = existing_mentioned_users - unchanged_mentions
        mentions_to_delete = {user.id for user in deleted_mentioned_users}
        Mention.query.filter(
            Mention.comment_id == self.id,
            Mention.user_id.in_(mentions_to_delete),
        ).delete()
        db.session.flush()

        # create new mentions
        for user in updated_mentioned_users - unchanged_mentions:
            mention = Mention(comment_id=self.id, user_id=user.id)
            db.session.add(mention)
        db.session.flush()

    def liked_by(self, user: 'User') -> bool:
        return user in self.likes.all()

    def serialize(self, user: Optional['User'] = None) -> Dict:
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
            'likes_count': self.likes.count(),
            'liked': self.liked_by(user) if user else False,
        }


class Mention(BaseModel):
    __tablename__ = 'mentions'

    comment_id = db.Column(
        db.Integer,
        db.ForeignKey('comments.id', ondelete="CASCADE"),
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


class CommentLike(BaseModel):
    __tablename__ = 'comment_likes'
    __table_args__ = (
        db.UniqueConstraint(
            'user_id', 'comment_id', name='user_id_comment_id_unique'
        ),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )
    comment_id = db.Column(
        db.Integer,
        db.ForeignKey('comments.id', ondelete="CASCADE"),
        nullable=False,
    )

    user = db.relationship("User", lazy=True)
    comment = db.relationship("Comment", lazy=True)

    def __init__(
        self,
        user_id: int,
        comment_id: int,
        created_at: Optional[datetime.datetime] = None,
    ) -> None:
        self.user_id = user_id
        self.comment_id = comment_id
        self.created_at = (
            datetime.datetime.utcnow() if created_at is None else created_at
        )
