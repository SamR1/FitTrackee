from datetime import datetime
from typing import Dict, Optional, Union

import jwt
from flask import current_app
from sqlalchemy import and_, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import select
from sqlalchemy.types import Enum

from fittrackee import BaseModel, bcrypt, db
from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.enums import ActivityType
from fittrackee.federation.exceptions import FederationDisabledException
from fittrackee.federation.models import Actor, Domain
from fittrackee.federation.tasks.user_inbox import send_to_users_inbox
from fittrackee.workouts.models import Workout

from .exceptions import (
    FollowRequestAlreadyProcessedError,
    FollowRequestAlreadyRejectedError,
    NotExistingFollowRequestError,
)
from .privacy_levels import PrivacyLevel
from .roles import UserRole
from .utils.token import decode_user_token, get_user_token


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
        if current_app.config['federation_enabled']:
            return {
                'from_user': self.from_user.actor.serialize(),
                'to_user': self.to_user.actor.serialize(),
            }
        return {
            'from_user': self.from_user.serialize(),
            'to_user': self.to_user.serialize(),
        }

    def get_activity(self) -> Dict:
        if not current_app.config['federation_enabled']:
            raise FederationDisabledException()
        follow_activity = {
            'id': (
                f'{self.from_user.actor.activitypub_id}#follows/'
                f'{self.to_user.actor.fullname}'
            ),
            'type': ActivityType.FOLLOW.value,
            'actor': self.from_user.actor.activitypub_id,
            'object': self.to_user.actor.activitypub_id,
        }
        if self.updated_at is None:
            activity = follow_activity.copy()
        else:
            activity = {
                'id': (
                    f'{self.to_user.actor.activitypub_id}#'
                    f'{"accept" if self.is_approved else "reject"}s/'
                    f'follow/{self.from_user.actor.fullname}'
                ),
                'type': (
                    ActivityType.ACCEPT.value
                    if self.is_approved
                    else ActivityType.REJECT.value
                ),
                'actor': self.to_user.actor.activitypub_id,
                'object': follow_activity,
            }
        activity['@context'] = AP_CTX
        return activity


class User(BaseModel):
    __tablename__ = 'users'
    __table_args__ = (
        db.UniqueConstraint(
            'username', 'actor_id', name='username_actor_id_unique'
        ),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actor_id = db.Column(
        db.Integer, db.ForeignKey('actors.id'), unique=True, nullable=True
    )
    username = db.Column(db.String(50), nullable=False)
    # Note: Null values are not considered equal
    # source: https://www.postgresql.org/docs/current/indexes-unique.html
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    birth_date = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(80), nullable=True)
    bio = db.Column(db.String(200), nullable=True)
    picture = db.Column(db.String(255), nullable=True)
    timezone = db.Column(db.String(50), nullable=True)
    # weekm: does the week start Monday?
    weekm = db.Column(db.Boolean(50), default=False, nullable=False)
    language = db.Column(db.String(50), nullable=True)
    imperial_units = db.Column(db.Boolean, default=False, nullable=False)
    manually_approves_followers = db.Column(
        db.Boolean, default=True, nullable=False
    )
    is_remote = db.Column(db.Boolean, default=False, nullable=False)
    workouts_visibility = db.Column(
        Enum(PrivacyLevel, name='privacy_levels'), server_default='PRIVATE'
    )
    map_visibility = db.Column(
        Enum(PrivacyLevel, name='privacy_levels'), server_default='PRIVATE'
    )

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
    actor = db.relationship(Actor, back_populates='user')
    received_follow_requests = db.relationship(
        FollowRequest,
        backref='to_user',
        primaryjoin=id == FollowRequest.followed_user_id,
        lazy='dynamic',
    )
    sent_follow_requests = db.relationship(
        FollowRequest,
        backref='from_user',
        primaryjoin=id == FollowRequest.follower_user_id,
        lazy='dynamic',
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
        ),
        lazy='dynamic',
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f'<User {self.username!r}>'

    def __init__(
        self,
        username: str,
        email: Optional[str],
        password: Optional[str],
        created_at: Optional[datetime] = datetime.utcnow(),
        is_remote: bool = False,
    ) -> None:
        self.username = username
        self.email = email  # email is None for remote actor
        self.password = (
            bcrypt.generate_password_hash(
                password, current_app.config.get('BCRYPT_LOG_ROUNDS')
            ).decode()
            if email
            else None  # no password for remote actor
        )
        self.created_at = created_at
        self.is_remote = is_remote

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
            return decode_user_token(auth_token)
        except jwt.ExpiredSignatureError:
            return 'signature expired, please log in again'
        except jwt.InvalidTokenError:
            return 'invalid token, please log in again'

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

        if current_app.config['federation_enabled']:
            # send Follow activity to remote followed user
            if target.actor.is_remote:
                send_to_users_inbox.send(
                    sender_id=self.actor.id,
                    activity=follow_request.get_activity(),
                    recipients=[target.actor.inbox_url],
                )

            # send Accept activity to remote follower user if local followed
            # user accepts follow requests automatically
            if self.actor.is_remote and not target.manually_approves_followers:
                send_to_users_inbox.send(
                    sender_id=target.actor.id,
                    activity=follow_request.get_activity(),
                    recipients=[self.actor.inbox_url],
                )

        return follow_request

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

        if current_app.config['federation_enabled'] and user.actor.is_remote:
            send_to_users_inbox.send(
                sender_id=self.actor.id,
                activity=follow_request.get_activity(),
                recipients=[user.actor.inbox_url],
            )

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
        if follow_request is None or (
            follow_request.updated_at and not follow_request.is_approved
        ):
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

    def get_user_url(self) -> str:
        """Return user url on user interface"""
        return f"{current_app.config['UI_URL']}/users/{self.username}"

    def create_actor(self) -> None:
        app_domain = Domain.query.filter_by(
            name=current_app.config['AP_DOMAIN']
        ).first()
        actor = Actor(
            preferred_username=self.username, domain_id=app_domain.id
        )
        db.session.add(actor)
        db.session.flush()
        self.actor_id = actor.id
        db.session.commit()

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
            'is_remote': self.is_remote,
            'last_name': self.last_name,
            'location': self.location,
            'map_visibility': self.map_visibility.value,
            'nb_workouts': self.workouts_count,
            'picture': self.picture is not None,
            'workouts_visibility': self.workouts_visibility.value,
            'username': self.username,
        }

        if role is not None:
            total = (0, '0:00:00')
            if self.workouts_count > 0:  # type: ignore
                total = (
                    db.session.query(
                        func.sum(Workout.distance), func.sum(Workout.duration)
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
            serialized_user['total_distance'] = float(total[0])
            serialized_user['total_duration'] = str(total[1])

        if role in [UserRole.AUTH_USER, UserRole.ADMIN]:
            serialized_user['email'] = self.email

        if role == UserRole.AUTH_USER:
            serialized_user = {
                **serialized_user,
                **{
                    'imperial_units': self.imperial_units,
                    'language': self.language,
                    'timezone': self.timezone,
                    'weekm': self.weekm,
                },
            }

        if current_user is not None and role != UserRole.AUTH_USER:
            serialized_user['follows'] = self.follows(current_user)
            serialized_user['is_followed_by'] = self.is_followed_by(
                current_user
            )

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
