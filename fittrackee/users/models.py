import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

import jwt
from flask import current_app
from jsonschema import validate
from sqlalchemy import and_, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session, object_session
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import select
from sqlalchemy.types import Enum

from fittrackee import BaseModel, appLog, bcrypt, db
from fittrackee.comments.models import Comment
from fittrackee.database import TZDateTime
from fittrackee.dates import aware_utc_now
from fittrackee.files import get_absolute_file_path
from fittrackee.utils import encode_uuid
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.constants import SPORTS_WITHOUT_ELEVATION_DATA
from fittrackee.workouts.models import Workout

from .constants import (
    NOTIFICATION_TYPES,
    NOTIFICATIONS_PREFERENCES_SCHEMA,
    USER_LINK_TEMPLATE,
)
from .exceptions import (
    BlockUserException,
    FollowRequestAlreadyProcessedError,
    FollowRequestAlreadyRejectedError,
    InvalidNotificationTypeException,
    NotExistingFollowRequestError,
    UserTaskException,
    UserTaskForbiddenException,
)
from .roles import (
    UserRole,
    has_admin_rights,
    has_moderator_rights,
    is_auth_user,
)
from .utils.tokens import decode_user_token, get_user_token

if TYPE_CHECKING:
    from fittrackee.equipments.models import Equipment
    from fittrackee.reports.models import ReportAction
    from fittrackee.workouts.models import Record


TASK_TYPES = [
    "user_data_export",
    "workouts_archive_upload",
]

SEGMENTS_CREATION_EVENTS = [
    "all",
    "none",
    "only_manual",
]


class FollowRequest(BaseModel):
    """Follow request between two users"""

    __tablename__ = "follow_requests"
    follower_user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id"),
        primary_key=True,
    )
    followed_user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id"),
        primary_key=True,
    )
    is_approved: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, default=aware_utc_now
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TZDateTime, nullable=True
    )

    to_user: Mapped["User"] = relationship(
        "User",
        primaryjoin="FollowRequest.followed_user_id == User.id",
        uselist=False,
        back_populates="received_follow_requests",
    )
    from_user: Mapped["User"] = relationship(
        "User",
        primaryjoin="FollowRequest.follower_user_id == User.id",
        uselist=False,
        back_populates="sent_follow_requests",
    )

    def __repr__(self) -> str:
        return (
            f"<FollowRequest from user '{self.follower_user_id}' "
            f"to user '{self.followed_user_id}'>"
        )

    def __init__(self, follower_user_id: int, followed_user_id: int):
        self.follower_user_id = follower_user_id
        self.followed_user_id = followed_user_id

    def is_rejected(self) -> bool:
        return not self.is_approved and self.updated_at is not None

    def serialize(self) -> Dict:
        return {
            "from_user": self.from_user.serialize(),
            "to_user": self.to_user.serialize(),
        }


