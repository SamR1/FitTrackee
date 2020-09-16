import shutil

from fittrackee import create_app, db
from fittrackee.activities.models import Activity
from fittrackee.activities.utils import update_activity
from fittrackee.application.utils import init_config
from tqdm import tqdm

from .database_utils import init_database

app = create_app()


@app.cli.command()
def drop_db():
    """Empty database for dev environments."""
    db.engine.execute("DROP TABLE IF EXISTS alembic_version;")
    db.drop_all()
    db.session.commit()
    print('Database dropped.')
    shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)
    print('Uploaded files deleted.')


@app.cli.command()
def initdata():
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


if __name__ == '__main__':
    app.run()
