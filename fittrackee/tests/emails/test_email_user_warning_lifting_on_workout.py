from typing import Dict, Optional, Union

import pytest
from flask import Flask

from fittrackee.emails.emails import EmailTemplate

from .template_results.email_user_warning_lifting_on_workout import (
    expected_en_html_body,
    expected_en_html_body_without_map,
    expected_en_text_body,
    expected_fr_html_body,
    expected_fr_text_body,
)


class TestEmailTemplateForUserWarningLiftingOnWorkoutReport:
    template_name = "user_warning_lifting"
    EMAIL_DATA: Dict[str, Union[Optional[str], bool]] = {
        "created_at": "07/14/2024 - 07:32:47",
        "fittrackee_url": "http://localhost",
        "map": "http://localhost/workouts/map/ZxB8qgyrcSY6ynNzerfirW",
        "title": "workout title",
        "user_image_url": "http://localhost/img/user.png",
        "username": "Test",
        "without_user_action": True,
        "workout_date": "07/14/2024 - 07:32:47",
        "workout_url": "http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/",
    }

    @pytest.mark.parametrize(
        "lang, expected_subject",
        [
            ("en", "FitTrackee - Warning for Test lifted"),
            ("fr", "FitTrackee - Avertissement levé pour Test"),
        ],
    )
    def test_it_gets_subject(
        self, app: Flask, lang: str, expected_subject: str
    ) -> None:
        email_template = EmailTemplate(
            app.config["TEMPLATES_FOLDER"],
            app.config["TRANSLATIONS_FOLDER"],
            app.config["LANGUAGES"],
        )

        subject = email_template.get_content(
            self.template_name, lang, "subject.txt", self.EMAIL_DATA
        )

        assert subject == expected_subject

    @pytest.mark.parametrize(
        "lang, expected_text_body",
        [
            ("en", expected_en_text_body),
            ("fr", expected_fr_text_body),
        ],
    )
    def test_it_gets_text_body(
        self, app: Flask, lang: str, expected_text_body: str
    ) -> None:
        email_template = EmailTemplate(
            app.config["TEMPLATES_FOLDER"],
            app.config["TRANSLATIONS_FOLDER"],
            app.config["LANGUAGES"],
        )

        text_body = email_template.get_content(
            self.template_name, lang, "body.txt", self.EMAIL_DATA
        )

        assert text_body == expected_text_body

    def test_it_gets_en_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(
            app.config["TEMPLATES_FOLDER"],
            app.config["TRANSLATIONS_FOLDER"],
            app.config["LANGUAGES"],
        )

        html_body = email_template.get_content(
            self.template_name, "en", "body.html", self.EMAIL_DATA
        )

        assert expected_en_html_body in html_body

    def test_it_gets_fr_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(
            app.config["TEMPLATES_FOLDER"],
            app.config["TRANSLATIONS_FOLDER"],
            app.config["LANGUAGES"],
        )

        html_body = email_template.get_content(
            self.template_name, "fr", "body.html", self.EMAIL_DATA
        )

        assert expected_fr_html_body in html_body

    def test_it_gets_en_html_body_without_map(self, app: Flask) -> None:
        self.EMAIL_DATA = {
            **self.EMAIL_DATA,
            "map": None,
        }
        email_template = EmailTemplate(
            app.config["TEMPLATES_FOLDER"],
            app.config["TRANSLATIONS_FOLDER"],
            app.config["LANGUAGES"],
        )

        html_body = email_template.get_content(
            self.template_name, "en", "body.html", self.EMAIL_DATA
        )

        assert expected_en_html_body_without_map in html_body
