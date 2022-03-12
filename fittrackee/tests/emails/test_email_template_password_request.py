import pytest
from flask import Flask

from fittrackee.emails.email import EmailTemplate

from .template_results.password_reset_request import (
    expected_en_html_body,
    expected_en_html_body_without_security,
    expected_en_text_body,
    expected_en_text_body_without_security,
    expected_fr_html_body,
    expected_fr_html_body_without_security,
    expected_fr_text_body,
    expected_fr_text_body_without_security,
)


class TestEmailTemplateForPasswordRequest:
    @pytest.mark.parametrize(
        'lang, expected_subject',
        [
            ('en', 'FitTrackee - Password reset request'),
            ('fr', 'FitTrackee - Réinitialiser votre mot de passe'),
        ],
    )
    def test_it_gets_subject(
        self, app: Flask, lang: str, expected_subject: str
    ) -> None:
        email_template = EmailTemplate(app.config['TEMPLATES_FOLDER'])

        subject = email_template.get_content(
            'password_reset_request', lang, 'subject.txt', {}
        )

        assert subject == expected_subject

    @pytest.mark.parametrize(
        'lang, expected_text_body',
        [('en', expected_en_text_body), ('fr', expected_fr_text_body)],
    )
    def test_it_gets_text_body(
        self, app: Flask, lang: str, expected_text_body: str
    ) -> None:
        email_template = EmailTemplate(app.config['TEMPLATES_FOLDER'])
        email_data = {
            'expiration_delay': '3 seconds' if lang == 'en' else '3 secondes',
            'username': 'test',
            'password_reset_url': 'http://localhost/password-reset?token=xxx',
            'operating_system': 'Linux',
            'browser_name': 'Firefox',
            'fittrackee_url': 'http://localhost',
        }

        text_body = email_template.get_content(
            'password_reset_request', lang, 'body.txt', email_data
        )

        assert text_body == expected_text_body

    def test_it_gets_en_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(app.config['TEMPLATES_FOLDER'])
        email_data = {
            'expiration_delay': '3 seconds',
            'username': 'test',
            'password_reset_url': 'http://localhost/password-reset?token=xxx',
            'operating_system': 'Linux',
            'browser_name': 'Firefox',
            'fittrackee_url': 'http://localhost',
        }

        text_body = email_template.get_content(
            'password_reset_request', 'en', 'body.html', email_data
        )

        assert expected_en_html_body in text_body

    def test_it_gets_fr_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(app.config['TEMPLATES_FOLDER'])
        email_data = {
            'expiration_delay': '3 secondes',
            'username': 'test',
            'password_reset_url': 'http://localhost/password-reset?token=xxx',
            'operating_system': 'Linux',
            'browser_name': 'Firefox',
            'fittrackee_url': 'http://localhost',
        }

        text_body = email_template.get_content(
            'password_reset_request', 'fr', 'body.html', email_data
        )

        assert expected_fr_html_body in text_body


class TestEmailTemplateForPasswordRequestWithoutSecurityInfos:
    @pytest.mark.parametrize(
        'lang, expected_subject',
        [
            ('en', 'FitTrackee - Password reset request'),
            ('fr', 'FitTrackee - Réinitialiser votre mot de passe'),
        ],
    )
    def test_it_gets_subject(
        self, app: Flask, lang: str, expected_subject: str
    ) -> None:
        email_template = EmailTemplate(app.config['TEMPLATES_FOLDER'])

        subject = email_template.get_content(
            'password_reset_request', lang, 'subject.txt', {}
        )

        assert subject == expected_subject

    @pytest.mark.parametrize(
        'lang, expected_text_body',
        [
            ('en', expected_en_text_body_without_security),
            ('fr', expected_fr_text_body_without_security),
        ],
    )
    def test_it_gets_text_body(
        self, app: Flask, lang: str, expected_text_body: str
    ) -> None:
        email_template = EmailTemplate(app.config['TEMPLATES_FOLDER'])
        email_data = {
            'expiration_delay': '3 seconds' if lang == 'en' else '3 secondes',
            'username': 'test',
            'password_reset_url': 'http://localhost/password-reset?token=xxx',
            'fittrackee_url': 'http://localhost',
        }

        text_body = email_template.get_content(
            'password_reset_request', lang, 'body.txt', email_data
        )

        assert text_body == expected_text_body

    def test_it_gets_en_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(app.config['TEMPLATES_FOLDER'])
        email_data = {
            'expiration_delay': '3 seconds',
            'username': 'test',
            'password_reset_url': 'http://localhost/password-reset?token=xxx',
            'fittrackee_url': 'http://localhost',
        }

        text_body = email_template.get_content(
            'password_reset_request', 'en', 'body.html', email_data
        )

        assert expected_en_html_body_without_security in text_body

    def test_it_gets_fr_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(app.config['TEMPLATES_FOLDER'])
        email_data = {
            'expiration_delay': '3 secondes',
            'username': 'test',
            'password_reset_url': 'http://localhost/password-reset?token=xxx',
            'fittrackee_url': 'http://localhost',
        }

        text_body = email_template.get_content(
            'password_reset_request', 'fr', 'body.html', email_data
        )

        assert expected_fr_html_body_without_security in text_body
