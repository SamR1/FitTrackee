from typing import Union

import pytest
from flask import Flask

from fittrackee.files import display_readable_file_size
from fittrackee.request import UserAgent
from fittrackee.utils import clean_input, get_readable_duration


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
