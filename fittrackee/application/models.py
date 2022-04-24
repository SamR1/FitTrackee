from typing import Dict

from flask import current_app
from sqlalchemy import exc
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session

from fittrackee import VERSION, db
from fittrackee.users.models import User

BaseModel: DeclarativeMeta = db.Model


class AppConfig(BaseModel):
    __tablename__ = 'app_config'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    max_users = db.Column(db.Integer, default=0, nullable=False)
    gpx_limit_import = db.Column(db.Integer, default=10, nullable=False)
    max_single_file_size = db.Column(
        db.Integer, default=1048576, nullable=False
    )
    max_zip_file_size = db.Column(db.Integer, default=10485760, nullable=False)
    admin_contact = db.Column(db.String(255), nullable=True)

    @property
    def is_registration_enabled(self) -> bool:
        try:
            nb_users = User.query.count()
        except exc.ProgrammingError as e:
            # workaround for user model related migrations
            if 'psycopg2.errors.UndefinedColumn' in str(e):
                result = db.engine.execute("SELECT COUNT(*) FROM users;")
                nb_users = result.fetchone()[0]
            else:
                raise e
        return self.max_users == 0 or nb_users < self.max_users

    @property
    def map_attribution(self) -> str:
        return current_app.config['TILE_SERVER']['ATTRIBUTION']

    def serialize(self) -> Dict:
        return {
            'admin_contact': self.admin_contact,
            'gpx_limit_import': self.gpx_limit_import,
            'is_email_sending_enabled': current_app.config['CAN_SEND_EMAILS'],
            'is_registration_enabled': self.is_registration_enabled,
            'max_single_file_size': self.max_single_file_size,
            'max_zip_file_size': self.max_zip_file_size,
            'max_users': self.max_users,
            'map_attribution': self.map_attribution,
            'version': VERSION,
        }


def update_app_config() -> None:
    config = AppConfig.query.first()
    if config:
        current_app.config[
            'is_registration_enabled'
        ] = config.is_registration_enabled


@listens_for(User, 'after_insert')
def on_user_insert(mapper: Mapper, connection: Connection, user: User) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        update_app_config()


@listens_for(User, 'after_delete')
def on_user_delete(
    mapper: Mapper, connection: Connection, old_user: User
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        update_app_config()
