import unittest

from mpwo_api import app, db
from mpwo_api.users.models import User


@app.cli.command()
def recreate_db():
    """Recreates a database."""
    db.drop_all()
    db.create_all()
    db.session.commit()
    print('Database (re)creation done.')


@app.cli.command()
def seed_db():
    """Seeds the database."""
    admin = User(username='admin', email='admin@example.com', password='admin')
    admin.admin = True
    db.session.add(admin)
    db.session.commit()


@app.cli.command()
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover(
        'mpwo_api/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    app.run()
