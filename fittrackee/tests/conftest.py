import os

os.environ['FLASK_ENV'] = 'testing'
os.environ['APP_SETTINGS'] = 'fittrackee.config.TestingConfig'
os.environ['UI_URL'] = 'https://0.0.0.0:5000'
os.environ['SENDER_EMAIL'] = 'fittrackee@example.com'
# to avoid resetting dev database during tests
os.environ['DATABASE_URL'] = os.environ['DATABASE_TEST_URL']

pytest_plugins = [
    'fittrackee.tests.fixtures.fixtures_app',
    'fittrackee.tests.fixtures.fixtures_federation',
    'fittrackee.tests.fixtures.fixtures_federation_users',
    'fittrackee.tests.fixtures.fixtures_workouts',
    'fittrackee.tests.fixtures.fixtures_users',
]
