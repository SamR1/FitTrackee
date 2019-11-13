from fittrackee_api import db

from ..users.models import User


class AppConfig(db.Model):
    __tablename__ = 'app_config'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registration = db.Column(db.Boolean, default=False, nullable=False)
    max_users = db.Column(db.Integer, default=0, nullable=False)
    gpx_limit_import = db.Column(db.Integer, default=10, nullable=False)
    max_single_file_size = db.Column(
        db.Integer, default=1048576, nullable=False
    )
    max_zip_file_size = db.Column(db.Integer, default=10485760, nullable=False)

    @property
    def is_registration_enabled(self):
        nb_users = User.query.count()
        return self.registration and nb_users < self.max_users

    def serialize(self):
        return {
            "gpx_limit_import": self.gpx_limit_import,
            "is_registration_enabled": self.is_registration_enabled,
            "max_single_file_size": self.max_single_file_size,
            "max_zip_file_size": self.max_zip_file_size,
            "max_users": self.max_users,
            "registration": self.registration,
        }
