import unittest

from mpwo_api import app, db
from mpwo_api.users.models import User


@app.cli.command()
def init_db():
    """Init the database."""
    db.drop_all()
    db.create_all()
    admin = User(
        username='admin',
        email='admin@example.com',
        password='mpwoadmin')
    admin.admin = True
    db.session.add(admin)
    db.session.commit()
    print('Database initialization done.')


@app.cli.command()
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover(
        'mpwo_api/mpwo_api/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    app.run()
