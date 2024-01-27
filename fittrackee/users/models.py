import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import jwt
from flask import current_app
from sqlalchemy import and_, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session, object_session
from sqlalchemy.sql.expression import select
from sqlalchemy.types import Enum

from fittrackee import BaseModel, appLog, bcrypt, db
from fittrackee.comments.models import Comment
from fittrackee.files import get_absolute_file_path
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.workouts.models import Workout

from .exceptions import (
    BlockUserException,
    FollowRequestAlreadyProcessedError,
    FollowRequestAlreadyRejectedError,
    InvalidNotificationTypeException,
    NotExistingFollowRequestError,
)
from .roles import UserRole
from .utils.token import decode_user_token, get_user_token

if TYPE_CHECKING:
    from fittrackee.administration.models import AdminAction

USER_LINK_TEMPLATE = (
    '<a href="{profile_url}" target="_blank" rel="noopener noreferrer">'
    '{username}</a>'
)

NOTIFICATION_TYPES = [
    'comment_like',
    'comment_reply',
    'follow',
    'follow_request',
    'mention',
    'report',
    'workout_comment',
    'workout_like',
]


class FollowRequest(BaseModel):
    """Follow request between two users"""

    __tablename__ = 'follow_requests'
    follower_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True,
    )
    followed_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True,
    )
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return (
            f'<FollowRequest from user \'{self.follower_user_id}\' '
            f'to user \'{self.followed_user_id}\'>'
        )

    def __init__(self, follower_user_id: int, followed_user_id: int):
        self.follower_user_id = follower_user_id
        self.followed_user_id = followed_user_id

    def is_rejected(self) -> bool:
        return not self.is_approved and self.updated_at is not None

    def serialize(self) -> Dict:
        return {
            'from_user': self.from_user.serialize(),
            'to_user': self.to_user.serialize(),
        }


