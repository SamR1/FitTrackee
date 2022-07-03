import pytest
from flask import Flask

from fittrackee.emails.email import EmailTemplate

from .template_results.password_change import (
    expected_en_html_body,
    expected_en_html_body_without_security,
    expected_en_text_body,
    expected_en_text_body_without_security,
    expected_fr_html_body,
    expected_fr_html_body_without_security,
    expected_fr_text_body,
    expected_fr_text_body_without_security,
)


class TestEmailTemplateForPasswordChange:
    EMAIL_DATA = {
        'username': 'test',
        'operating_system': 'Linux',
        'browser_name': 'Firefox',
        'fittrackee_url': 'http://localhost',
    }

    @pytest.mark.parametrize(
        'lang, expected_subject',
        [
            ('en', 'FitTrackee - Password changed'),
            ('fr', 'FitTrackee - Mot de passe modifié'),
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
            'password_change', lang, 'subject.txt', {}
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
            'password_change', lang, 'body.txt', self.EMAIL_DATA
        )

        assert text_body == expected_text_body

    def test_it_gets_en_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        text_body = email_template.get_content(
            'password_change', 'en', 'body.html', self.EMAIL_DATA
        )

        assert expected_en_html_body in text_body

    def test_it_gets_fr_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        text_body = email_template.get_content(
            'password_change', 'fr', 'body.html', self.EMAIL_DATA
        )

        assert expected_fr_html_body in text_body


class TestEmailTemplateForPasswordChangeWithSecurityInfos:
    EMAIL_DATA = {
        'username': 'test',
        'fittrackee_url': 'http://localhost',
    }

    @pytest.mark.parametrize(
        'lang, expected_subject',
        [
            ('en', 'FitTrackee - Password changed'),
            ('fr', 'FitTrackee - Mot de passe modifié'),
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
            'password_change', lang, 'subject.txt', {}
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
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        text_body = email_template.get_content(
            'password_change', lang, 'body.txt', self.EMAIL_DATA
        )

        assert text_body == expected_text_body

    def test_it_gets_en_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        text_body = email_template.get_content(
            'password_change', 'en', 'body.html', self.EMAIL_DATA
        )

        assert expected_en_html_body_without_security in text_body

    def test_it_gets_fr_html_body(self, app: Flask) -> None:
        email_template = EmailTemplate(
            app.config['TEMPLATES_FOLDER'],
            app.config['TRANSLATIONS_FOLDER'],
            app.config['LANGUAGES'],
        )

        text_body = email_template.get_content(
            'password_change', 'fr', 'body.html', self.EMAIL_DATA
        )

        assert expected_fr_html_body_without_security in text_body
