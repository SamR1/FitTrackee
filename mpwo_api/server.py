import shutil

from mpwo_api import create_app, db
from mpwo_api.activities.models import Sport
from mpwo_api.users.models import User

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
def init_data():
    """Init the database."""
    admin = User(
        username='admin',
        email='admin@example.com',
        password='mpwoadmin')
    admin.admin = True
    db.session.add(admin)
    db.session.add(Sport(label='Cycling (Sport)'))
    db.session.add(Sport(label='Cycling (Transport)'))
    db.session.add(Sport(label='Hiking'))
    db.session.add(Sport(label='Mountain Biking'))
    db.session.add(Sport(label='Running'))
    db.session.add(Sport(label='Walking'))
    db.session.commit()
    print('Initial data stored in database.')


if __name__ == '__main__':
    app.run()