@listens_for(FollowRequest, 'after_insert')
def on_follow_request_insert(
    mapper: Mapper, connection: Connection, new_follow_request: FollowRequest
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        notification = Notification(
            from_user_id=new_follow_request.follower_user_id,
            to_user_id=new_follow_request.followed_user_id,
            created_at=new_follow_request.created_at,
            event_type=(
                'follow'
                if new_follow_request.is_approved
                else 'follow_request'
            ),
        )
        session.add(notification)


@listens_for(FollowRequest, 'after_update')
def on_follow_request_update(
    mapper: Mapper, connection: Connection, follow_request: FollowRequest
) -> None:
    if object_session(follow_request).is_modified(follow_request):

        @listens_for(db.Session, 'after_flush', once=True)
        def receive_after_flush(session: Session, context: Connection) -> None:
            if follow_request.is_approved:
                notification_table = Notification.__table__
                connection.execute(
                    notification_table.update()
                    .where(
                        notification_table.c.from_user_id
                        == follow_request.follower_user_id,
                        notification_table.c.to_user_id
                        == follow_request.followed_user_id,
                        notification_table.c.event_type == 'follow_request',
                    )
                    .values(
                        event_type='follow',
                        marked_as_read=False,
                    )
                )
            if (
                not follow_request.is_approved
                and follow_request.updated_at is not None
            ):
                Notification.query.filter_by(
                    from_user_id=follow_request.follower_user_id,
                    to_user_id=follow_request.followed_user_id,
                    event_type='follow_request',
                ).delete()


@listens_for(FollowRequest, 'after_delete')
def on_follow_request_delete(
    mapper: Mapper, connection: Connection, old_follow_request: FollowRequest
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        Notification.query.filter(
            Notification.from_user_id == old_follow_request.follower_user_id,
            Notification.to_user_id == old_follow_request.followed_user_id,
            Notification.event_type.in_(['follow', 'follow_request']),
        ).delete()


class BlockedUser(BaseModel):
    __tablename__ = 'blocked_users'
    __table_args__ = (
        db.UniqueConstraint(
            'user_id', 'by_user_id', name='blocked_users_unique'
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
    )
    by_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
    )
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self,
        user_id: int,
        by_user_id: int,
        created_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.by_user_id = by_user_id
        self.created_at = (
            datetime.utcnow() if created_at is None else created_at
        )


class User(BaseModel):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    birth_date = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(80), nullable=True)
    bio = db.Column(db.String(200), nullable=True)
    picture = db.Column(db.String(255), nullable=True)
    timezone = db.Column(db.String(50), nullable=True)
    date_format = db.Column(db.String(50), nullable=True)
    # weekm: does the week start Monday?
    weekm = db.Column(db.Boolean, default=False, nullable=False)
    language = db.Column(db.String(50), nullable=True)
    imperial_units = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    email_to_confirm = db.Column(db.String(255), nullable=True)
    confirmation_token = db.Column(db.String(255), nullable=True)
    display_ascent = db.Column(db.Boolean, default=True, nullable=False)
    accepted_policy_date = db.Column(db.DateTime, nullable=True)
    start_elevation_at_zero = db.Column(
        db.Boolean, default=True, nullable=False
    )
    use_raw_gpx_speed = db.Column(db.Boolean, default=False, nullable=False)
    use_dark_mode = db.Column(db.Boolean, default=False, nullable=True)
    manually_approves_followers = db.Column(
        db.Boolean, default=True, nullable=False
    )
    hide_profile_in_users_directory = db.Column(
        db.Boolean, default=True, nullable=False
    )
    workouts_visibility = db.Column(
        Enum(PrivacyLevel, name='privacy_levels'),
        server_default='PRIVATE',
        nullable=False,
    )
    map_visibility = db.Column(
        Enum(PrivacyLevel, name='privacy_levels'),
        server_default='PRIVATE',
        nullable=False,
    )
    suspended_at = db.Column(db.DateTime, nullable=True)

    workouts = db.relationship(
        'Workout',
        lazy=True,
        backref=db.backref('user', lazy='joined', single_parent=True),
    )
    records = db.relationship(
        'Record',
        lazy=True,
        backref=db.backref('user', lazy='joined', single_parent=True),
    )
    received_follow_requests = db.relationship(
        FollowRequest,
        backref='to_user',
        primaryjoin=id == FollowRequest.followed_user_id,
        lazy='dynamic',
        cascade='all, delete-orphan',
    )
    sent_follow_requests = db.relationship(
        FollowRequest,
        backref='from_user',
        primaryjoin=id == FollowRequest.follower_user_id,
        lazy='dynamic',
        cascade='all, delete-orphan',
    )
    followers = db.relationship(
        'User',
        secondary='follow_requests',
        primaryjoin=and_(
            id == FollowRequest.followed_user_id,
            FollowRequest.is_approved == True,  # noqa
        ),
        secondaryjoin=and_(
            id == FollowRequest.follower_user_id,
            suspended_at == None,  # noqa
        ),
        lazy='dynamic',
        viewonly=True,
    )
    following = db.relationship(
        'User',
        secondary='follow_requests',
        primaryjoin=and_(
            id == FollowRequest.follower_user_id,
            FollowRequest.is_approved == True,  # noqa
        ),
        secondaryjoin=and_(
            id == FollowRequest.followed_user_id,
            suspended_at == None,  # noqa
        ),
        lazy='dynamic',
        viewonly=True,
    )
    comments = db.relationship(
        'Comment',
        lazy=True,
        backref=db.backref(
            'user',
            lazy='joined',
            single_parent=True,
        ),
        cascade='all, delete-orphan',
    )
    blocked_users = db.relationship(
        'BlockedUser',
        primaryjoin=id == BlockedUser.by_user_id,
        lazy='dynamic',
        viewonly=True,
    )
    blocked_by_users = db.relationship(
        'BlockedUser',
        primaryjoin=id == BlockedUser.user_id,
        lazy='dynamic',
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f'<User {self.username!r}>'

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.created_at = (
            datetime.utcnow() if created_at is None else created_at
        )

    @staticmethod
    def encode_auth_token(user_id: int) -> str:
        """
        Generates the auth token
        :param user_id: -
        :return: JWToken
        """
        return get_user_token(user_id)

    @staticmethod
    def encode_password_reset_token(user_id: int) -> str:
        """
        Generates the auth token
        :param user_id: -
        :return: JWToken
        """
        return get_user_token(user_id, password_reset=True)

    @staticmethod
    def decode_auth_token(auth_token: str) -> Union[int, str]:
        """
        Decodes the auth token
        :param auth_token: -
        :return: integer|string
        """
        try:
            resp = decode_user_token(auth_token)
            is_blacklisted = BlacklistedToken.check(auth_token)
            if is_blacklisted:
                return 'blacklisted token, please log in again'
            return resp
        except jwt.ExpiredSignatureError:
            return 'signature expired, please log in again'
        except jwt.InvalidTokenError:
            return 'invalid token, please log in again'

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def generate_password_hash(new_password: str) -> str:
        return bcrypt.generate_password_hash(
            new_password, current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def get_user_id(self) -> int:
        return self.id

    @hybrid_property
    def workouts_count(self) -> int:
        return Workout.query.filter(Workout.user_id == self.id).count()

    @workouts_count.expression  # type: ignore
    def workouts_count(self) -> int:
        return (
            select([func.count(Workout.id)])
            .where(Workout.user_id == self.id)
            .label('workouts_count')
        )

    @property
    def pending_follow_requests(self) -> FollowRequest:
        return self.received_follow_requests.filter_by(updated_at=None).all()

    def send_follow_request_to(self, target: 'User') -> FollowRequest:
        existing_follow_request = FollowRequest.query.filter_by(
            follower_user_id=self.id, followed_user_id=target.id
        ).first()
        if existing_follow_request:
            if existing_follow_request.is_rejected():
                raise FollowRequestAlreadyRejectedError()
            return existing_follow_request

        follow_request = FollowRequest(
            follower_user_id=self.id, followed_user_id=target.id
        )
        db.session.add(follow_request)
        if not target.manually_approves_followers:
            follow_request.is_approved = True
            follow_request.updated_at = datetime.utcnow()
        db.session.commit()

        return follow_request

    def unfollows(self, target: 'User') -> None:
        existing_follow_request = FollowRequest.query.filter_by(
            follower_user_id=self.id, followed_user_id=target.id
        ).first()
        if not existing_follow_request:
            raise NotExistingFollowRequestError()

        db.session.delete(existing_follow_request)
        db.session.commit()
        return None

    def undoes_follow(self, follower: 'User') -> None:
        existing_follow_request = FollowRequest.query.filter_by(
            followed_user_id=self.id, follower_user_id=follower.id
        ).first()
        if not existing_follow_request:
            raise NotExistingFollowRequestError()
        db.session.delete(existing_follow_request)
        db.session.commit()
        return None

    def _processes_follow_request_from(
        self, user: 'User', approved: bool
    ) -> FollowRequest:
        follow_request = FollowRequest.query.filter_by(
            follower_user_id=user.id, followed_user_id=self.id
        ).first()
        if not follow_request:
            raise NotExistingFollowRequestError()
        if follow_request.updated_at is not None:
            raise FollowRequestAlreadyProcessedError()
        follow_request.is_approved = approved
        follow_request.updated_at = datetime.now()
        db.session.commit()
        return follow_request

    def approves_follow_request_from(self, user: 'User') -> FollowRequest:
        follow_request = self._processes_follow_request_from(
            user=user, approved=True
        )
        return follow_request

    def rejects_follow_request_from(self, user: 'User') -> FollowRequest:
        follow_request = self._processes_follow_request_from(
            user=user, approved=False
        )
        return follow_request

    @staticmethod
    def follow_request_status(follow_request: FollowRequest) -> str:
        if follow_request is None:
            return 'false'
        if follow_request.is_approved:
            return 'true'
        return 'pending'

    def is_followed_by(self, user: 'User') -> str:
        follow_request = FollowRequest.query.filter_by(
            follower_user_id=user.id, followed_user_id=self.id
        ).first()
        return self.follow_request_status(follow_request)

    def follows(self, user: 'User') -> str:
        follow_request = FollowRequest.query.filter_by(
            follower_user_id=self.id, followed_user_id=user.id
        ).first()
        return self.follow_request_status(follow_request)

    def get_following_user_ids(self) -> List:
        return [following.id for following in self.following]

    def get_user_url(self) -> str:
        """Return user url on user interface"""
        return f"{current_app.config['UI_URL']}/users/{self.username}"

    def linkify_mention(self) -> str:
        return USER_LINK_TEMPLATE.format(
            profile_url=self.get_user_url(), username=f"@{self.username}"
        )

    def blocks_user(self, user: 'User') -> None:
        if self.id == user.id:
            raise BlockUserException()

        db.session.execute(
            insert(BlockedUser)
            .values(
                user_id=user.id,
                by_user_id=self.id,
                created_at=datetime.utcnow(),
            )
            .on_conflict_do_nothing()
        )
        follow_request = FollowRequest.query.filter_by(
            follower_user_id=user.id,
            followed_user_id=self.id,
        ).first()
        if follow_request:
            db.session.delete(follow_request)
        db.session.commit()

    def unblocks_user(self, user: 'User') -> None:
        BlockedUser.query.filter_by(
            user_id=user.id, by_user_id=self.id
        ).delete()
        db.session.commit()

    def is_blocked_by(self, user: 'User') -> bool:
        return (
            BlockedUser.query.filter_by(
                user_id=self.id, by_user_id=user.id
            ).first()
            is not None
        )

    def get_blocked_user_ids(self) -> List:
        return [
            blocked_user.user_id for blocked_user in self.blocked_users.all()
        ]

    def get_blocked_by_user_ids(self) -> List:
        return [
            blocked_user.by_user_id
            for blocked_user in self.blocked_by_users.all()
        ]

    @property
    def suspension_action(self) -> Optional['AdminAction']:
        if self.suspended_at is None:
            return None

        from fittrackee.administration.models import AdminAction

        return (
            AdminAction.query.filter(
                AdminAction.user_id == self.id,
                AdminAction.action_type == "user_suspension",
            )
            .order_by(AdminAction.created_at.desc())
            .first()
        )

    def serialize(self, current_user: Optional['User'] = None) -> Dict:
        if current_user is None:
            role = None
        else:
            role = (
                UserRole.AUTH_USER
                if current_user.id == self.id
                else UserRole.ADMIN
                if current_user.admin
                else UserRole.USER
            )
        sports = []
        if self.workouts_count > 0:  # type: ignore
            sports = (
                db.session.query(Workout.sport_id)
                .filter(Workout.user_id == self.id)
                .group_by(Workout.sport_id)
                .order_by(Workout.sport_id)
                .all()
            )

        serialized_user = {
            'admin': self.admin,
            'bio': self.bio,
            'birth_date': self.birth_date,
            'created_at': self.created_at,
            'first_name': self.first_name,
            'followers': self.followers.count(),
            'following': self.following.count(),
            'is_active': self.is_active,
            'last_name': self.last_name,
            'location': self.location,
            'nb_workouts': self.workouts_count,
            'picture': self.picture is not None,
            'suspended_at': self.suspended_at,
            'username': self.username,
        }

        if role is not None:
            total = (0, '0:00:00', 0)
            if self.workouts_count > 0:  # type: ignore
                total = (
                    db.session.query(
                        func.sum(Workout.distance),
                        func.sum(Workout.duration),
                        func.sum(Workout.ascent),
                    )
                    .filter(Workout.user_id == self.id)
                    .first()
                )

            serialized_user['nb_sports'] = len(sports)
            serialized_user['records'] = [
                record.serialize() for record in self.records
            ]
            serialized_user['sports_list'] = [
                sport for sportslist in sports for sport in sportslist
            ]
            serialized_user['total_ascent'] = (
                float(total[2]) if total[2] else 0.0
            )
            serialized_user['total_distance'] = float(total[0])
            serialized_user['total_duration'] = str(total[1])

        if role in [UserRole.AUTH_USER, UserRole.ADMIN]:
            serialized_user['email'] = self.email
            serialized_user['email_to_confirm'] = self.email_to_confirm

        if role == UserRole.AUTH_USER:
            accepted_privacy_policy = False
            if self.accepted_policy_date:
                accepted_privacy_policy = (
                    True
                    if current_app.config['privacy_policy_date'] is None
                    else current_app.config['privacy_policy_date']
                    < self.accepted_policy_date
                )
            serialized_user = {
                **serialized_user,
                **{
                    'accepted_privacy_policy': accepted_privacy_policy,
                    'date_format': self.date_format,
                    'display_ascent': self.display_ascent,
                    'imperial_units': self.imperial_units,
                    'language': self.language,
                    'start_elevation_at_zero': self.start_elevation_at_zero,
                    'timezone': self.timezone,
                    'use_dark_mode': self.use_dark_mode,
                    'use_raw_gpx_speed': self.use_raw_gpx_speed,
                    'weekm': self.weekm,
                    'map_visibility': self.map_visibility.value,
                    'workouts_visibility': self.workouts_visibility.value,
                    'manually_approves_followers': (
                        self.manually_approves_followers
                    ),
                    'hide_profile_in_users_directory': (
                        self.hide_profile_in_users_directory
                    ),
                },
            }

        if current_user is not None and role != UserRole.AUTH_USER:
            serialized_user['follows'] = self.follows(current_user)
            serialized_user['is_followed_by'] = self.is_followed_by(
                current_user
            )
            serialized_user['blocked'] = self.is_blocked_by(current_user)

        return serialized_user


class UserSportPreference(BaseModel):
    __tablename__ = 'users_sports_preferences'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True,
    )
    sport_id = db.Column(
        db.Integer,
        db.ForeignKey('sports.id'),
        primary_key=True,
    )
    color = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    stopped_speed_threshold = db.Column(db.Float, default=1.0, nullable=False)

    def __init__(
        self,
        user_id: int,
        sport_id: int,
        stopped_speed_threshold: float,
    ) -> None:
        self.user_id = user_id
        self.sport_id = sport_id
        self.is_active = True
        self.stopped_speed_threshold = stopped_speed_threshold

    def serialize(self) -> Dict:
        return {
            'user_id': self.user_id,
            'sport_id': self.sport_id,
            'color': self.color,
            'is_active': self.is_active,
            'stopped_speed_threshold': self.stopped_speed_threshold,
        }


class BlacklistedToken(BaseModel):
    __tablename__ = 'blacklisted_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    expired_at = db.Column(db.Integer, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(
        self, token: str, blacklisted_on: Optional[datetime] = None
    ) -> None:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256'],
        )
        self.token = token
        self.expired_at = payload['exp']
        self.blacklisted_on = (
            blacklisted_on if blacklisted_on else datetime.utcnow()
        )

    @classmethod
    def check(cls, auth_token: str) -> bool:
        return cls.query.filter_by(token=str(auth_token)).first() is not None


