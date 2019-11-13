import logging
import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
appLog = logging.getLogger('fittrackee_api')


def create_app():
    # instantiate the app
    app = Flask(__name__)

    # set config
    with app.app_context():
        app_settings = os.getenv('APP_SETTINGS')
        app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # get configuration from database
    from .application.models import AppConfig
    from .application.utils import init_config, update_app_config_from_database

    with app.app_context():
        # Note: check if "app_config" table exist to avoid errors when
        # dropping tables on dev environments
        if db.engine.dialect.has_table(db.engine, 'app_config'):
            db_app_config = AppConfig.query.one_or_none()
            if not db_app_config:
                _, db_app_config = init_config()
            update_app_config_from_database(app, db_app_config)

    from .users.auth import auth_blueprint  # noqa
    from .users.users import users_blueprint  # noqa
    from .activities.activities import activities_blueprint  # noqa
    from .activities.records import records_blueprint  # noqa
    from .activities.sports import sports_blueprint  # noqa
    from .activities.stats import stats_blueprint  # noqa
    from .application.app_config import config_blueprint  # noqa

    app.register_blueprint(users_blueprint, url_prefix='/api')
    app.register_blueprint(auth_blueprint, url_prefix='/api')
    app.register_blueprint(activities_blueprint, url_prefix='/api')
    app.register_blueprint(records_blueprint, url_prefix='/api')
    app.register_blueprint(sports_blueprint, url_prefix='/api')
    app.register_blueprint(stats_blueprint, url_prefix='/api')
    app.register_blueprint(config_blueprint, url_prefix='/api')

    if app.debug:
        logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy').handlers = logging.getLogger(
            'werkzeug'
        ).handlers
        logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)
        logging.getLogger('flake8').propagate = False
        appLog.setLevel(logging.DEBUG)

    if app.debug:
        # Enable CORS
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add(
                'Access-Control-Allow-Headers', 'Content-Type,Authorization'
            )
            response.headers.add(
                'Access-Control-Allow-Methods',
                'GET,PUT,POST,DELETE,PATCH,OPTIONS',
            )
            return response

    return app
