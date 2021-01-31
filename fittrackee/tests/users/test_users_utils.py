from typing import Union
from uuid import uuid4

import pytest

from fittrackee.users.utils import (
    display_readable_file_size,
    get_readable_duration,
)


class TestDisplayReadableFileSize:
    @pytest.mark.parametrize(
        'size, expected_readable_size',
        [
            (0, '0 bytes'),
            (1, '1 byte'),
            (100, '100.0 bytes'),
            (1024, '1.0KB'),
            (286773663, '273.5MB'),
        ],
    )
    def test_it_returns_readable_file_size(
        self, size: Union[float, int], expected_readable_size: str
    ) -> None:
        readable_file_size = display_readable_file_size(size)

        assert readable_file_size == expected_readable_size


class TestReadableDuration:
    @pytest.mark.parametrize(
        'locale, expected_duration',
        [
            ('en', '30 seconds'),
            ('fr', '30 secondes'),
            (None, '30 seconds'),
            (uuid4().hex, '30 seconds'),
        ],
    )
    def test_it_returns_duration_in_locale(
        self, locale: str, expected_duration: str
    ) -> None:
        readable_duration = get_readable_duration(30, locale)

        assert readable_duration == expected_duration
