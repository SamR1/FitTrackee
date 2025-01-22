import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, Optional, Union
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session, object_session
from sqlalchemy.sql.expression import nulls_last
from sqlalchemy.types import JSON, Enum

from fittrackee import BaseModel, appLog, db
from fittrackee.comments.models import Comment
from fittrackee.equipments.models import WorkoutEquipment
from fittrackee.files import get_absolute_file_path
from fittrackee.utils import TZDateTime, aware_utc_now, encode_uuid
from fittrackee.visibility_levels import (
    VisibilityLevel,
    can_view,
    get_calculated_visibility,
)

from .exceptions import WorkoutForbiddenException
from .utils.convert import convert_in_duration, convert_value_to_integer

if TYPE_CHECKING:
    from sqlalchemy.orm.attributes import AttributeEvent

    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User

    from ..reports.models import ReportAction


EMPTY_MINIMAL_WORKOUT_VALUES: Dict = {
    'title': '',
    'moving': None,
    'distance': None,
    'duration': None,
    'min_alt': None,
    'max_alt': None,
    'descent': None,
    'ascent': None,
    'map_visibility': None,
}
EMPTY_WORKOUT_VALUES: Dict = {
    'creation_date': None,
    'modification_date': None,
    'pauses': None,
    'equipments': [],
    'records': [],
    'segments': [],
    'weather_start': None,
    'weather_end': None,
    'notes': '',
    'likes_count': 0,
    'liked': False,
}

record_types = [
    'AS',  # 'Best Average Speed'
    'FD',  # 'Farthest Distance'
    'HA',  # 'Highest Ascent'
    'LD',  # 'Longest Duration'
    'MS',  # 'Max speed'
]
DESCRIPTION_MAX_CHARACTERS = 10000
NOTES_MAX_CHARACTERS = 500
TITLE_MAX_CHARACTERS = 255


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


def format_value(
    value: Union[Decimal, timedelta], attribute: str
) -> Union[float, timedelta]:
    return float(value) if attribute == 'distance' else value  # type: ignore


