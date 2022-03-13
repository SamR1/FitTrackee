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
