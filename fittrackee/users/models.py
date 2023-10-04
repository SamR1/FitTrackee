import os
from datetime import datetime
from typing import Any, Dict, Optional, Union

import jwt
from flask import current_app
from sqlalchemy import func
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select

from fittrackee import appLog, bcrypt, db
from fittrackee.files import get_absolute_file_path
from fittrackee.workouts.models import Workout

from .exceptions import UserNotFoundException
from .roles import UserRole
from .utils.token import decode_user_token, get_user_token

BaseModel: DeclarativeMeta = db.Model


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
    # does the week start Monday?
    weekm = db.Column(db.Boolean, default=False, nullable=False)
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

    def serialize(self, current_user: 'User') -> Dict:
        role = (
            UserRole.AUTH_USER
            if current_user.id == self.id
            else UserRole.ADMIN
            if current_user.admin
            else UserRole.USER
        )

        if role == UserRole.USER:
            raise UserNotFoundException()

        sports = []
        total = (0, '0:00:00', 0)
        if self.workouts_count > 0:  # type: ignore
            sports = (
                db.session.query(Workout.sport_id)
                .filter(Workout.user_id == self.id)
                .group_by(Workout.sport_id)
                .order_by(Workout.sport_id)
                .all()
            )
            total = (
                db.session.query(
                    func.sum(Workout.distance),
                    func.sum(Workout.duration),
                    func.sum(Workout.ascent),
                )
                .filter(Workout.user_id == self.id)
                .first()
            )

        serialized_user = {
            'admin': self.admin,
            'bio': self.bio,
            'birth_date': self.birth_date,
            'created_at': self.created_at,
            'email': self.email,
            'email_to_confirm': self.email_to_confirm,
            'first_name': self.first_name,
            'is_active': self.is_active,
            'last_name': self.last_name,
            'location': self.location,
            'nb_sports': len(sports),
            'nb_workouts': self.workouts_count,
            'picture': self.picture is not None,
            'records': [record.serialize() for record in self.records],
            'sports_list': [
                sport for sportslist in sports for sport in sportslist
            ],
            'total_ascent': float(total[2]) if total[2] else 0.0,
            'total_distance': float(total[0]),
            'total_duration': str(total[1]),
            'username': self.username,
        }
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
                    'use_raw_gpx_speed': self.use_raw_gpx_speed,
                    'weekm': self.weekm,
                },
            }

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