class UserDataExport(BaseModel):
    __tablename__ = 'users_data_export'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
        unique=True,
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime, nullable=True, onupdate=datetime.utcnow
    )
    completed = db.Column(db.Boolean, nullable=False, default=False)
    file_name = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)

    def __init__(
        self,
        user_id: int,
        created_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.created_at = (
            datetime.utcnow() if created_at is None else created_at
        )

    def serialize(self) -> Dict:
        if self.completed:
            status = "successful" if self.file_name else "errored"
        else:
            status = "in_progress"
        return {
            "created_at": self.created_at,
            "status": status,
            "file_name": self.file_name if status == "successful" else None,
            "file_size": self.file_size if status == "successful" else None,
        }


@listens_for(UserDataExport, 'after_delete')
def on_users_data_export_delete(
    mapper: Mapper, connection: Connection, old_record: 'UserDataExport'
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        if old_record.file_name:
            try:
                file_path = (
                    f"exports/{old_record.user_id}/{old_record.file_name}"
                )
                os.remove(get_absolute_file_path(file_path))
            except OSError:
                appLog.error('archive found when deleting export request')


class Notification(BaseModel):
    __tablename__ = 'notifications'
    __table_args__ = (
        db.UniqueConstraint(
            'from_user_id',
            'to_user_id',
            'event_type',
            'event_object_id',
            name='users_event_unique',
        ),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
    )
    to_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
    )
    created_at = db.Column(db.DateTime, nullable=False)
    marked_as_read = db.Column(db.Boolean, nullable=False, default=False)
    event_object_id = db.Column(db.Integer, nullable=True)
    event_type = db.Column(db.String(50), nullable=False)

    def __init__(
        self,
        from_user_id: int,
        to_user_id: int,
        created_at: datetime,
        event_type: str,
        event_object_id: Optional[int] = None,
    ):
        if event_type not in NOTIFICATION_TYPES:
            raise InvalidNotificationTypeException()
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.created_at = created_at
        self.event_type = event_type
        self.event_object_id = event_object_id

    def serialize(self) -> Dict:
        serialized_notification = {
            "created_at": self.created_at,
            "id": self.id,
            "marked_as_read": self.marked_as_read,
            "type": self.event_type,
        }

        if self.event_type in ["follow", "follow_request"]:
            follow_request = FollowRequest.query.filter_by(
                follower_user_id=self.from_user_id,
                followed_user_id=self.to_user_id,
            ).first()
            from_user = follow_request.from_user
            to_user = follow_request.to_user
            return {
                **serialized_notification,
                "from": {
                    **from_user.serialize(),
                    "follows": from_user.follows(to_user),
                    "is_followed_by": from_user.is_followed_by(to_user),
                },
            }

        from_user = User.query.filter_by(id=self.from_user_id).first()
        to_user = User.query.filter_by(id=self.to_user_id).first()
        serialized_notification = {
            **serialized_notification,
            "from": from_user.serialize(current_user=to_user),
        }

        if self.event_type == "workout_like":
            workout = Workout.query.filter_by(id=self.event_object_id).first()
            serialized_notification["workout"] = workout.serialize(
                user=to_user
            )

        if self.event_type in [
            "comment_like",
            "comment_reply",
            "mention",
            "workout_comment",
        ]:
            comment = Comment.query.filter_by(id=self.event_object_id).first()
            serialized_notification["comment"] = comment.serialize(
                user=to_user
            )

        if self.event_type == "report":
            from fittrackee.reports.models import Report

            report = Report.query.filter_by(id=self.event_object_id).first()
            serialized_notification["report"] = report.serialize(
                current_user=to_user
            )

        return serialized_notification
