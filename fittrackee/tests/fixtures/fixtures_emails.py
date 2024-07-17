from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture()
def email_updated_to_current_address_mock() -> Iterator[MagicMock]:
    with patch(
        'fittrackee.users.auth.email_updated_to_current_address'
    ) as mock:
        yield mock


@pytest.fixture()
def email_updated_to_new_address_mock() -> Iterator[MagicMock]:
    with patch('fittrackee.users.auth.email_updated_to_new_address') as mock:
        yield mock


@pytest.fixture()
def password_change_email_mock() -> Iterator[MagicMock]:
    with patch('fittrackee.users.auth.password_change_email') as mock:
        yield mock


@pytest.fixture()
def user_password_change_email_mock() -> Iterator[MagicMock]:
    with patch('fittrackee.users.users.password_change_email') as mock:
        yield mock


@pytest.fixture()
def reset_password_email() -> Iterator[MagicMock]:
    with patch('fittrackee.users.auth.reset_password_email') as mock:
        yield mock


@pytest.fixture()
def user_reset_password_email() -> Iterator[MagicMock]:
    with patch('fittrackee.users.users.reset_password_email') as mock:
        yield mock


@pytest.fixture()
def user_email_updated_to_new_address_mock() -> Iterator[MagicMock]:
    with patch('fittrackee.users.users.email_updated_to_new_address') as mock:
        yield mock


@pytest.fixture()
def account_confirmation_email_mock() -> Iterator[MagicMock]:
    with patch('fittrackee.users.auth.account_confirmation_email') as mock:
        yield mock


@pytest.fixture()
def data_export_email_mock() -> Iterator[MagicMock]:
    with patch('fittrackee.users.export_data.data_export_email') as mock:
        yield mock


@pytest.fixture()
def user_suspension_email_mock() -> Iterator[MagicMock]:
    with patch('fittrackee.reports.reports.user_suspension_email') as mock:
        yield mock


@pytest.fixture()
def user_unsuspension_email_mock() -> Iterator[MagicMock]:
    with patch('fittrackee.reports.reports.user_unsuspension_email') as mock:
        yield mock


@pytest.fixture()
def comment_suspension_email_mock() -> Iterator[MagicMock]:
    with patch('fittrackee.reports.reports.comment_suspension_email') as mock:
        yield mock


@pytest.fixture()
def workout_suspension_email_mock() -> Iterator[MagicMock]:
    with patch('fittrackee.reports.reports.workout_suspension_email') as mock:
        yield mock
