import pytest
from flask import Flask

from fittrackee.emails.email import EmailTemplate

from .template_results.email_comment_unsuspension import (
    expected_en_html_body,
    expected_en_html_body_without_reason,
    expected_en_text_body,
    expected_en_text_body_without_reason,
    expected_fr_html_body,
    expected_fr_text_body,
)


class TestEmailTemplateForCommentReactivation:
    template_name = "comment_unsuspension"
    EMAIL_DATA = {
        "comment_url": (
            "http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/"
            "comments/ZxB8qgyrcSY6ynNzerfirW"
        ),
        "created_at": "07/14/2024 - 07:32:47",
        "fittrackee_url": "http://localhost",
        "reason": "some reason",
        "text": "comment text",
        "user_image_url": "http://localhost/img/user.png",
        "username": "test",
        "without_user_action": True,
    }

    @pytest.mark.parametrize(
        'lang, expected_subject',
        [
            (
                'en',
                'FitTrackee - The suspension on your comment has been lifted',
            ),
            (
                'fr',
                'FitTrackee - La suspension de votre commentaire a été levée',
            ),
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