def update_equipments(workout: 'Workout', connection: Connection) -> None:
    from fittrackee.equipments.models import Equipment

    instance_state = db.inspect(workout)
    workout_values = {}

    for attribute in ["distance", "duration", "moving"]:
        state_history = instance_state.attrs[attribute].load_history()
        if len(state_history.added) > 0 and len(state_history.deleted) > 0:
            workout_values[attribute] = {
                'new': format_value(state_history.added[0], attribute),
                'old': format_value(state_history.deleted[0], attribute),
            }
    if not workout_values:
        return

    equipment_table = Equipment.__table__
    for equipment in workout.equipments:
        equipment_values = {}
        for attribute, value in workout_values.items():
            column = getattr(equipment, f"total_{attribute}")
            equipment_values[f"total_{attribute}"] = (
                format_value(column, attribute)  # type: ignore
                - value["old"]
                + value["new"]
            )

        connection.execute(
            equipment_table.update()
            .where(equipment_table.c.id == equipment.id)
            .values(**equipment_values)
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

    @property
    def has_workouts(self) -> bool:
        return (
            db.session.query(Workout.id)
            .filter_by(sport_id=self.id)
            .limit(1)
            .count()
            > 0
        )

    def serialize(
        self,
        *,
        check_workouts: bool = False,
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
        if check_workouts:
            serialized_sport['has_workouts'] = self.has_workouts

        serialized_sport['default_equipments'] = (
            []
            if sport_preferences is None
            else sport_preferences['default_equipments']
        )

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
    title = db.Column(db.String(TITLE_MAX_CHARACTERS), nullable=True)
    gpx = db.Column(db.String(255), nullable=True)
    creation_date = db.Column(TZDateTime, default=aware_utc_now)
    modification_date = db.Column(TZDateTime, onupdate=aware_utc_now)
    workout_date = db.Column(TZDateTime, index=True, nullable=False)
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
    notes = db.Column(db.String(NOTES_MAX_CHARACTERS), nullable=True)
    description = db.Column(
        db.String(DESCRIPTION_MAX_CHARACTERS), nullable=True
    )
    workout_visibility = db.Column(
        Enum(VisibilityLevel, name='visibility_levels'),
        server_default='PRIVATE',
        nullable=False,
    )
    map_visibility = db.Column(
        Enum(VisibilityLevel, name='visibility_levels'),
        server_default='PRIVATE',
        nullable=False,
    )
    suspended_at = db.Column(TZDateTime, nullable=True)
    analysis_visibility = db.Column(
        Enum(VisibilityLevel, name='visibility_levels'),
        server_default='PRIVATE',
        nullable=False,
    )

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
        order_by='Record.record_type.asc()',
    )
    equipments = db.relationship(
        'Equipment', secondary=WorkoutEquipment, back_populates='workouts'
    )
    comments = db.relationship(
        Comment,
        lazy=True,
        backref=db.backref('workout', lazy='select', single_parent=True),
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
        workout_date: datetime,
        distance: float,
        duration: timedelta,
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
    def calculated_analysis_visibility(self) -> VisibilityLevel:
        return get_calculated_visibility(
            visibility=self.analysis_visibility,
            parent_visibility=self.workout_visibility,
        )

    @property
    def calculated_map_visibility(self) -> VisibilityLevel:
        return get_calculated_visibility(
            visibility=self.map_visibility,
            parent_visibility=self.analysis_visibility,
        )

    def liked_by(self, user: 'User') -> bool:
        return user in self.likes.all()

    @property
    def suspension_action(self) -> Optional['ReportAction']:
        if self.suspended_at is None:
            return None

        from fittrackee.reports.models import ReportAction

        return (
            ReportAction.query.filter(
                ReportAction.workout_id == self.id,
                ReportAction.action_type == "workout_suspension",
            )
            .order_by(ReportAction.created_at.desc())
            .first()
        )

    def get_workout_data(
        self,
        user: Optional['User'],
        *,
        can_see_analysis_data: Optional[bool] = None,
        can_see_map_data: Optional[bool] = None,
        for_report: bool = False,
        additional_data: bool = False,
        light: bool = True,
        with_equipments: bool = False,  # for workouts list
    ) -> Dict:
        """
        Used by Workout serializer and data export

        - can_see_analysis_data: if user can see charts
        - can_see_map_data: if user can see map
        - for_report: privacy levels are overridden on report
        - additional_data is False when:
          - workout is not suspended
          - user is workout owner
            or workout is displayed in report and current user has moderation
            rights
        - light: when true, only workouts data needed for workout lists
          and timeline.
          If 'light' is False, 'with_equipments' is ignored.
        - with_equipments: only used when 'light' is True. Needed for
          3rd-party apps updating workouts equipments
        """
        for_report = (
            for_report and user is not None and user.has_moderator_rights
        )
        if can_see_analysis_data is None:
            can_see_analysis_data = can_view(
                self,
                "calculated_analysis_visibility",
                user=user,
                for_report=for_report,
            )
        if can_see_map_data is None:
            can_see_map_data = can_view(
                self,
                "calculated_map_visibility",
                user=user,
                for_report=for_report,
            )

        workout_data = {
            'id': self.short_id,  # WARNING: client use uuid as id
            'sport_id': self.sport_id,
            'workout_date': self.workout_date,
            'workout_visibility': self.workout_visibility.value,
        }

        if not additional_data:
            return {
                **workout_data,
                **EMPTY_MINIMAL_WORKOUT_VALUES,
                **EMPTY_WORKOUT_VALUES,
            }

        workout_data = {
            **workout_data,
            **EMPTY_WORKOUT_VALUES,
            'title': self.title,
            'moving': None if self.moving is None else str(self.moving),
            'distance': (
                None if self.distance is None else float(self.distance)
            ),
            'duration': (
                None if self.duration is None else str(self.duration)
            ),
            'ave_speed': (
                None if self.ave_speed is None else float(self.ave_speed)
            ),
            'max_speed': (
                None if self.max_speed is None else float(self.max_speed)
            ),
            'min_alt': (
                float(self.min_alt)
                if self.min_alt is not None and can_see_analysis_data
                else None
            ),
            'max_alt': (
                float(self.max_alt)
                if self.max_alt is not None and can_see_analysis_data
                else None
            ),
            'descent': None if self.descent is None else float(self.descent),
            'ascent': None if self.ascent is None else float(self.ascent),
            'analysis_visibility': (
                self.calculated_analysis_visibility.value
                if can_see_analysis_data
                else VisibilityLevel.PRIVATE
            ),
            'map_visibility': (
                self.calculated_map_visibility.value
                if can_see_map_data
                else VisibilityLevel.PRIVATE
            ),
        }

        if not light or with_equipments:
            workout_data['equipments'] = (
                [equipment.serialize() for equipment in self.equipments]
                if user and user.id == self.user_id
                else []
            )

        if light:
            return workout_data

        return {
            **workout_data,
            'creation_date': self.creation_date,
            'modification_date': self.modification_date,
            'pauses': str(self.pauses) if self.pauses else None,
            'records': (
                []
                if for_report
                else [record.serialize() for record in self.records]
            ),
            'segments': (
                [segment.serialize() for segment in self.segments]
                if can_see_analysis_data
                else []
            ),
            'weather_start': self.weather_start,
            'weather_end': self.weather_end,
            'notes': (
                self.notes if user and user.id == self.user_id else None
            ),
            'description': self.description,
            'likes_count': self.likes.count(),
            'liked': self.liked_by(user) if user else False,
        }

    def serialize(
        self,
        *,
        user: Optional['User'] = None,
        params: Optional[Dict] = None,
        for_report: bool = False,
        light: bool = True,  # for workouts list and timeline
        with_equipments: bool = False,  # for workouts list
    ) -> Dict:
        """
        If 'light' is False, 'with_equipments' is ignored.
        """

        for_report = (
            for_report and user is not None and user.has_moderator_rights
        )
        if not can_view(
            self, "workout_visibility", user=user, for_report=for_report
        ):
            raise WorkoutForbiddenException()
        can_see_analysis_data = can_view(
            self,
            "calculated_analysis_visibility",
            user=user,
            for_report=for_report,
        )
        can_see_map_data = can_view(
            self, "calculated_map_visibility", user=user, for_report=for_report
        )
        is_owner = user is not None and user.id == self.user_id
        is_workout_suspended = self.suspended_at is not None
        additional_data = not is_workout_suspended or for_report or is_owner

        workout = self.get_workout_data(
            user,
            can_see_analysis_data=can_see_analysis_data,
            can_see_map_data=can_see_map_data,
            for_report=for_report,
            additional_data=additional_data,
            light=light,
            with_equipments=with_equipments,
        )

        workout["map"] = (
            self.map_id
            if self.map and can_see_map_data and additional_data
            else None
        )
        workout["with_gpx"] = (
            self.gpx is not None and can_see_map_data and additional_data
        )
        workout["with_analysis"] = (
            self.gpx is not None and can_see_analysis_data and additional_data
        )
        workout["suspended"] = is_workout_suspended
        workout["user"] = self.user.serialize()

        if is_owner or for_report:
            workout["suspended_at"] = self.suspended_at
            if self.suspension_action:
                workout["suspension"] = self.suspension_action.serialize(
                    current_user=user,  # type: ignore
                    full=False,
                )

        if light:
            workout["next_workout"] = None
            workout["previous_workout"] = None
            workout["bounds"] = []
            return workout

        if is_owner:
            if params and user:
                from .utils.workouts import get_datetime_from_request_args

                date_from, date_to = get_datetime_from_request_args(
                    params, user
                )
            else:
                date_from, date_to = (None, None)

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
                    Workout.workout_date >= date_from if date_from else True,
                    Workout.workout_date <= date_to if date_to else True,
                    (
                        Workout.distance >= float(distance_from)
                        if distance_from
                        else True
                    ),
                    (
                        Workout.distance <= float(distance_to)
                        if distance_to
                        else True
                    ),
                    (
                        Workout.duration >= convert_in_duration(duration_from)
                        if duration_from
                        else True
                    ),
                    (
                        Workout.duration <= convert_in_duration(duration_to)
                        if duration_to
                        else True
                    ),
                    (
                        Workout.ave_speed >= float(ave_speed_from)
                        if ave_speed_from
                        else True
                    ),
                    (
                        Workout.ave_speed <= float(ave_speed_to)
                        if ave_speed_to
                        else True
                    ),
                    (
                        Workout.max_speed >= float(max_speed_from)
                        if max_speed_from
                        else True
                    ),
                    (
                        Workout.max_speed <= float(max_speed_to)
                        if max_speed_to
                        else True
                    ),
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
                    Workout.workout_date >= date_from if date_from else True,
                    Workout.workout_date <= date_to if date_to else True,
                    (
                        Workout.distance >= float(distance_from)
                        if distance_from
                        else True
                    ),
                    (
                        Workout.distance <= float(distance_to)
                        if distance_to
                        else True
                    ),
                    (
                        Workout.duration >= convert_in_duration(duration_from)
                        if duration_from
                        else True
                    ),
                    (
                        Workout.duration <= convert_in_duration(duration_to)
                        if duration_to
                        else True
                    ),
                    (
                        Workout.ave_speed >= float(ave_speed_from)
                        if ave_speed_from
                        else True
                    ),
                    (
                        Workout.ave_speed <= float(ave_speed_to)
                        if ave_speed_to
                        else True
                    ),
                )
                .order_by(Workout.workout_date.asc())
                .first()
            )

        else:
            next_workout = None
            previous_workout = None

        workout["next_workout"] = (
            next_workout.short_id if next_workout else None
        )
        workout["previous_workout"] = (
            previous_workout.short_id if previous_workout else None
        )
        workout["bounds"] = (
            [float(bound) for bound in self.bounds]
            if self.bounds and can_see_map_data and additional_data
            else []
        )
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
                    Workout.user_id == user_id, Workout.sport_id == sport_id
                )
                .order_by(nulls_last(column_sorted), Workout.workout_date)
                .first()
            )
            records[record_type] = dict(
                record_value=(
                    getattr(record_workout, column) if record_workout else None
                ),
                workout=record_workout,
            )
        return records


