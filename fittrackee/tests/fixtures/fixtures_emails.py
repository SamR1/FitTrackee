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