@listens_for(FollowRequest, "after_insert")
def on_follow_request_insert(
    mapper: Mapper, connection: Connection, new_follow_request: FollowRequest
) -> None:
    @listens_for(db.Session, "after_flush", once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        to_user = User.query.filter_by(
            id=new_follow_request.followed_user_id
        ).first()
        if not to_user:
            return
        event_type = (
            "follow" if new_follow_request.is_approved else "follow_request"
        )

        if not to_user.is_notification_enabled(event_type):
            return

        notification = Notification(
            from_user_id=new_follow_request.follower_user_id,
            to_user_id=new_follow_request.followed_user_id,
            created_at=new_follow_request.created_at,
            event_type=event_type,
        )
        session.add(notification)


@listens_for(FollowRequest, "after_update")
def on_follow_request_update(
    mapper: Mapper, connection: Connection, follow_request: FollowRequest
) -> None:
    follow_request_object = object_session(follow_request)
    if follow_request_object and follow_request_object.is_modified(
        follow_request
    ):

        @listens_for(db.Session, "after_flush", once=True)
        def receive_after_flush(session: Session, context: Connection) -> None:
            if follow_request.is_approved:
                if follow_request.to_user.is_notification_enabled("follow"):
                    follow_request_notification = Notification.query.filter_by(
                        from_user_id=follow_request.follower_user_id,
                        to_user_id=follow_request.followed_user_id,
                        event_type="follow_request",
                    ).first()

                    if follow_request_notification:
                        notification_table = Notification.__table__  # type: ignore
                        connection.execute(
                            notification_table.update()
                            .where(
                                notification_table.c.from_user_id
                                == follow_request.follower_user_id,
                                notification_table.c.to_user_id
                                == follow_request.followed_user_id,
                                notification_table.c.event_type
                                == "follow_request",
                            )
                            .values(
                                event_type="follow",
                                marked_as_read=False,
                            )
                        )
                    else:
                        follow_notification = Notification(
                            from_user_id=follow_request.follower_user_id,
                            to_user_id=follow_request.followed_user_id,
                            created_at=datetime.now(timezone.utc),
                            event_type="follow",
                        )
                        session.add(follow_notification)

                if follow_request.from_user.is_notification_enabled(
                    "follow_request_approved"
                ):
                    notification = Notification(
                        from_user_id=follow_request.followed_user_id,
                        to_user_id=follow_request.follower_user_id,
                        created_at=datetime.now(timezone.utc),
                        event_type="follow_request_approved",
                    )
                    session.add(notification)

            if (
                not follow_request.is_approved
                and follow_request.updated_at is not None
            ):
                Notification.query.filter_by(
                    from_user_id=follow_request.follower_user_id,
                    to_user_id=follow_request.followed_user_id,
                    event_type="follow_request",
                ).delete()


@listens_for(FollowRequest, "after_delete")
def on_follow_request_delete(
    mapper: Mapper, connection: Connection, old_follow_request: FollowRequest
) -> None:
    @listens_for(db.Session, "after_flush", once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        Notification.query.filter(
            Notification.from_user_id == old_follow_request.follower_user_id,
            Notification.to_user_id == old_follow_request.followed_user_id,
            Notification.event_type.in_(["follow", "follow_request"]),
        ).delete()
        Notification.query.filter(
            Notification.from_user_id == old_follow_request.followed_user_id,
            Notification.to_user_id == old_follow_request.follower_user_id,
            Notification.event_type == "follow_request_approved",
        ).delete()


class BlockedUser(BaseModel):
    __tablename__ = "blocked_users"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "by_user_id", name="blocked_users_unique"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    by_user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False)

    def __init__(
        self,
        user_id: int,
        by_user_id: int,
        created_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.by_user_id = by_user_id
        self.created_at = (
            datetime.now(timezone.utc) if created_at is None else created_at
        )


class User(BaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        db.String(255), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        db.String(255), unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(
        db.String(80), nullable=True
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        db.String(80), nullable=True
    )
    birth_date: Mapped[Optional[datetime]] = mapped_column(
        TZDateTime, nullable=True
    )
    location: Mapped[Optional[str]] = mapped_column(
        db.String(80), nullable=True
    )
    bio: Mapped[Optional[str]] = mapped_column(db.String(200), nullable=True)
    picture: Mapped[Optional[str]] = mapped_column(
        db.String(255), nullable=True
    )
    timezone: Mapped[Optional[str]] = mapped_column(
        db.String(50), nullable=True
    )
    date_format: Mapped[Optional[str]] = mapped_column(
        db.String(50), nullable=True
    )
    # weekm: does the week start Monday?
    weekm: Mapped[bool] = mapped_column(default=False, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(
        db.String(50), nullable=True
    )
    imperial_units: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
    email_to_confirm: Mapped[Optional[str]] = mapped_column(
        db.String(255), nullable=True
    )
    confirmation_token: Mapped[Optional[str]] = mapped_column(
        db.String(255), nullable=True
    )
    display_ascent: Mapped[bool] = mapped_column(default=True, nullable=False)
    accepted_policy_date: Mapped[Optional[datetime]] = mapped_column(
        TZDateTime, nullable=True
    )
    start_elevation_at_zero: Mapped[bool] = mapped_column(
        default=True, nullable=False
    )
    use_raw_gpx_speed: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    use_dark_mode: Mapped[Optional[bool]] = mapped_column(
        default=False, nullable=True
    )
    manually_approves_followers: Mapped[bool] = mapped_column(
        default=True, nullable=False
    )
    hide_profile_in_users_directory: Mapped[bool] = mapped_column(
        default=True, nullable=False
    )
    workouts_visibility: Mapped[VisibilityLevel] = mapped_column(
        Enum(VisibilityLevel, name="visibility_levels"),
        server_default="PRIVATE",
        nullable=False,
    )
    map_visibility: Mapped[VisibilityLevel] = mapped_column(
        Enum(VisibilityLevel, name="visibility_levels"),
        server_default="PRIVATE",
        nullable=False,
    )
    suspended_at: Mapped[Optional[datetime]] = mapped_column(
        TZDateTime, nullable=True
    )
    role: Mapped[int] = mapped_column(
        CheckConstraint(
            f"role IN ({', '.join(UserRole.db_values())})",
            name="ck_users_role",
        ),
        nullable=False,
        default=UserRole.USER.value,
    )
    analysis_visibility: Mapped[VisibilityLevel] = mapped_column(
        Enum(VisibilityLevel, name="visibility_levels"),
        server_default="PRIVATE",
        nullable=False,
    )
    notification_preferences: Mapped[Optional[Dict]] = mapped_column(
        postgresql.JSONB, nullable=True
    )
    hr_visibility: Mapped[VisibilityLevel] = mapped_column(
        Enum(VisibilityLevel, name="visibility_levels"),
        server_default="PRIVATE",
        nullable=False,
    )
    segments_creation_event: Mapped[str] = mapped_column(
        Enum(*SEGMENTS_CREATION_EVENTS, name="segments_creation_events"),
        server_default="only_manual",
    )
    split_workout_charts: Mapped[bool] = mapped_column(
        server_default="false", nullable=False
    )

    workouts: Mapped[List["Workout"]] = relationship(
        "Workout", lazy=True, back_populates="user"
    )
    records: Mapped[List["Record"]] = relationship(
        "Record", lazy=True, back_populates="user"
    )
    equipments: Mapped[List["Equipment"]] = relationship(
        "Equipment", lazy="select", back_populates="user"
    )
    received_follow_requests = relationship(
        FollowRequest,
        back_populates="to_user",
        primaryjoin=id == FollowRequest.followed_user_id,
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    sent_follow_requests = relationship(
        FollowRequest,
        back_populates="from_user",
        primaryjoin=id == FollowRequest.follower_user_id,
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    followers = relationship(
        "User",
        secondary="follow_requests",
        primaryjoin=and_(
            id == FollowRequest.followed_user_id,
            FollowRequest.is_approved == True,  # noqa
        ),
        secondaryjoin=and_(
            id == FollowRequest.follower_user_id,
            suspended_at == None,  # noqa
        ),
        lazy="dynamic",
        viewonly=True,
    )
    following = relationship(
        "User",
        secondary="follow_requests",
        primaryjoin=and_(
            id == FollowRequest.follower_user_id,
            FollowRequest.is_approved == True,  # noqa
        ),
        secondaryjoin=and_(
            id == FollowRequest.followed_user_id,
            suspended_at == None,  # noqa
        ),
        lazy="dynamic",
        viewonly=True,
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        lazy=True,
        back_populates="user",
        cascade="all, delete-orphan",
    )
    blocked_users = relationship(
        "BlockedUser",
        primaryjoin=id == BlockedUser.by_user_id,
        lazy="dynamic",
        viewonly=True,
    )
    blocked_by_users = relationship(
        "BlockedUser",
        primaryjoin=id == BlockedUser.user_id,
        lazy="dynamic",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f"<User {self.username!r}>"

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
            password, current_app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode()
        self.created_at = (
            datetime.now(timezone.utc) if created_at is None else created_at
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
                return "blacklisted token, please log in again"
            return resp
        except jwt.ExpiredSignatureError:
            return "signature expired, please log in again"
        except jwt.InvalidTokenError:
            return "invalid token, please log in again"

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def generate_password_hash(new_password: str) -> str:
        return bcrypt.generate_password_hash(
            new_password, current_app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode()

    def get_user_id(self) -> int:
        return self.id

    @property
    def has_moderator_rights(self) -> bool:
        return has_moderator_rights(UserRole(self.role))

    @property
    def has_admin_rights(self) -> bool:
        return has_admin_rights(UserRole(self.role))

    @hybrid_property
    def workouts_count(self) -> int:
        return Workout.query.filter(Workout.user_id == self.id).count()

    @workouts_count.expression  # type: ignore
    def workouts_count(self) -> int:
        return (
            select(func.count(Workout.id))
            .where(Workout.user_id == self.id)
            .label("workouts_count")
        )

    @property
    def pending_follow_requests(self) -> List[FollowRequest]:
        return self.received_follow_requests.filter_by(updated_at=None).all()

    def send_follow_request_to(self, target: "User") -> FollowRequest:
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
            follow_request.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        return follow_request

    def unfollows(self, target: "User") -> None:
        existing_follow_request = FollowRequest.query.filter_by(
            follower_user_id=self.id, followed_user_id=target.id
        ).first()
        if not existing_follow_request:
            raise NotExistingFollowRequestError()

        db.session.delete(existing_follow_request)
        db.session.commit()
        return None

    def undoes_follow(self, follower: "User") -> None:
        existing_follow_request = FollowRequest.query.filter_by(
            followed_user_id=self.id, follower_user_id=follower.id
        ).first()
        if not existing_follow_request:
            raise NotExistingFollowRequestError()
        db.session.delete(existing_follow_request)
        db.session.commit()
        return None

    def _processes_follow_request_from(
        self, user: "User", approved: bool
    ) -> FollowRequest:
        follow_request = FollowRequest.query.filter_by(
            follower_user_id=user.id, followed_user_id=self.id
        ).first()
        if not follow_request:
            raise NotExistingFollowRequestError()
        if follow_request.updated_at is not None:
            raise FollowRequestAlreadyProcessedError()
        follow_request.is_approved = approved
        follow_request.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return follow_request

    def approves_follow_request_from(self, user: "User") -> FollowRequest:
        follow_request = self._processes_follow_request_from(
            user=user, approved=True
        )
        return follow_request

    def rejects_follow_request_from(self, user: "User") -> FollowRequest:
        follow_request = self._processes_follow_request_from(
            user=user, approved=False
        )
        return follow_request

    @staticmethod
    def follow_request_status(follow_request: Optional[FollowRequest]) -> str:
        if follow_request is None:
            return "false"
        if follow_request.is_approved:
            return "true"
        return "pending"

    def is_followed_by(self, user: "User") -> str:
        follow_request = FollowRequest.query.filter_by(
            follower_user_id=user.id, followed_user_id=self.id
        ).first()
        return self.follow_request_status(follow_request)

    def follows(self, user: "User") -> str:
        follow_request = FollowRequest.query.filter_by(
            follower_user_id=self.id, followed_user_id=user.id
        ).first()
        return self.follow_request_status(follow_request)

    def get_following_user_ids(self) -> List:
        return [following.id for following in self.following]

    def get_followers_user_ids(self) -> List:
        return [followers.id for followers in self.followers]

    def get_user_url(self) -> str:
        """Return user url on user interface"""
        return f"{current_app.config['UI_URL']}/users/{self.username}"

    def linkify_mention(self) -> str:
        return USER_LINK_TEMPLATE.format(
            profile_url=self.get_user_url(), username=f"@{self.username}"
        )

    def blocks_user(self, user: "User") -> None:
        if self.id == user.id:
            raise BlockUserException()

        db.session.execute(
            postgresql.insert(BlockedUser)
            .values(
                user_id=user.id,
                by_user_id=self.id,
                created_at=datetime.now(timezone.utc),
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

    def unblocks_user(self, user: "User") -> None:
        BlockedUser.query.filter_by(
            user_id=user.id, by_user_id=self.id
        ).delete()
        db.session.commit()

    def is_blocked_by(self, user: "User") -> bool:
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
    def suspension_action(self) -> Optional["ReportAction"]:
        if self.suspended_at is None:
            return None

        from fittrackee.reports.models import ReportAction

        return (
            ReportAction.query.filter(
                ReportAction.user_id == self.id,
                ReportAction.action_type == "user_suspension",
            )
            .order_by(ReportAction.created_at.desc())
            .first()
        )

    @property
    def sanctions_count(self) -> int:
        from fittrackee.reports.models import ReportAction

        return (
            ReportAction.query.filter(
                ReportAction.user_id == self.id,
                ReportAction.action_type.not_in(
                    [
                        "comment_unsuspension",
                        "user_unsuspension",
                        "user_warning_lifting",
                        "workout_unsuspension",
                    ]
                ),
            )
            .order_by(ReportAction.created_at.desc())
            .count()
        )

    @property
    def all_reports_count(self) -> Dict[str, int]:
        query = """
        SELECT (
                SELECT COUNT(*) AS created_reports_count
                FROM reports
                WHERE reports.reported_by = :user_id
            ),
            (
                SELECT COUNT(*) AS reported_count
                FROM reports
                WHERE reports.reported_user_id = :user_id
            ),
            (
                SELECT COUNT(*) AS sanctions_count
                FROM report_actions
                WHERE report_actions.user_id = :user_id
                  AND report_actions.action_type NOT IN (
                     'comment_unsuspension',
                     'user_unsuspension',
                     'user_warning_lifting',
                     'workout_unsuspension'
                )
        );"""
        result = db.session.execute(text(query), {"user_id": self.id}).one()
        return {
            "created_reports_count": result[0],
            "reported_count": result[1],
            "sanctions_count": result[2],
        }

    def update_preferences(self, updated_preferences: Dict) -> None:
        notification_preferences = {
            **(
                self.notification_preferences
                if self.notification_preferences
                else {}
            ),
            **updated_preferences,
        }
        validate(
            instance=notification_preferences,
            schema=NOTIFICATIONS_PREFERENCES_SCHEMA,
        )
        self.notification_preferences = notification_preferences
        db.session.commit()

    def is_notification_enabled(self, notification_type: str) -> bool:
        if not self.notification_preferences:
            return True
        return self.notification_preferences.get(notification_type, True)

    def serialize(
        self,
        *,
        current_user: Optional["User"] = None,
        light: bool = True,
    ) -> Dict:
        if current_user is None:
            role = None
        else:
            role = (
                UserRole.AUTH_USER
                if current_user.id == self.id
                else UserRole(current_user.role)
            )

        serialized_user: Dict = {
            "created_at": self.created_at,
            "followers": self.followers.count(),
            "following": self.following.count(),
            "nb_workouts": self.workouts_count,
            "picture": self.picture is not None,
            "role": UserRole(self.role).name.lower(),
            "suspended_at": self.suspended_at,
            "username": self.username,
        }
        if is_auth_user(role) or has_moderator_rights(role):
            serialized_user["is_active"] = self.is_active
            serialized_user["email"] = self.email
        if (
            has_moderator_rights(role)
            and self.suspended_at
            and self.suspension_action
        ):
            serialized_user["suspension_report_id"] = (
                self.suspension_action.report_id
            )

        if current_user is not None and not is_auth_user(role):
            serialized_user["follows"] = self.follows(current_user)
            serialized_user["is_followed_by"] = self.is_followed_by(
                current_user
            )
            serialized_user["blocked"] = self.is_blocked_by(current_user)

        if light or not role:
            return serialized_user

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
            **serialized_user,
            "bio": self.bio,
            "birth_date": self.birth_date,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "location": self.location,
        }

        if role is not None:
            total = (0, "0:00:00", 0)
            if self.workouts_count > 0:  # type: ignore
                total = tuple(
                    db.session.query(
                        func.sum(Workout.distance),
                        func.sum(Workout.moving),
                        func.sum(Workout.ascent),
                    )
                    .filter(Workout.user_id == self.id)
                    .one()
                )

            serialized_user["nb_sports"] = len(sports)
            serialized_user["records"] = [
                record.serialize()
                for record in self.records
                if (
                    record.sport.label not in SPORTS_WITHOUT_ELEVATION_DATA
                    or record.record_type != "HA"
                )
            ]
            serialized_user["sports_list"] = [
                sport for sportslist in sports for sport in sportslist
            ]
            serialized_user["total_ascent"] = (
                float(total[2]) if total[2] else 0.0
            )
            serialized_user["total_distance"] = float(total[0])
            serialized_user["total_duration"] = str(total[1])

        if is_auth_user(role) or has_admin_rights(role):
            serialized_user["email_to_confirm"] = self.email_to_confirm

        if current_user and has_moderator_rights(UserRole(current_user.role)):
            reports_count = self.all_reports_count
            serialized_user["created_reports_count"] = reports_count[
                "created_reports_count"
            ]
            serialized_user["reported_count"] = reports_count["reported_count"]
            serialized_user["sanctions_count"] = reports_count[
                "sanctions_count"
            ]

        if is_auth_user(role):
            accepted_privacy_policy = None
            if self.accepted_policy_date:
                accepted_privacy_policy = (
                    current_app.config["privacy_policy_date"]
                    < self.accepted_policy_date
                )
            serialized_user = {
                **serialized_user,
                **{
                    "accepted_privacy_policy": accepted_privacy_policy,
                    "date_format": self.date_format,
                    "display_ascent": self.display_ascent,
                    "imperial_units": self.imperial_units,
                    "language": self.language,
                    "start_elevation_at_zero": self.start_elevation_at_zero,
                    "timezone": self.timezone,
                    "use_dark_mode": self.use_dark_mode,
                    "use_raw_gpx_speed": self.use_raw_gpx_speed,
                    "weekm": self.weekm,
                    "map_visibility": self.map_visibility.value,
                    "analysis_visibility": self.analysis_visibility.value,
                    "workouts_visibility": self.workouts_visibility.value,
                    "hr_visibility": self.hr_visibility.value,
                    "segments_creation_event": self.segments_creation_event,
                    "manually_approves_followers": (
                        self.manually_approves_followers
                    ),
                    "hide_profile_in_users_directory": (
                        self.hide_profile_in_users_directory
                    ),
                    "sanctions_count": self.sanctions_count,
                    "notification_preferences": (
                        self.notification_preferences
                        if self.notification_preferences
                        else {}
                    ),
                    "split_workout_charts": self.split_workout_charts,
                },
            }

        return serialized_user


UserSportPreferenceEquipment = db.Table(
    "users_sports_preferences_equipments",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "sport_id",
        db.Integer,
        db.ForeignKey("sports.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "equipment_id",
        db.Integer,
        db.ForeignKey("equipments.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class UserSportPreference(BaseModel):
    __tablename__ = "users_sports_preferences"

    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id"),
        primary_key=True,
    )
    sport_id: Mapped[int] = mapped_column(
        db.ForeignKey("sports.id"),
        primary_key=True,
    )
    color: Mapped[Optional[str]] = mapped_column(db.String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    stopped_speed_threshold: Mapped[float] = mapped_column(
        default=1.0, nullable=False
    )

    default_equipments = relationship(
        "Equipment",
        secondary=UserSportPreferenceEquipment,
        primaryjoin=and_(
            user_id == UserSportPreferenceEquipment.c.user_id,
            sport_id == UserSportPreferenceEquipment.c.sport_id,
        ),
        lazy="dynamic",
        viewonly=True,
        back_populates="default_for_sports",
    )
    user: Mapped["User"] = relationship("User", lazy=True)

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
            "user_id": self.user_id,
            "sport_id": self.sport_id,
            "color": self.color,
            "is_active": self.is_active,
            "stopped_speed_threshold": self.stopped_speed_threshold,
            "default_equipments": [
                equipment.serialize(current_user=self.user)
                for equipment in self.default_equipments.all()
            ],
        }


class BlacklistedToken(BaseModel):
    __tablename__ = "blacklisted_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(
        db.String(500), unique=True, nullable=False
    )
    expired_at: Mapped[int] = mapped_column(nullable=False)
    blacklisted_on: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False
    )

    def __init__(
        self, token: str, blacklisted_on: Optional[datetime] = None
    ) -> None:
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
        self.token = token
        self.expired_at = payload["exp"]
        self.blacklisted_on = (
            blacklisted_on if blacklisted_on else datetime.now(timezone.utc)
        )

    @classmethod
    def check(cls, auth_token: str) -> bool:
        return cls.query.filter_by(token=str(auth_token)).first() is not None


class UserTask(BaseModel):
    __tablename__ = "user_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, nullable=False, default=aware_utc_now
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TZDateTime, nullable=True, onupdate=aware_utc_now
    )
    task_type: Mapped[str] = mapped_column(
        Enum(*TASK_TYPES, name="task_types"), index=True
    )
    progress: Mapped[int] = mapped_column(nullable=False, default=0)
    errored: Mapped[bool] = mapped_column(nullable=False, default=False)
    aborted: Mapped[bool] = mapped_column(nullable=False, default=False)
    # can be input or output file
    file_size: Mapped[Optional[int]] = mapped_column(nullable=True)
    # relative or absolute path
    file_path: Mapped[Optional[str]] = mapped_column(
        db.String(255), nullable=True
    )
    errors: Mapped[Dict] = mapped_column(
        postgresql.JSONB, nullable=False, server_default="{}"
    )
    data: Mapped[Dict] = mapped_column(
        postgresql.JSONB, nullable=False, server_default="{}"
    )
    message_id: Mapped[Optional[str]] = mapped_column(
        db.String(36), nullable=True
    )

    def __init__(
        self,
        user_id: int,
        task_type: str,
        created_at: Optional[datetime] = None,
        data: Optional[Dict] = None,
        file_path: Optional[str] = None,
    ):
        self.user_id = user_id
        self.task_type = task_type
        self.created_at = (
            datetime.now(timezone.utc) if created_at is None else created_at
        )
        self.data = data if data else {}
        self.file_path = file_path
        if task_type == "workouts_archive_upload":
            self.errors = {
                "archive": None,
                "files": {},
            }

    @property
    def completed(self) -> bool:
        return self.progress == 100

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    def _get_user_data_export(
        self, serialized_task: Dict, *, for_admin: bool = False
    ) -> Dict:
        serialized_task = {
            **serialized_task,
            "file_size": (
                self.file_size
                if self.status == "successful" and self.file_size is not None
                else None
            ),
        }

        if for_admin:
            return serialized_task

        return {
            **serialized_task,
            "file_name": (
                self.file_path.split("/")[-1]
                if self.status == "successful" and self.file_path
                else None
            ),
        }

    @property
    def status(self) -> str:
        if self.errored:
            return "errored"
        elif self.aborted:
            return "aborted"
        elif self.progress == 0:
            return "queued"
        elif self.progress == 100:
            return "successful"
        return "in_progress"

    def _get_workouts_archive_upload(
        self, serialized_task: Dict, *, for_admin: bool = False
    ) -> Dict:
        total_files = len(self.data.get("files_to_process", []))

        serialized_task = {
            **serialized_task,
            "file_size": self.file_size,
            "files_count": total_files,
        }

        if for_admin:
            return serialized_task

        serialized_task = {
            **serialized_task,
            "sport_id": self.data.get("workouts_data", {}).get("sport_id"),
            "errored_files": self.errors,
            "new_workouts_count": self.data.get("new_workouts_count", 0),
            "progress": self.progress,
            "original_file_name": self.data.get("original_file_name"),
            "updated_at": self.updated_at,
        }
        return serialized_task

    def serialize(
        self,
        *,
        current_user: "User",
        for_admin: bool = False,
        task_user: Optional["User"] = None,
    ) -> Dict:
        if (
            current_user.id != self.user_id
            and not current_user.has_admin_rights
        ):
            raise UserTaskForbiddenException()

        if task_user and task_user.id != self.user_id:
            raise UserTaskException("invalid tasks user")

        serialized_task = {
            "id": self.short_id,
            "created_at": self.created_at,
            "status": self.status,
            "type": self.task_type,
        }

        if current_user.has_admin_rights and for_admin:
            serialized_task["message_id"] = self.message_id
            if task_user:
                serialized_task["user"] = task_user.serialize(
                    current_user=current_user, light=True
                )

        if self.task_type == "user_data_export":
            return self._get_user_data_export(
                serialized_task, for_admin=for_admin
            )

        return self._get_workouts_archive_upload(
            serialized_task, for_admin=for_admin
        )


@listens_for(UserTask, "after_delete")
def on_user_task_delete(
    mapper: Mapper, connection: Connection, old_record: "UserTask"
) -> None:
    @listens_for(db.Session, "after_flush", once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        Notification.query.filter(
            Notification.event_object_id == old_record.id,
        ).delete()
        if old_record.file_path:
            try:
                os.remove(get_absolute_file_path(old_record.file_path))
            except OSError:
                appLog.error("archive found when deleting export request")


class Notification(BaseModel):
    __tablename__ = "notifications"
    __table_args__ = (
        db.UniqueConstraint(
            "from_user_id",
            "to_user_id",
            "event_type",
            "event_object_id",
            name="users_event_unique",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )
    from_user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    to_user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(TZDateTime, nullable=False)
    marked_as_read: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=False
    )
    event_object_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    event_type: Mapped[str] = mapped_column(db.String(50), nullable=False)

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

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    def serialize(self) -> Dict:
        serialized_notification = {
            "created_at": self.created_at,
            "id": self.short_id,
            "marked_as_read": self.marked_as_read,
            "type": self.event_type,
        }

        if self.event_type in ["follow", "follow_request"]:
            follow_request = FollowRequest.query.filter_by(
                follower_user_id=self.from_user_id,
                followed_user_id=self.to_user_id,
            ).one()
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

        if self.event_type in [
            "comment_suspension",
            "comment_unsuspension",
            "user_warning",
            "user_warning_lifting",
            "workout_suspension",
            "workout_unsuspension",
        ]:
            from_user = None
        else:
            from_user = User.query.filter_by(id=self.from_user_id).first()
        to_user = User.query.filter_by(id=self.to_user_id).first()
        serialized_notification = {
            **serialized_notification,
            "from": (
                from_user.serialize(current_user=to_user)
                if from_user
                else None
            ),
        }

        if self.event_type == "workout_like":
            workout = Workout.query.filter_by(id=self.event_object_id).one()
            serialized_notification["workout"] = workout.serialize(
                user=to_user
            )

        if self.event_type in [
            "comment_like",
            "mention",
            "workout_comment",
        ]:
            comment = Comment.query.filter_by(id=self.event_object_id).one()
            serialized_notification["comment"] = comment.serialize(
                user=to_user
            )

        if self.event_type in [
            "report",
            "suspension_appeal",
            "user_warning_appeal",
        ]:
            from fittrackee.reports.models import Report, ReportActionAppeal

            if self.event_type in ["suspension_appeal", "user_warning_appeal"]:
                appeal = ReportActionAppeal.query.filter_by(
                    id=self.event_object_id
                ).one()
                report = Report.query.filter_by(
                    id=appeal.action.report_id
                ).one()
            else:
                report = Report.query.filter_by(id=self.event_object_id).one()
            serialized_notification["report"] = report.serialize(
                current_user=to_user
            )

        if self.event_type in [
            "comment_suspension",
            "comment_unsuspension",
            "user_warning",
            "user_warning_lifting",
            "workout_suspension",
            "workout_unsuspension",
        ]:
            from fittrackee.reports.models import Report, ReportAction

            report_action = ReportAction.query.filter_by(
                id=self.event_object_id
            ).one()
            serialized_notification["report_action"] = report_action.serialize(
                current_user=to_user
            )
            report = Report.query.filter_by(id=report_action.report_id).one()
            if report.object_type == "comment":
                comment = Comment.query.filter_by(
                    id=report.reported_comment_id
                ).first()
                serialized_notification["comment"] = (
                    comment.serialize(user=to_user) if comment else None
                )
            elif report.object_type == "workout":
                workout = Workout.query.filter_by(
                    id=report.reported_workout_id
                ).first()
                serialized_notification["workout"] = (
                    workout.serialize(user=to_user) if workout else None
                )

        if self.event_type == "workouts_archive_upload":
            task = UserTask.query.filter_by(id=self.event_object_id).first()
            if task:
                serialized_notification["task"] = {
                    "id": task.short_id,
                    "original_file_name": task.data.get("original_file_name"),
                }

        return serialized_notification
