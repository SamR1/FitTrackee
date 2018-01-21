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
    creation_date = db.Column(db.DateTime, default=datetime.datetime.now)
    modification_date = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    activity_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Interval, nullable=False)
    pauses = db.Column(db.Interval, nullable=True)
    moving = db.Column(db.Interval, nullable=True)
    distance = db.Column(db.Numeric(5, 2), nullable=True)
    min_alt = db.Column(db.Numeric(5, 2), nullable=True)
    max_alt = db.Column(db.Numeric(5, 2), nullable=True)
    descent = db.Column(db.Numeric(5, 2), nullable=True)
    ascent = db.Column(db.Numeric(5, 2), nullable=True)
    max_speed = db.Column(db.Numeric(5, 2), nullable=True)
    ave_speed = db.Column(db.Numeric(5, 2), nullable=True)

    def __str__(self):
        return self.sport.label + \
               " - " + self.activity_date.strftime('%Y-%m-%d')

    def __init__(self, user_id, sport_id, activity_date):
        self.user_id = user_id
        self.sport_id = sport_id
        self.activity_date = activity_date
