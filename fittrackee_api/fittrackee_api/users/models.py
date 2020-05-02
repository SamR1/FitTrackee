import datetime

import jwt
from fittrackee_api import bcrypt, db
from flask import current_app
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import select

from ..activities.models import Activity


class User(db.Model):
    __tablename__ = "users"
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
    activities = db.relationship(
        'Activity', lazy=True, backref=db.backref('user', lazy='joined')
    )
    records = db.relationship(
        'Record', lazy=True, backref=db.backref('user', lazy='joined')
    )
    language = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<User {self.username!r}>'

    def __init__(
        self, username, email, password, created_at=datetime.datetime.utcnow()
    ):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.created_at = created_at

    @staticmethod
    def encode_auth_token(user_id):
        """
        Generates the auth token
        :param user_id: -
        :return: JWToken
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow()
                + datetime.timedelta(
                    days=current_app.config.get('TOKEN_EXPIRATION_DAYS'),
                    seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS'),
                ),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id,
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256',
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token: -
        :return: integer|string
        """
        try:
            payload = jwt.decode(
                auth_token, current_app.config.get('SECRET_KEY')
            )
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    @hybrid_property
    def activities_count(self):
        return Activity.query.filter(Activity.user_id == self.id).count()

    @activities_count.expression
    def activities_count(self):
        return (
            select([func.count(Activity.id)])
            .where(Activity.user_id == self.id)
            .label("activities_count")
        )

    def serialize(self):
        sports = []
        total = (None, None)
        if self.activities_count > 0:
            sports = (
                db.session.query(Activity.sport_id)
                .filter(Activity.user_id == self.id)
                .group_by(Activity.sport_id)
                .order_by(Activity.sport_id)
                .all()
            )
            total = (
                db.session.query(
                    func.sum(Activity.distance), func.sum(Activity.duration)
                )
                .filter(Activity.user_id == self.id)
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
            'nb_activities': self.activities_count,
            'nb_sports': len(sports),
            'sports_list': [
                sport for sportslist in sports for sport in sportslist
            ],
            'total_distance': float(total[0]) if total[0] else 0,
            'total_duration': str(total[1]) if total[1] else "0:00:00",
        }
