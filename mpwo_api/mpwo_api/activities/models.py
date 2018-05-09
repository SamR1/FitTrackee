import datetime

from mpwo_api import db


class Sport(db.Model):
    __tablename__ = "sports"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(50), unique=True, nullable=False)
    activities = db.relationship('Activity',
                                 lazy=True,
                                 backref=db.backref('sports', lazy='joined'))

    def __repr__(self):
        return self.label

    def __init__(self, label):
        self.label = label

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label
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
    gpx = db.Column(db.String(255), nullable=True)
    creation_date = db.Column(
        db.DateTime, default=datetime.datetime.utcnow)
    modification_date = db.Column(
        db.DateTime, onupdate=datetime.datetime.utcnow)
    activity_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Interval, nullable=False)
    pauses = db.Column(db.Interval, nullable=True)
    moving = db.Column(db.Interval, nullable=True)
    distance = db.Column(db.Numeric(5, 2), nullable=True)    # kilometers
    min_alt = db.Column(db.Numeric(5, 2), nullable=True)     # meters
    max_alt = db.Column(db.Numeric(5, 2), nullable=True)     # meters
    descent = db.Column(db.Numeric(5, 2), nullable=True)     # meters
    ascent = db.Column(db.Numeric(5, 2), nullable=True)      # meters
    max_speed = db.Column(db.Numeric(5, 2), nullable=True)   # km/h
    ave_speed = db.Column(db.Numeric(5, 2), nullable=True)   # km/h

    def __str__(self):
        return str(self.sports.label) + \
               " - " + self.activity_date.strftime('%Y-%m-%d')

    def __init__(self, user_id, sport_id, activity_date, duration):
        self.user_id = user_id
        self.sport_id = sport_id
        self.activity_date = activity_date
        self.duration = duration

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sport_id": self.sport_id,
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
