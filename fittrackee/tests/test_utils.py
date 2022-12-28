from typing import Union

import pytest

from fittrackee.files import display_readable_file_size
from fittrackee.request import UserAgent
from fittrackee.utils import get_readable_duration


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
            ('invalid_locale', '30 seconds'),
        ],
    )
    def test_it_returns_duration_in_locale(
        self, locale: str, expected_duration: str
    ) -> None:
        readable_duration = get_readable_duration(30, locale)

        assert readable_duration == expected_duration


class TestParseUserAgent:
    string = (
        'Mozilla/5.0 (X11; Linux x86_64; rv:98.0) '
        'Gecko/20100101 Firefox/98.0'
    )

    def test_it_returns_browser_name(self) -> None:
        user_agent = UserAgent(self.string)
        assert user_agent.browser == 'Firefox'

    def test_it_returns_other_as_brother_name_when_empty_string_provided(
        self,
    ) -> None:
        user_agent = UserAgent('')
        assert user_agent.browser == 'Other'

    def test_it_returns_operating_system(self) -> None:
        user_agent = UserAgent(self.string)
        assert user_agent.platform == 'Linux'

    def test_it_returns_other_as_os_when_empty_string_provided(self) -> None:
        user_agent = UserAgent('')
        assert user_agent.platform == 'Other'
