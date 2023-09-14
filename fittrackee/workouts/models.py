import datetime
import os
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session, object_session
from sqlalchemy.types import JSON, Enum

from fittrackee import BaseModel, appLog, db
from fittrackee.comments.models import Comment
from fittrackee.federation.decorators import federation_required
from fittrackee.federation.objects.like import LikeObject
from fittrackee.federation.objects.tombstone import TombstoneObject
from fittrackee.federation.objects.workout import WorkoutObject
from fittrackee.files import get_absolute_file_path
from fittrackee.privacy_levels import (
    PrivacyLevel,
    can_view,
    get_map_visibility,
)
from fittrackee.utils import encode_uuid

from .exceptions import WorkoutForbiddenException
from .utils.convert import convert_in_duration, convert_value_to_integer

if TYPE_CHECKING:
    from fittrackee.users.models import User


record_types = [
    'AS',  # 'Best Average Speed'
    'FD',  # 'Farthest Distance'
    'HA',  # 'Highest Ascent'
    'LD',  # 'Longest Duration'
    'MS',  # 'Max speed'
]


def update_records(
    user_id: int, sport_id: int, connection: Connection, session: Session
) -> None:
    record_table = Record.__table__
    new_records = Workout.get_user_workout_records(user_id, sport_id)
    for record_type, record_data in new_records.items():
        if record_data['record_value']:
            record = Record.query.filter_by(
                user_id=user_id, sport_id=sport_id, record_type=record_type
            ).first()
            if record:
                value = convert_value_to_integer(
                    record_type, record_data['record_value']
                )
                connection.execute(
                    record_table.update()
                    .where(record_table.c.id == record.id)
                    .values(
                        value=value,
                        workout_id=record_data['workout'].id,
                        workout_uuid=record_data['workout'].uuid,
                        workout_date=record_data['workout'].workout_date,
                    )
                )
            else:
                new_record = Record(
                    workout=record_data['workout'], record_type=record_type
                )
                new_record.value = record_data['record_value']  # type: ignore
                session.add(new_record)
        else:
            connection.execute(
                record_table.delete()
                .where(record_table.c.user_id == user_id)
                .where(record_table.c.sport_id == sport_id)
                .where(record_table.c.record_type == record_type)
            )


class Sport(BaseModel):
    __tablename__ = 'sports'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(50), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    stopped_speed_threshold = db.Column(db.Float, default=1.0, nullable=False)
    workouts = db.relationship(
        'Workout',
        lazy=True,
        backref=db.backref('sport', lazy='joined', single_parent=True),
    )
    records = db.relationship(
        'Record',
        lazy=True,
        backref=db.backref('sport', lazy='joined', single_parent=True),
    )

    def __repr__(self) -> str:
        return f'<Sport {self.label!r}>'

    def __init__(self, label: str) -> None:
        self.label = label

    def serialize(
        self,
        is_admin: Optional[bool] = False,
        sport_preferences: Optional[Dict] = None,
    ) -> Dict:
        serialized_sport = {
            'id': self.id,
            'label': self.label,
            'is_active': self.is_active,
            'is_active_for_user': (
                self.is_active
                if sport_preferences is None
                else (sport_preferences['is_active'] and self.is_active)
            ),
            'color': (
                None
                if sport_preferences is None
                else sport_preferences['color']
            ),
            'stopped_speed_threshold': (
                self.stopped_speed_threshold
                if sport_preferences is None
                else sport_preferences['stopped_speed_threshold']
            ),
        }
        if is_admin:
            serialized_sport['has_workouts'] = len(self.workouts) > 0
        return serialized_sport


