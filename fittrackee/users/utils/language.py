from typing import Optional

from flask import current_app


def get_language(language: Optional[str]) -> str:
    # Note: some users may not have language preferences set
    if not language or language not in current_app.config['LANGUAGES']:
        language = 'en'
    return language
