import shutil

from fittrackee_api import create_app, db
from fittrackee_api.activities.models import Activity, Sport
from fittrackee_api.activities.utils import update_activity
from fittrackee_api.users.models import User
from tqdm import tqdm

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
    """Init the database."""
    admin = User(
        username='admin', email='admin@example.com', password='mpwoadmin'
    )
    admin.admin = True
    admin.timezone = 'Europe/Paris'
    db.session.add(admin)
    sport = Sport(label='Cycling (Sport)')
    sport.img = '/img/sports/cycling-sport.png'
    sport.is_default = True
    db.session.add(sport)
    sport = Sport(label='Cycling (Transport)')
    sport.img = '/img/sports/cycling-transport.png'
    sport.is_default = True
    db.session.add(sport)
    sport = Sport(label='Hiking')
    sport.img = '/img/sports/hiking.png'
    sport.is_default = True
    db.session.add(sport)
    sport = Sport(label='Mountain Biking')
    sport.img = '/img/sports/mountain-biking.png'
    sport.is_default = True
    db.session.add(sport)
    sport = Sport(label='Running')
    sport.img = '/img/sports/running.png'
    sport.is_default = True
    db.session.add(sport)
    sport = Sport(label='Walking')
    sport.img = '/img/sports/walking.png'
    sport.is_default = True
    db.session.add(sport)
    db.session.commit()
    print('Initial data stored in database.')


@app.cli.command()
def recalculate():
    print("Starting activities data refresh")
    activities = (
        Activity.query.filter(Activity.gpx != None)
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


if __name__ == '__main__':
    app.run()
