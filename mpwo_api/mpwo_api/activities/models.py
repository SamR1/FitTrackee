import datetime

from mpwo_api import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import Enum

record_types = [
    'AS',  # 'Best Average Speed'
    'FD',  # 'Farthest Distance'
    'LD',  # 'Longest Duration'
    'MS',  # 'Max speed'
]


class Sport(db.Model):
    __tablename__ = "sports"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(50), unique=True, nullable=False)
    activities = db.relationship('Activity',
                                 lazy=True,
                                 backref=db.backref('sports', lazy='joined'))
    records = db.relationship('Record',
                              lazy=True,
                              backref=db.backref('sports', lazy='joined'))

    def __repr__(self):
        return '<Sport {!r}>'.format(self.label)

    def __init__(self, label):
        self.label = label

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            '_can_be_deleted': len(self.activities) == 0
        }


class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False)
    sport_id = db.Column(
        db.Integer,
        db.ForeignKey('sports.id'),
        nullable=False)
    title = db.Column(db.String(255), nullable=True)
    gpx = db.Column(db.String(255), nullable=True)
    creation_date = db.Column(
        db.DateTime, default=datetime.datetime.utcnow)
    modification_date = db.Column(
        db.DateTime, onupdate=datetime.datetime.utcnow)
    activity_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Interval, nullable=False)
    pauses = db.Column(db.Interval, nullable=True)
    moving = db.Column(db.Interval, nullable=True)
    distance = db.Column(db.Numeric(5, 3), nullable=True)    # kilometers
    min_alt = db.Column(db.Numeric(5, 2), nullable=True)     # meters
    max_alt = db.Column(db.Numeric(5, 2), nullable=True)     # meters
    descent = db.Column(db.Numeric(5, 2), nullable=True)     # meters
    ascent = db.Column(db.Numeric(5, 2), nullable=True)      # meters
    max_speed = db.Column(db.Numeric(5, 2), nullable=True)   # km/h
    ave_speed = db.Column(db.Numeric(5, 2), nullable=True)   # km/h
    records = db.relationship('Record',
                              lazy=True,
                              backref=db.backref('activities', lazy='joined'))

    def __str__(self):
        return '<Activity \'{}\' - {}>'.format(
            self.sports.label, self.activity_date, )

    def __init__(self, user_id, sport_id, activity_date, distance, duration):
        self.user_id = user_id
        self.sport_id = sport_id
        self.activity_date = activity_date
        self.distance = distance
        self.duration = duration

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sport_id": self.sport_id,
            "title": self.title,
            "creation_date": self.creation_date,
            "modification_date": self.modification_date,
            "activity_date": self.activity_date,
            "duration": str(self.duration) if self.duration else None,
            "pauses": str(self.pauses) if self.pauses else None,
            "moving": str(self.moving) if self.moving else None,
            "distance": float(self.distance) if self.distance else None,
            "min_alt": float(self.min_alt) if self.min_alt else None,
            "max_alt": float(self.max_alt) if self.max_alt else None,
            "descent": float(self.descent) if self.descent else None,
            "ascent": float(self.ascent) if self.ascent else None,
            "max_speed": float(self.max_speed) if self.max_speed else None,
            "ave_speed": float(self.ave_speed) if self.ave_speed else None,
            "with_gpx": self.gpx is not None
        }


class Record(db.Model):
    __tablename__ = "records"
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'sport_id', 'record_type', name='user_sports_records'),)
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False)
    sport_id = db.Column(
        db.Integer,
        db.ForeignKey('sports.id'),
        nullable=False)
    activity_id = db.Column(
        db.Integer,
        db.ForeignKey('activities.id'),
        nullable=False)
    record_type = db.Column(Enum(*record_types, name="record_types"))
    activity_date = db.Column(db.DateTime, nullable=False)
    _value = db.Column("value", db.Integer, nullable=True)

    def __str__(self):
        return '<Record {} - {} - {}>'.format(
            self.sports.label,
            self.record_type,
            self.activity_date.strftime('%Y-%m-%d')
        )

    def __init__(self, user_id, sport_id, activity, record_type):
        self.user_id = user_id
        self.sport_id = sport_id
        self.activity_id = activity.id
        self.record_type = record_type
        self.activity_date = activity.activity_date

    @hybrid_property
    def value(self):
        if self._value is None:
            return None

        if self.record_type == 'LD':
            return datetime.timedelta(seconds=self._value)
        elif self.record_type in ['AS', 'MS']:
            return float(self._value / 100)
        else:  # 'FD'
            return float(self._value / 1000)

    @value.setter
    def value(self, val):
        if self.record_type == 'LD':
            hours, minutes, seconds = str(val).split(':')
            self._value = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        elif self.record_type in ['AS', 'MS']:
            self._value = int(val * 100)
        else:  # 'FD'
            self._value = int(val * 1000)

    def serialize(self):
        if self.value is None:
            value = None
        elif self.record_type in ['AS', 'FD', 'MS']:
            value = float(self.value)
        else:  # 'LD'
            value = str(self.value)

        return {
            "id": self.id,
            "user_id": self.user_id,
            "sport_id": self.sport_id,
            "activity_id": self.activity_id,
            "record_type": self.record_type,
            "activity_date": self.activity_date,
            "value": value,
        }
