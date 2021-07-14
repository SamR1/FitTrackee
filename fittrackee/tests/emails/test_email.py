from unittest.mock import Mock, patch

from flask import Flask

from fittrackee import email_service
from fittrackee.emails.email import EmailMessage

from ..api_test_case import CallArgsMixin
from .template_results.password_reset_request import expected_en_text_body


class TestEmailMessage:
    def test_it_generate_email_data(self) -> None:
        message = EmailMessage(
            sender='fittrackee@example.com',
            recipient='test@test.com',
            subject='Fittrackee - test email',
            html="""\
<html>
  <body>
    <p>Hello !</p>
  </body>
</html>
            """,
            text='Hello !',
        )
        message_data = message.generate_message()
        assert message_data.get('From') == 'fittrackee@example.com'
        assert message_data.get('To') == 'test@test.com'
        assert message_data.get('Subject') == 'Fittrackee - test email'
        message_string = message_data.as_string()
        assert 'Hello !' in message_string


class TestEmailSending(CallArgsMixin):

    email_data = {
        'expiration_delay': '3 seconds',
        'username': 'test',
        'password_reset_url': 'http://localhost/password-reset?token=xxx',
        'operating_system': 'Linux',
        'browser_name': 'Firefox',
    }

    def assert_smtp(self, smtp: Mock) -> None:
        assert smtp.sendmail.call_count == 1
        call_args = self.get_args(smtp.sendmail.call_args)
        assert call_args[0] == 'fittrackee@example.com'
        assert call_args[1] == 'test@test.com'
        assert expected_en_text_body in call_args[2]

    @patch('smtplib.SMTP_SSL')
    @patch('smtplib.SMTP')
    def test_it_sends_message(
        self, mock_smtp: Mock, mock_smtp_ssl: Mock, app: Flask
    ) -> None:

        email_service.send(
            template='password_reset_request',
            lang='en',
            recipient='test@test.com',
            data=self.email_data,
        )

        smtp = mock_smtp.return_value.__enter__.return_value
        assert smtp.starttls.not_called
        self.assert_smtp(smtp)

    @patch('smtplib.SMTP_SSL')
    @patch('smtplib.SMTP')
    def test_it_sends_message_with_ssl(
        self, mock_smtp: Mock, mock_smtp_ssl: Mock, app_ssl: Flask
    ) -> None:
        email_service.send(
            template='password_reset_request',
            lang='en',
            recipient='test@test.com',
            data=self.email_data,
        )

        smtp = mock_smtp_ssl.return_value.__enter__.return_value
        assert smtp.starttls.not_called
        self.assert_smtp(smtp)

    @patch('smtplib.SMTP_SSL')
    @patch('smtplib.SMTP')
    def test_it_sends_message_with_tls(
        self, mock_smtp: Mock, mock_smtp_ssl: Mock, app_tls: Flask
    ) -> None:
        email_service.send(
            template='password_reset_request',
            lang='en',
            recipient='test@test.com',
            data=self.email_data,
        )

        smtp = mock_smtp.return_value.__enter__.return_value
        assert smtp.starttls.call_count == 1
        self.assert_smtp(smtp)
