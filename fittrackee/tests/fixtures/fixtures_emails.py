from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture()
def reports_send_email_mock() -> Iterator[MagicMock]:
    with patch("fittrackee.reports.reports_email_service.send_email") as mock:
        yield mock


@pytest.fixture()
def auth_send_email_mock() -> Iterator[MagicMock]:
    with patch("fittrackee.users.auth.send_email") as mock:
        yield mock


@pytest.fixture()
def users_send_email_mock() -> Iterator[MagicMock]:
    with patch("fittrackee.users.users.send_email") as mock:
        yield mock


@pytest.fixture()
def export_data_send_email_mock() -> Iterator[MagicMock]:
    with patch("fittrackee.users.export_data.send_email") as mock:
        yield mock
