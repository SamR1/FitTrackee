from datetime import datetime
from typing import Union

import pytest
from flask import Flask

from fittrackee.files import display_readable_file_size
from fittrackee.request import UserAgent
from fittrackee.users.models import User
from fittrackee.utils import (
    clean_input,
    get_date_string_for_user,
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
        'Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0'
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


class TestSanitizeInput:
    @pytest.mark.parametrize(
        'input_comment',
        [
            'just a text\nfor "test"',
            'link: http://www.example.com',
            'link: <a href="http://www.example.com" '
            'rel="noopener noreferrer">example</a>',
            '<p>just a<br><span>test</span></p>',
        ],
    )
    def test_clean_input_remains_unchanged(
        self, app: Flask, input_comment: str
    ) -> None:
        assert clean_input(input_comment) == input_comment

    @pytest.mark.parametrize(
        'input_comment, expected_comment',
        [
            ("<script>alert('evil!')</script>", ""),
            ("<div><b>test</b></div>", "test"),
            ("<div>test", "test"),
            ("just a<br />test", "just a<br>test"),
            ("<p>test", "<p>test</p>"),
            ('<p class="active">test</p>', "<p>test</p>"),
            ('<p style="display:none;">test</p>', "<p>test</p>"),
            (
                'link: <a href="http://www.example.com">example</a>',
                'link: <a href="http://www.example.com" '
                'rel="noopener noreferrer">example</a>',
            ),
            (
                '<div><a href="http://www.example.com">example</a></div>',
                '<a href="http://www.example.com" '
                'rel="noopener noreferrer">example</a>',
            ),
            (
                '<a href="http://example.com/user/Sam" target="_blank" '
                'rel="noopener noreferrer">@Sam</a> nice!',
                '<a href="http://example.com/user/Sam" target="_blank" '
                'rel="noopener noreferrer">@Sam</a> nice!',
            ),
        ],
    )
    def test_it_removes_disallowed_tags(
        self, app: Flask, input_comment: str, expected_comment: str
    ) -> None:
        assert clean_input(input_comment) == expected_comment


class TestGetDateStringForUser:
    @pytest.mark.parametrize(
        'language, date_format, timezone, expected_date_string',
        [
            ('en', 'MM/dd/yyyy', 'America/New_York', '07/14/2024 - 07:32:47'),
            ('fr', 'dd/MM/yyyy', 'Europe/Paris', '14/07/2024 - 13:32:47'),
            (None, 'yyyy-MM-dd', 'Europe/Paris', '2024-07-14 - 13:32:47'),
            ('en', 'MM/dd/yyyy', None, '07/14/2024 - 13:32:47'),
            ('en', None, 'Europe/Paris', '07/14/2024 - 13:32:47'),
            (
                'en',
                'date_string',
                'America/New_York',
                'Jul. 14, 2024 - 07:32:47',
            ),
            ('cs', 'date_string', 'Europe/Paris', '14. čvc 2024 - 13:32:47'),
            ('de', 'date_string', 'Europe/Paris', '14. Juli 2024 - 13:32:47'),
            ('en', 'date_string', 'Europe/Paris', 'Jul. 14, 2024 - 13:32:47'),
            ('es', 'date_string', 'Europe/Paris', '14 jul 2024 - 13:32:47'),
            ('eu', 'date_string', 'Europe/Paris', '2024 uzt. 14 - 13:32:47'),
            ('fr', 'date_string', 'Europe/Paris', '14 juil. 2024 - 13:32:47'),
            ('gl', 'date_string', 'Europe/Paris', '14 xul. 2024 - 13:32:47'),
            ('it', 'date_string', 'Europe/Paris', '14 lug 2024 - 13:32:47'),
            ('nb', 'date_string', 'Europe/Paris', '14. juli 2024 - 13:32:47'),
            ('nl', 'date_string', 'Europe/Paris', '14 jul. 2024 - 13:32:47'),
            ('pl', 'date_string', 'Europe/Paris', '14 lip 2024 - 13:32:47'),
            ('pt', 'date_string', 'Europe/Paris', '14 jul. 2024 - 13:32:47'),
            (None, 'date_string', 'Europe/Paris', 'Jul. 14, 2024 - 13:32:47'),
        ],
    )
    def test_it_returns_date_string_with_user_preferences(
        self,
        app: Flask,
        user_1: 'User',
        language: Union[str, None],
        date_format: str,
        timezone: Union[str, None],
        expected_date_string: str,
    ) -> None:
        naive_datetime = datetime(
            year=2024, month=7, day=14, hour=11, minute=32, second=47
        )
        user_1.language = language
        user_1.date_format = date_format
        user_1.timezone = timezone

        date_string = get_date_string_for_user(naive_datetime, user_1)

        assert date_string == expected_date_string
