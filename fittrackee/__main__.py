# source for StandaloneApplication class:
# http://docs.gunicorn.org/en/stable/custom.html
import os
import shutil

import gunicorn.app.base
from fittrackee import create_app, db
from fittrackee.activities.models import Activity
from fittrackee.activities.utils import update_activity
from fittrackee.application.utils import init_config
from fittrackee.database_utils import init_database
from flask_dramatiq import worker
from flask_migrate import upgrade
from tqdm import tqdm

HOST = os.getenv('HOST', '0.0.0.0')
PORT = os.getenv('PORT', '5000')
WORKERS = os.getenv('APP_WORKERS', 1)
BASEDIR = os.path.abspath(os.path.dirname(__file__))
app = create_app()
dramatiq_worker = worker


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, current_app, options=None):
        self.options = options or {}
        self.application = current_app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def upgrade_db():
    with app.app_context():
        upgrade(directory=BASEDIR + '/migrations')


@app.cli.command('drop-db')
def drop_db():
    """Empty database for dev environments."""
    db.engine.execute("DROP TABLE IF EXISTS alembic_version;")
    db.drop_all()
    db.session.commit()
    print('Database dropped.')
    shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)
    print('Uploaded files deleted.')


@app.cli.command('init-data')
def init_data():
    """Init the database and application config."""
    init_database(app)


@app.cli.command()
def recalculate():
    print("Starting activities data refresh")
    activities = (
        Activity.query.filter(Activity.gpx != None)  # noqa
        .order_by(Activity.activity_date.asc())  # noqa
        .all()
    )
    if len(activities) == 0:
        print('➡️  no activities to upgrade.')
        return None
    pbar = tqdm(activities)
    for activity in pbar:
        update_activity(activity)
        pbar.set_postfix(activitiy_id=activity.id)
    db.session.commit()


@app.cli.command('init-app-config')
def init_app_config():
    """Init application configuration."""
    print("Init application configuration")
    config_created, _ = init_config()
    if config_created:
        print("Creation done!")
    else:
        print(
            "Application configuration already existing in database. "
            "Please use web application to update it."
        )


def main():
    options = {'bind': f'{HOST}:{PORT}', 'workers': WORKERS}
    StandaloneApplication(app, options).run()


if __name__ == '__main__':
    app.run()