@listens_for(Workout, 'after_insert')
def on_workout_insert(
    mapper: Mapper, connection: Connection, workout: Workout
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        update_records(workout.user_id, workout.sport_id, connection, session)


@listens_for(Workout, 'after_update')
def on_workout_update(
    mapper: Mapper, connection: Connection, workout: Workout
) -> None:
    if object_session(workout).is_modified(workout, include_collections=True):

        @listens_for(db.Session, 'after_flush', once=True)
        def receive_after_flush(session: Session, context: Any) -> None:
            if workout.equipments:
                update_equipments(workout, connection)
            sports_list = [workout.sport_id]
            records = Record.query.filter_by(workout_id=workout.id).all()
            for rec in records:
                if rec.sport_id not in sports_list:
                    sports_list.append(rec.sport_id)
            for sport_id in sports_list:
                update_records(workout.user_id, sport_id, connection, session)


@listens_for(Workout, 'after_delete')
def on_workout_delete(
    mapper: Mapper, connection: Connection, old_workout: 'Workout'
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        from fittrackee.users.models import Notification

        # Equipments must be removed before deleting workout
        # in order to recalculate equipments totals
        if old_workout.equipments:
            raise Exception("equipments exists, remove them first")

        if old_workout.map:
            try:
                os.remove(get_absolute_file_path(old_workout.map))
            except OSError:
                appLog.error('map file not found when deleting workout')
        if old_workout.gpx:
            try:
                os.remove(get_absolute_file_path(old_workout.gpx))
            except OSError:
                appLog.error('gpx file not found when deleting workout')

        Notification.query.filter(
            Notification.event_object_id == old_workout.id,
            Notification.to_user_id == old_workout.user_id,
            Notification.event_type.in_(
                [
                    'workout_comment',
                    'workout_like',
                ]
            ),
        ).delete()


@listens_for(Workout.equipments, 'append')
def on_workout_equipments_append(
    target: Workout, value: 'Equipment', initiator: 'AttributeEvent'
) -> None:
    value.total_distance = float(value.total_distance) + float(target.distance)
    value.total_duration += target.duration
    if target.moving:
        value.total_moving += target.moving
    value.total_workouts += 1


@listens_for(Workout.equipments, 'remove')
def on_workout_equipments_remove(
    target: Workout, value: 'Equipment', initiator: 'AttributeEvent'
) -> None:
    value.total_distance = float(value.total_distance) - float(target.distance)
    value.total_duration -= target.duration
    if target.moving:
        value.total_moving -= target.moving
    value.total_workouts -= 1


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
        db.Index('workout_records', 'workout_id', 'record_type'),
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
    workout_date = db.Column(TZDateTime, nullable=False)
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
    def value(self) -> Optional[Union[timedelta, float]]:
        if self._value is None:
            return None
        if self.record_type == 'LD':
            return timedelta(seconds=self._value)
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
    created_at = db.Column(TZDateTime, nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id', ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user = db.relationship("User", lazy=True)
    workout = db.relationship("Workout", lazy=True)

    def __init__(
        self,
        user_id: int,
        workout_id: int,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.user_id = user_id
        self.workout_id = workout_id
        self.created_at = (
            datetime.now(timezone.utc) if created_at is None else created_at
        )


@listens_for(WorkoutLike, 'after_insert')
def on_workout_like_insert(
    mapper: Mapper, connection: Connection, new_workout_like: WorkoutLike
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        from fittrackee.users.models import Notification, User

        workout = Workout.query.filter_by(
            id=new_workout_like.workout_id
        ).first()
        if new_workout_like.user_id != workout.user_id:
            to_user = User.query.filter_by(id=workout.user_id).first()
            if not to_user.is_notification_enabled('workout_like'):
                return

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