class Workout(BaseModel):
    __tablename__ = 'workouts'
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
    sport_id = db.Column(
        db.Integer, db.ForeignKey('sports.id'), index=True, nullable=False
    )
    title = db.Column(db.String(255), nullable=True)
    gpx = db.Column(db.String(255), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modification_date = db.Column(
        db.DateTime, onupdate=datetime.datetime.utcnow
    )
    workout_date = db.Column(db.DateTime, index=True, nullable=False)
    duration = db.Column(db.Interval, nullable=False)
    pauses = db.Column(db.Interval, nullable=True)
    moving = db.Column(db.Interval, nullable=True)
    distance = db.Column(db.Numeric(6, 3), nullable=True)  # kilometers
    min_alt = db.Column(db.Numeric(6, 2), nullable=True)  # meters
    max_alt = db.Column(db.Numeric(6, 2), nullable=True)  # meters
    descent = db.Column(db.Numeric(8, 3), nullable=True)  # meters
    ascent = db.Column(db.Numeric(8, 3), nullable=True)  # meters
    max_speed = db.Column(db.Numeric(6, 2), nullable=True)  # km/h
    ave_speed = db.Column(db.Numeric(6, 2), nullable=True)  # km/h
    bounds = db.Column(postgresql.ARRAY(db.Float), nullable=True)
    map = db.Column(db.String(255), nullable=True)
    map_id = db.Column(db.String(50), index=True, nullable=True)
    weather_start = db.Column(JSON, nullable=True)
    weather_end = db.Column(JSON, nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    workout_visibility = db.Column(
        Enum(PrivacyLevel, name='privacy_levels'),
        server_default='PRIVATE',
        nullable=False,
    )
    map_visibility = db.Column(
        Enum(PrivacyLevel, name='privacy_levels'),
        server_default='PRIVATE',
        nullable=False,
    )
    ap_id = db.Column(db.Text(), nullable=True)
    remote_url = db.Column(db.Text(), nullable=True)

    segments = db.relationship(
        'WorkoutSegment',
        lazy=True,
        cascade='all, delete',
        backref=db.backref('workout', lazy='joined', single_parent=True),
    )
    records = db.relationship(
        'Record',
        lazy=True,
        cascade='all, delete',
        backref=db.backref('workout', lazy='joined', single_parent=True),
    )
    comments = db.relationship(
        Comment,
        lazy=True,
        backref=db.backref('workout', lazy='joined', single_parent=True),
    )
    likes = db.relationship(
        "User",
        secondary="workout_likes",
        primaryjoin="Workout.id == WorkoutLike.workout_id",
        secondaryjoin="WorkoutLike.user_id == User.id",
        lazy="dynamic",
        viewonly=True,
    )

    def __str__(self) -> str:
        return f'<Workout \'{self.sport.label}\' - {self.workout_date}>'

    def __init__(
        self,
        user_id: int,
        sport_id: int,
        workout_date: datetime.datetime,
        distance: float,
        duration: datetime.timedelta,
    ) -> None:
        self.user_id = user_id
        self.sport_id = sport_id
        self.workout_date = workout_date
        self.distance = distance
        self.duration = duration

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    @property
    def calculated_map_visibility(self) -> PrivacyLevel:
        return get_map_visibility(self.map_visibility, self.workout_visibility)

    def liked_by(self, user: 'User') -> bool:
        return user in self.likes.all()

    def get_workout_data(
        self,
        user: Optional['User'],
        can_see_map_data: Optional[bool] = None,
        for_report: bool = False,
    ) -> Dict:
        if can_see_map_data is None:
            can_see_map_data = can_view(
                self,
                "calculated_map_visibility",
                user=user,
                for_report=for_report,
            )
        return {
            'id': self.short_id,  # WARNING: client use uuid as id
            'sport_id': self.sport_id,
            'title': self.title,
            'creation_date': self.creation_date,
            'modification_date': self.modification_date,
            'workout_date': self.workout_date,
            'duration': None if self.duration is None else str(self.duration),
            'pauses': str(self.pauses) if self.pauses else None,
            'moving': None if self.moving is None else str(self.moving),
            'distance': (
                None if self.distance is None else float(self.distance)
            ),
            'min_alt': None if self.min_alt is None else float(self.min_alt),
            'max_alt': None if self.max_alt is None else float(self.max_alt),
            'descent': None if self.descent is None else float(self.descent),
            'ascent': None if self.ascent is None else float(self.ascent),
            'max_speed': (
                None if self.max_speed is None else float(self.max_speed)
            ),
            'ave_speed': (
                None if self.ave_speed is None else float(self.ave_speed)
            ),
            'records': (
                []
                if for_report
                else [record.serialize() for record in self.records]
            ),
            'segments': (
                [segment.serialize() for segment in self.segments]
                if can_see_map_data
                else []
            ),
            'weather_start': self.weather_start,
            'weather_end': self.weather_end,
            'notes': self.notes if user and user.id == self.user_id else None,
            'map_visibility': self.calculated_map_visibility.value,
            'workout_visibility': self.workout_visibility.value,
            'likes_count': self.likes.count(),
            'liked': self.liked_by(user) if user else False,
        }

    def serialize(
        self,
        user: Optional['User'] = None,
        params: Optional[Dict] = None,
        for_report: bool = False,
    ) -> Dict:
        if not can_view(
            self, "workout_visibility", user=user, for_report=for_report
        ):
            raise WorkoutForbiddenException()
        can_see_map_data = can_view(
            self, "calculated_map_visibility", user=user, for_report=for_report
        )
        is_owner = user and user.id == self.user_id
        if is_owner:
            date_from = params.get('from') if params else None
            date_to = params.get('to') if params else None
            distance_from = params.get('distance_from') if params else None
            distance_to = params.get('distance_to') if params else None
            duration_from = params.get('duration_from') if params else None
            duration_to = params.get('duration_to') if params else None
            ave_speed_from = params.get('ave_speed_from') if params else None
            ave_speed_to = params.get('ave_speed_to') if params else None
            max_speed_from = params.get('max_speed_from') if params else None
            max_speed_to = params.get('max_speed_to') if params else None
            sport_id = params.get('sport_id') if params else None
            previous_workout = (
                Workout.query.filter(
                    Workout.id != self.id,
                    Workout.user_id == self.user_id,
                    Workout.sport_id == sport_id if sport_id else True,
                    Workout.workout_date <= self.workout_date,
                    Workout.workout_date
                    >= datetime.datetime.strptime(date_from, '%Y-%m-%d')
                    if date_from
                    else True,
                    Workout.workout_date
                    <= datetime.datetime.strptime(date_to, '%Y-%m-%d')
                    if date_to
                    else True,
                    Workout.distance >= float(distance_from)
                    if distance_from
                    else True,
                    Workout.distance <= float(distance_to)
                    if distance_to
                    else True,
                    Workout.duration >= convert_in_duration(duration_from)
                    if duration_from
                    else True,
                    Workout.duration <= convert_in_duration(duration_to)
                    if duration_to
                    else True,
                    Workout.ave_speed >= float(ave_speed_from)
                    if ave_speed_from
                    else True,
                    Workout.ave_speed <= float(ave_speed_to)
                    if ave_speed_to
                    else True,
                    Workout.max_speed >= float(max_speed_from)
                    if max_speed_from
                    else True,
                    Workout.max_speed <= float(max_speed_to)
                    if max_speed_to
                    else True,
                )
                .order_by(Workout.workout_date.desc())
                .first()
            )
            next_workout = (
                Workout.query.filter(
                    Workout.id != self.id,
                    Workout.user_id == self.user_id,
                    Workout.sport_id == sport_id if sport_id else True,
                    Workout.workout_date >= self.workout_date,
                    Workout.workout_date
                    >= datetime.datetime.strptime(date_from, '%Y-%m-%d')
                    if date_from
                    else True,
                    Workout.workout_date
                    <= datetime.datetime.strptime(date_to, '%Y-%m-%d')
                    if date_to
                    else True,
                    Workout.distance >= float(distance_from)
                    if distance_from
                    else True,
                    Workout.distance <= float(distance_to)
                    if distance_to
                    else True,
                    Workout.duration >= convert_in_duration(duration_from)
                    if duration_from
                    else True,
                    Workout.duration <= convert_in_duration(duration_to)
                    if duration_to
                    else True,
                    Workout.ave_speed >= float(ave_speed_from)
                    if ave_speed_from
                    else True,
                    Workout.ave_speed <= float(ave_speed_to)
                    if ave_speed_to
                    else True,
                )
                .order_by(Workout.workout_date.asc())
                .first()
            )
        else:
            next_workout = None
            previous_workout = None

        workout = self.get_workout_data(user, can_see_map_data, for_report)
        workout["next_workout"] = (
            next_workout.short_id if next_workout else None
        )
        workout["previous_workout"] = (
            previous_workout.short_id if previous_workout else None
        )
        workout["bounds"] = (
            [float(bound) for bound in self.bounds]
            if self.bounds and can_see_map_data
            else []
        )
        workout["user"] = self.user.serialize()
        workout["map"] = self.map_id if self.map and can_see_map_data else None
        workout["with_gpx"] = self.gpx is not None and can_see_map_data
        if self.user.is_remote:
            workout['remote_url'] = self.remote_url
        return workout

    @classmethod
    def get_user_workout_records(cls, user_id: int, sport_id: int) -> Dict:
        """
        Note:
        Values for ascent are null for workouts without gpx
        """
        record_types_columns = {
            'AS': 'ave_speed',  # 'Average speed'
            'FD': 'distance',  # 'Farthest Distance'
            'HA': 'ascent',  # 'Highest Ascent'
            'LD': 'moving',  # 'Longest Duration'
            'MS': 'max_speed',  # 'Max speed'
        }
        records = {}
        for record_type, column in record_types_columns.items():
            column_sorted = getattr(getattr(Workout, column), 'desc')()
            record_workout = (
                Workout.query.filter(
                    Workout.user_id == user_id,
                    Workout.sport_id == sport_id,
                    getattr(Workout, column) != None,  # noqa
                )
                .order_by(column_sorted, Workout.workout_date)
                .first()
            )
            records[record_type] = dict(
                record_value=(
                    getattr(record_workout, column) if record_workout else None
                ),
                workout=record_workout,
            )
        return records

    @federation_required
    def get_activities(self, activity_type: str) -> Tuple[Dict, Dict]:
        if activity_type in ['Create', 'Update']:
            workout_object = WorkoutObject(self, activity_type=activity_type)
            return workout_object.get_activity(), workout_object.get_activity(
                is_note=True
            )
        # Delete activity
        tombstone_object = TombstoneObject(self)
        delete_activity = tombstone_object.get_activity()
        # delete activities for workout and note are the same
        return delete_activity, delete_activity


@listens_for(Workout, 'after_insert')
def on_workout_insert(
    mapper: Mapper, connection: Connection, workout: Workout
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        # For now only create records for local workouts
        if not workout.remote_url:
            update_records(
                workout.user_id, workout.sport_id, connection, session
            )


@listens_for(Workout, 'after_update')
def on_workout_update(
    mapper: Mapper, connection: Connection, workout: Workout
) -> None:
    if object_session(workout).is_modified(
        workout, include_collections=True
    ):  # noqa

        @listens_for(db.Session, 'after_flush', once=True)
        def receive_after_flush(session: Session, context: Any) -> None:
            sports_list = [workout.sport_id]
            records = Record.query.filter_by(workout_id=workout.id).all()
            for rec in records:
                if rec.sport_id not in sports_list:
                    sports_list.append(rec.sport_id)
            for sport_id in sports_list:
                update_records(workout.user_id, sport_id, connection, session)


@listens_for(Workout, 'after_delete')
def on_workout_delete(
    mapper: Mapper, connection: Connection, old_record: 'Record'
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        if old_record.map:
            try:
                os.remove(get_absolute_file_path(old_record.map))
            except OSError:
                appLog.error('map file not found when deleting workout')
        if old_record.gpx:
            try:
                os.remove(get_absolute_file_path(old_record.gpx))
            except OSError:
                appLog.error('gpx file not found when deleting workout')


class WorkoutSegment(BaseModel):
    __tablename__ = 'workout_segments'
    workout_id = db.Column(
        db.Integer, db.ForeignKey('workouts.id'), primary_key=True
    )
    workout_uuid = db.Column(postgresql.UUID(as_uuid=True), nullable=False)
    segment_id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Interval, nullable=False)
    pauses = db.Column(db.Interval, nullable=True)
    moving = db.Column(db.Interval, nullable=True)
    distance = db.Column(db.Numeric(6, 3), nullable=True)  # kilometers
    min_alt = db.Column(db.Numeric(6, 2), nullable=True)  # meters
    max_alt = db.Column(db.Numeric(6, 2), nullable=True)  # meters
    descent = db.Column(db.Numeric(8, 3), nullable=True)  # meters
    ascent = db.Column(db.Numeric(8, 3), nullable=True)  # meters
    max_speed = db.Column(db.Numeric(6, 2), nullable=True)  # km/h
    ave_speed = db.Column(db.Numeric(6, 2), nullable=True)  # km/h

    def __str__(self) -> str:
        return (
            f'<Segment \'{self.segment_id}\' '
            f'for workout \'{encode_uuid(self.workout_uuid)}\'>'
        )

    def __init__(
        self, segment_id: int, workout_id: int, workout_uuid: UUID
    ) -> None:
        self.segment_id = segment_id
        self.workout_id = workout_id
        self.workout_uuid = workout_uuid

    def serialize(self) -> Dict:
        return {
            'workout_id': encode_uuid(self.workout_uuid),
            'segment_id': self.segment_id,
            'duration': str(self.duration) if self.duration else None,
            'pauses': str(self.pauses) if self.pauses else None,
            'moving': str(self.moving) if self.moving else None,
            'distance': float(self.distance) if self.distance else None,
            'min_alt': float(self.min_alt) if self.min_alt else None,
            'max_alt': float(self.max_alt) if self.max_alt else None,
            'descent': float(self.descent) if self.descent else None,
            'ascent': float(self.ascent) if self.ascent else None,
            'max_speed': float(self.max_speed) if self.max_speed else None,
            'ave_speed': float(self.ave_speed) if self.ave_speed else None,
        }


class Record(BaseModel):
    __tablename__ = "records"
    __table_args__ = (
        db.UniqueConstraint(
            'user_id', 'sport_id', 'record_type', name='user_sports_records'
        ),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sport_id = db.Column(
        db.Integer, db.ForeignKey('sports.id'), nullable=False
    )
    workout_id = db.Column(
        db.Integer, db.ForeignKey('workouts.id'), nullable=False
    )
    workout_uuid = db.Column(postgresql.UUID(as_uuid=True), nullable=False)
    record_type = db.Column(Enum(*record_types, name="record_types"))
    workout_date = db.Column(db.DateTime, nullable=False)
    _value = db.Column("value", db.Integer, nullable=True)

    def __str__(self) -> str:
        return (
            f'<Record {self.sport.label} - '
            f'{self.record_type} - '
            f"{self.workout_date.strftime('%Y-%m-%d')}>"
        )

    def __init__(self, workout: Workout, record_type: str) -> None:
        self.user_id = workout.user_id
        self.sport_id = workout.sport_id
        self.workout_id = workout.id
        self.workout_uuid = workout.uuid
        self.record_type = record_type
        self.workout_date = workout.workout_date

    @hybrid_property
    def value(self) -> Optional[Union[datetime.timedelta, float]]:
        if self._value is None:
            return None
        if self.record_type == 'LD':
            return datetime.timedelta(seconds=self._value)
        elif self.record_type in ['AS', 'MS']:
            return float(self._value / 100)
        else:  # 'FD' or 'HA'
            return float(self._value / 1000)

    @value.setter  # type: ignore
    def value(self, val: Union[str, float]) -> None:
        self._value = convert_value_to_integer(self.record_type, val)

    def serialize(self) -> Dict:
        if self.value is None:
            value = None
        elif self.record_type in ['AS', 'FD', 'HA', 'MS']:
            value = float(self.value)  # type: ignore
        else:  # 'LD'
            value = str(self.value)  # type: ignore

        return {
            'id': self.id,
            'user': self.user.username,
            'sport_id': self.sport_id,
            'workout_id': encode_uuid(self.workout_uuid),
            'record_type': self.record_type,
            'workout_date': self.workout_date,
            'value': value,
        }


@listens_for(Record, 'after_delete')
def on_record_delete(
    mapper: Mapper, connection: Connection, old_record: Record
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        workout = old_record.workout
        new_records = Workout.get_user_workout_records(
            workout.user_id, workout.sport_id
        )
        for record_type, record_data in new_records.items():
            if (
                record_data['record_value']
                and record_type == old_record.record_type
            ):
                new_record = Record(
                    workout=record_data['workout'], record_type=record_type
                )
                new_record.value = record_data['record_value']  # type: ignore
                session.add(new_record)


class WorkoutLike(BaseModel):
    __tablename__ = 'workout_likes'
    __table_args__ = (
        db.UniqueConstraint(
            'user_id', 'workout_id', name='user_id_workout_id_unique'
        ),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id', ondelete="CASCADE"),
        nullable=False,
    )

    user = db.relationship("User", lazy=True)
    workout = db.relationship("Workout", lazy=True)

    def __init__(
        self,
        user_id: int,
        workout_id: int,
        created_at: Optional[datetime.datetime] = None,
    ) -> None:
        self.user_id = user_id
        self.workout_id = workout_id
        self.created_at = (
            datetime.datetime.utcnow() if created_at is None else created_at
        )

    def get_activity(self, is_undo: bool = False) -> Dict:
        return LikeObject(
            actor_ap_id=self.user.actor.activitypub_id,
            target_object_ap_id=self.workout.ap_id,
            like_id=self.id,
            is_undo=is_undo,
        ).get_activity()


@listens_for(WorkoutLike, 'after_insert')
def on_workout_like_insert(
    mapper: Mapper, connection: Connection, new_workout_like: WorkoutLike
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        from fittrackee.users.models import Notification

        workout = Workout.query.filter_by(
            id=new_workout_like.workout_id
        ).first()
        if new_workout_like.user_id != workout.user_id:
            notification = Notification(
                from_user_id=new_workout_like.user_id,
                to_user_id=workout.user_id,
                created_at=new_workout_like.created_at,
                event_type='workout_like',
                event_object_id=workout.id,
            )
            session.add(notification)


@listens_for(WorkoutLike, 'after_delete')
def on_workout_like_delete(
    mapper: Mapper, connection: Connection, old_workout_like: WorkoutLike
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        from fittrackee.users.models import Notification

        workout = Workout.query.filter_by(
            id=old_workout_like.workout_id
        ).first()
        Notification.query.filter_by(
            from_user_id=old_workout_like.user_id,
            to_user_id=workout.user_id,
            event_type='workout_like',
            event_object_id=workout.id,
        ).delete()
