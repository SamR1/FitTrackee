from typing import Optional

from flask import current_app

from fittrackee.users.constants import USER_LANGUAGE


def get_language(language: Optional[str]) -> str:
    # Note: some users may not have language preferences set
    if not language or language not in current_app.config["LANGUAGES"]:
        language = USER_LANGUAGE
    return language
