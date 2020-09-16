from fittrackee_api import db
from flask import current_app
from sqlalchemy.event import listens_for

from ..users.models import User


class AppConfig(db.Model):
    __tablename__ = 'app_config'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    max_users = db.Column(db.Integer, default=0, nullable=False)
    gpx_limit_import = db.Column(db.Integer, default=10, nullable=False)
    max_single_file_size = db.Column(
        db.Integer, default=1048576, nullable=False
    )
    max_zip_file_size = db.Column(db.Integer, default=10485760, nullable=False)

    @property
    def is_registration_enabled(self):
        nb_users = User.query.count()
        return self.max_users == 0 or nb_users < self.max_users

    @property
    def map_attribution(self):
        return current_app.config['TILE_SERVER']['ATTRIBUTION']

    def serialize(self):
        return {
            "gpx_limit_import": self.gpx_limit_import,
            "is_registration_enabled": self.is_registration_enabled,
            "max_single_file_size": self.max_single_file_size,
            "max_zip_file_size": self.max_zip_file_size,
            "max_users": self.max_users,
            "map_attribution": self.map_attribution,
        }


def update_app_config():
    config = AppConfig.query.first()
    if config:
        current_app.config[
            'is_registration_enabled'
        ] = config.is_registration_enabled


@listens_for(User, 'after_insert')
def on_user_insert(mapper, connection, user):
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        update_app_config()


@listens_for(User, 'after_delete')
def on_user_delete(mapper, connection, old_user):
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        update_app_config()
