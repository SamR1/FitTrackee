import pytest


@pytest.fixture
def firefox_options(firefox_options):
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--width=1920')
    firefox_options.add_argument('--height=1080')
    return firefox_options
