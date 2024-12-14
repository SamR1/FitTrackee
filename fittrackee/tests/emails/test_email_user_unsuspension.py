import pytest
from flask import Flask

from fittrackee.emails.email import EmailTemplate

from .template_results.email_user_unsuspension import (
    expected_en_html_body,
    expected_en_html_body_without_reason,
    expected_en_text_body,
    expected_en_text_body_without_reason,
    expected_fr_html_body,
    expected_fr_text_body,
)


class TestEmailTemplateForUserReactivation:
    template_name = "user_unsuspension"
    EMAIL_DATA = {
        "fittrackee_url": "http://localhost",
        "reason": "some reason",
        "username": "test",
        "without_user_action": True,
    }

    @pytest.mark.parametrize(
        'lang, expected_subject',
        [
            ('en', 'FitTrackee - Your account has been reactivated'),
            ('fr', 'FitTrackee - Votre compte a été réactivé'),
        ],
    )
    def test_it_gets_subject(
        self, app: Flask, lang: str, expected_subject: str
    ) -> None:
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        subject = email_template.get_content(
            self.template_name, lang, 'subject.txt', {}
        )

        assert subject == expected_subject

    @pytest.mark.parametrize(
        'lang, expected_text_body',
        [
            ('en', expected_en_text_body),
            ('fr', expected_fr_text_body),
        ],
    )
    def test_it_gets_text_body(
        self, app: Flask, lang: str, expected_text_body: str
    ) -> None:
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        text_body = email_template.get_content(
            self.template_name, lang, 'body.txt', self.EMAIL_DATA
        )

        assert text_body == expected_text_body

    def test_it_gets_en_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        html_body = email_template.get_content(
            self.template_name, 'en', 'body.html', self.EMAIL_DATA
        )

        assert expected_en_html_body in html_body

    def test_it_gets_fr_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        html_body = email_template.get_content(
            self.template_name, 'fr', 'body.html', self.EMAIL_DATA
        )

        assert expected_fr_html_body in html_body

    def test_it_gets_text_body_without_reason(
        self,
        app: Flask,
    ) -> None:
        self.EMAIL_DATA = {
            **self.EMAIL_DATA,
            "reason": None,
        }
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        text_body = email_template.get_content(
            self.template_name, "en", 'body.txt', self.EMAIL_DATA
        )

        assert text_body == expected_en_text_body_without_reason

    def test_it_gets_en_html_body_without_reason(self, app: Flask) -> None:
        self.EMAIL_DATA = {
            **self.EMAIL_DATA,
            "reason": None,
        }
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        html_body = email_template.get_content(
            self.template_name, 'en', 'body.html', self.EMAIL_DATA
        )

        assert expected_en_html_body_without_reason in html_body
