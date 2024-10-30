import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

from flask import current_app
from sqlalchemy import and_, or_
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.types import Enum

from fittrackee import BaseModel, db
from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.objects.comment import CommentObject
from fittrackee.federation.objects.like import LikeObject
from fittrackee.federation.objects.tombstone import TombstoneObject
from fittrackee.privacy_levels import PrivacyLevel, can_view
from fittrackee.utils import encode_uuid

from .exceptions import CommentForbiddenException

if TYPE_CHECKING:
    from fittrackee.reports.models import ReportAction
    from fittrackee.users.models import User


def get_comments(
    workout_id: int, user: Optional['User'], reply_to: Optional[int] = None
) -> List['Comment']:
    if user:
        (
            local_following_ids,
            remote_following_ids,
        ) = user.get_following_user_ids()
        blocked_users = user.get_blocked_user_ids()
        blocked_by_users = user.get_blocked_by_user_ids()
        comments_filter = Comment.query.join(
            Mention, Mention.comment_id == Comment.id, isouter=True
        ).filter(
            Comment.workout_id == workout_id,
            Comment.reply_to == reply_to,
            or_(
                Comment.user_id == user.id,
                or_(
                    Mention.user_id == user.id,
                    and_(
                        Comment.text_visibility == PrivacyLevel.PUBLIC,
                        Comment.user_id.not_in(
                            blocked_users + blocked_by_users
                        ),
                    ),
                    and_(
                        Comment.user_id.in_(local_following_ids),
                        Comment.text_visibility.in_(
                            [
                                PrivacyLevel.FOLLOWERS,
                                PrivacyLevel.FOLLOWERS_AND_REMOTE,
                            ]
                        ),
                    ),
                    and_(
                        Comment.user_id.in_(remote_following_ids),
                        Comment.text_visibility
                        == PrivacyLevel.FOLLOWERS_AND_REMOTE,
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
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
        nullable=False,
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
    suspended_at = db.Column(db.DateTime, nullable=True)
    ap_id = db.Column(db.Text(), nullable=True)
    remote_url = db.Column(db.Text(), nullable=True)

    parent_comment = db.relationship(
        'Comment', remote_side=[id], lazy='joined'
    )
    mentions = db.relationship(
        "Mention",
        lazy=True,
        cascade="all, delete",
        backref=db.backref("comment", lazy="joined", single_parent=True),
    )
    mentioned_users = db.relationship(
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
        workout_id: Union[int, None],
        text: str,
        text_visibility: PrivacyLevel,
        created_at: Optional[datetime.datetime] = None,
        reply_to: Optional[int] = None,
    ) -> None:
        if (
            text_visibility == PrivacyLevel.FOLLOWERS_AND_REMOTE
            and not current_app.config['FEDERATION_ENABLED']
        ):
            raise InvalidVisibilityException(
                "invalid visibility: followers_and_remote_only, "
                "federation is disabled."
            )
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

    @property
    def suspension_action(self) -> Optional['ReportAction']:
        if self.suspended_at is None:
            return None

        from fittrackee.reports.models import ReportAction

        return (
            ReportAction.query.filter(
                ReportAction.comment_id == self.id,
                ReportAction.action_type == "comment_suspension",
            )
            .order_by(ReportAction.created_at.desc())
            .first()
        )

    @hybrid_property
    def remote_mentions(self) -> Query:
        from fittrackee.users.models import User

        return (
            db.session.query(User)
            .join(Mention, User.id == Mention.user_id)
            .filter(Mention.comment_id == self.id)
            .filter(User.is_remote == True)  # noqa
        )

    @hybrid_property
    def has_remote_mentions(self) -> bool:
        return self.remote_mentions.count() > 0

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

    def update_mentions(self) -> Set['User']:
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
        deleted_mentioned_users = existing_mentioned_users - intersection
        mentions_to_delete = {user.id for user in deleted_mentioned_users}
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

        # return users associated to deleted mention to send delete
        return deleted_mentioned_users

    def liked_by(self, user: 'User') -> bool:
        return user in self.likes.all()

    def serialize(
        self,
        user: Optional['User'] = None,
        with_replies: bool = True,
        get_parent_comment: bool = False,
        for_report: bool = False,
    ) -> Dict:
        if not can_view(self, 'text_visibility', user, for_report):
            raise CommentForbiddenException

        try:
            reply_to = (
                None
                if self.reply_to is None
                else (
                    self.parent_comment.serialize(user, with_replies=False)
                    if get_parent_comment
                    else self.parent_comment.short_id
                )
            )
        except CommentForbiddenException:
            reply_to = None

        # suspended comment content is only visible to its owner or
        # to admin in report only
        suspension: Dict[str, Any] = {}
        if self.suspended_at:
            suspension["suspended"] = True
            if user and user.id == self.user_id and self.suspension_action:
                suspension["suspension"] = self.suspension_action.serialize(
                    current_user=user, full=False
                )
        if user and (user.id == self.user_id or (user.admin and for_report)):
            suspension["suspended_at"] = self.suspended_at

        display_content = (
            False
            if (
                self.suspended_at
                and (
                    not user
                    or (user.admin and not for_report)
                    or (
                        not (user.admin and for_report)
                        and user.id != self.user_id
                    )
                )
            )
            else True
        )

        return {
            'id': self.short_id,
            'user': self.user.serialize(),
            'workout_id': (
                self.workout.short_id
                if self.workout
                and can_view(self.workout, 'workout_visibility', user)
                else None
            ),
            'text': self.text if display_content else None,
            'text_html': (
                self.handle_mentions()[0] if display_content else None
            ),
            'text_visibility': self.text_visibility,
            'created_at': self.created_at,
            'modification_date': self.modification_date,
            'mentions': (
                [
                    mentioned_user.serialize()
                    for mentioned_user in self.mentioned_users
                ]
                if display_content
                else []
            ),
            'reply_to': reply_to,
            'replies': (
                [
                    reply.serialize(user)
                    for reply in get_comments(
                        workout_id=self.workout_id,
                        user=user,
                        reply_to=self.id,
                    )
                ]
                if with_replies and not for_report
                else []
            ),
            'likes_count': self.likes.count() if display_content else 0,
            'liked': self.liked_by(user) if user else False,
            **suspension,
        }

    def get_activity(self, activity_type: str) -> Dict:
        if activity_type in ['Create', 'Update']:
            return CommentObject(
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


@listens_for(Comment, 'after_insert')
def on_comment_insert(
    mapper: Mapper, connection: Connection, new_comment: Comment
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        from fittrackee.users.models import FollowRequest, Notification
        from fittrackee.workouts.models import Workout

        # it creates notification on comment creation only when:
        # - the comment author (notification.from_user_id) is not the recipient
        #   (notification.to_user)
        # - the comment is public
        # - the recipient is mentioned (regardless comment privacy level)
        # - the recipient follows the comment author if privacy level is only
        #   followers

        create_notification = False
        if new_comment.text_visibility == PrivacyLevel.PUBLIC:
            create_notification = True

        workout = Workout.query.filter_by(id=new_comment.workout_id).first()
        if not workout:
            return

        if new_comment.reply_to is None:
            to_user_id = workout.user_id
        else:
            comment = Comment.query.filter_by(id=new_comment.reply_to).first()
            to_user_id = comment.user_id

        if new_comment.user_id == to_user_id:
            return

        if not create_notification:
            user_is_mentioned = Mention.query.filter_by(
                comment_id=new_comment.id, user_id=to_user_id
            ).first()

            if user_is_mentioned:
                create_notification = True
            elif PrivacyLevel.FOLLOWERS:
                create_notification = (
                    FollowRequest.query.filter_by(
                        follower_user_id=to_user_id,
                        followed_user_id=new_comment.user_id,
                    ).first()
                    is not None
                )

        if not create_notification:
            return

        notification = Notification(
            from_user_id=new_comment.user_id,
            to_user_id=to_user_id,
            created_at=new_comment.created_at,
            event_type=(
                'workout_comment'
                if new_comment.reply_to is None
                else 'comment_reply'
            ),
            event_object_id=new_comment.id,
        )
        session.add(notification)


@listens_for(Comment, 'after_delete')
def on_comment_delete(
    mapper: Mapper, connection: Connection, old_comment: Comment
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        from fittrackee.users.models import Notification

        # delete all notifications related to deleted comment
        Notification.query.filter_by(
            event_object_id=old_comment.id,
        ).delete()


@listens_for(Mention, 'after_insert')
def on_mention_insert(
    mapper: Mapper, connection: Connection, new_mention: Mention
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        from fittrackee.users.models import Notification
        from fittrackee.workouts.models import Workout

        comment = Comment.query.filter_by(id=new_mention.comment_id).first()
        if new_mention.user_id == comment.user_id:
            return

        # `mention` notification is not created:
        # - when mentioned user is workout owner
        # (`workout_comment' notification already exists)
        workout = Workout.query.filter_by(id=comment.workout_id).first()
        if workout and workout.user_id == new_mention.user_id:
            return

        # - when mentioned user is parent comment owner
        # (`comment_reply' notification already exists)
        if comment.reply_to:
            parent_comment = Comment.query.filter_by(
                id=comment.reply_to
            ).first()
            if (
                parent_comment
                and parent_comment.user_id == new_mention.user_id
            ):
                return

        notification = Notification(
            from_user_id=comment.user_id,
            to_user_id=new_mention.user_id,
            created_at=new_mention.created_at,
            event_type='mention',
            event_object_id=comment.id,
        )
        session.add(notification)


@listens_for(Mention, 'after_delete')
def on_mention_delete(
    mapper: Mapper, connection: Connection, old_mention: Mention
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        from fittrackee.users.models import Notification

        Notification.query.filter_by(
            to_user_id=old_mention.user_id,
            event_type='mention',
            event_object_id=old_mention.comment_id,
        ).delete()


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
        db.ForeignKey('users.id', ondelete='CASCADE'),
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

    def get_activity(self, is_undo: bool = False) -> Dict:
        return LikeObject(
            actor_ap_id=self.user.actor.activitypub_id,
            target_object_ap_id=self.comment.ap_id,
            like_id=self.id,
            is_undo=is_undo,
        ).get_activity()


@listens_for(CommentLike, 'after_insert')
def on_comment_like_insert(
    mapper: Mapper, connection: Connection, new_comment_like: CommentLike
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        from fittrackee.users.models import Notification

        comment = Comment.query.filter_by(
            id=new_comment_like.comment_id
        ).first()
        if new_comment_like.user_id != comment.user_id:
            notification = Notification(
                from_user_id=new_comment_like.user_id,
                to_user_id=comment.user_id,
                created_at=new_comment_like.created_at,
                event_type='comment_like',
                event_object_id=comment.id,
            )
            session.add(notification)


@listens_for(CommentLike, 'after_delete')
def on_comment_like_delete(
    mapper: Mapper, connection: Connection, old_comment_like: CommentLike
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        from fittrackee.users.models import Notification

        comment = Comment.query.filter_by(
            id=old_comment_like.comment_id
        ).first()
        Notification.query.filter_by(
            from_user_id=old_comment_like.user_id,
            to_user_id=comment.user_id,
            event_type='comment_like',
            event_object_id=comment.id,
        ).delete()
