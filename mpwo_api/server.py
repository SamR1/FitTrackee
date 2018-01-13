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


def run_test(test_path='mpwo_api/tests'):
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover(
        test_path, pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@app.cli.command()
def test(test_path='mpwo_api/tests'):
    """Runs the tests without code coverage."""
    run_test()


@app.cli.command()
def test_local():
    """Runs the tests without code coverage in local machine w/ make."""
    run_test('mpwo_api/mpwo_api/tests')


if __name__ == '__main__':
    app.run()
