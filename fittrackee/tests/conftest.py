import os
import tempfile

import pytest
from werkzeug.test import TestResponse

os.environ["FLASK_ENV"] = "testing"
os.environ["APP_SETTINGS"] = "fittrackee.config.TestingConfig"
# to avoid resetting dev database during tests
os.environ["DATABASE_URL"] = os.environ["DATABASE_TEST_URL"]
TEMP_FOLDER = os.path.join(tempfile.gettempdir(), "FitTrackee")
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.environ["UPLOAD_FOLDER"] = TEMP_FOLDER
os.environ["APP_LOG"] = os.path.join(TEMP_FOLDER, "fittrackee.log")
os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "1"

pytest_plugins = [
    "fittrackee.tests.fixtures.fixtures_app",
    "fittrackee.tests.fixtures.fixtures_emails",
    "fittrackee.tests.fixtures.fixtures_equipments",
    "fittrackee.tests.fixtures.fixtures_geometries",
    "fittrackee.tests.fixtures.fixtures_workouts",
    "fittrackee.tests.fixtures.fixtures_users",
]

pytest.register_assert_rewrite("fittrackee.tests.custom_asserts")

# Prevent pytest from collecting TestResponse as test
TestResponse.__test__ = False  # type: ignore
