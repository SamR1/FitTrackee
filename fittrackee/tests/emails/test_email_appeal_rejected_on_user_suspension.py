from typing import Dict, Optional, Union

import pytest
from flask import Flask

from fittrackee.emails.email import EmailTemplate

from .template_results.email_appeal_rejected_on_user_suspension import (
    expected_en_html_body,
    expected_en_text_body,
    expected_fr_html_body,
    expected_fr_text_body,
)


class TestEmailTemplateForAppealRejectedOnUserSuspension:
    template_name = "appeal_rejected"
    EMAIL_DATA: Dict[str, Union[Optional[str], bool]] = {
        "action_type": "user_suspension",
        "fittrackee_url": "http://localhost",
        "user_image_url": "http://localhost/img/user.png",
        "username": "Test",
        "without_user_action": True,
    }

    @pytest.mark.parametrize(
        'lang, expected_subject',
        [
            ('en', 'FitTrackee - Appeal rejected'),
            ('fr', 'FitTrackee - Appel rejeté'),
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
            self.template_name, lang, 'subject.txt', self.EMAIL_DATA
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
