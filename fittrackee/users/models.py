from datetime import datetime
from typing import Dict, Optional, Union

import jwt
from fittrackee import bcrypt, db
from flask import current_app
from sqlalchemy import func
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import select

from ..workouts.models import Workout
from .utils_token import decode_user_token, get_user_token

BaseModel: DeclarativeMeta = db.Model


class User(BaseModel):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
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
    # does the week start Monday?
    weekm = db.Column(db.Boolean(50), default=False, nullable=False)
    workouts = db.relationship(
        'Workout', lazy=True, backref=db.backref('user', lazy='joined')
    )
    records = db.relationship(
        'Record', lazy=True, backref=db.backref('user', lazy='joined')
    )
    language = db.Column(db.String(50), nullable=True)

    def __repr__(self) -> str:
        return f'<User {self.username!r}>'

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        created_at: Optional[datetime] = datetime.utcnow(),
    ) -> None:
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.created_at = created_at

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
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

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

    def serialize(self) -> Dict:
        sports = []
        total = (0, '0:00:00')
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
                    func.sum(Workout.distance), func.sum(Workout.duration)
                )
                .filter(Workout.user_id == self.id)
                .first()
            )
        return {
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'admin': self.admin,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'location': self.location,
            'birth_date': self.birth_date,
            'picture': self.picture is not None,
            'timezone': self.timezone,
            'weekm': self.weekm,
            'language': self.language,
            'nb_sports': len(sports),
            'nb_workouts': self.workouts_count,
            'sports_list': [
                sport for sportslist in sports for sport in sportslist
            ],
            'total_distance': float(total[0]),
            'total_duration': str(total[1]),
        }
