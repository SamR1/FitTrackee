from unittest.mock import Mock, patch
from urllib.parse import quote

import pytest
from flask import Flask

from fittrackee import email_service
from fittrackee.emails.email import EmailMessage
from fittrackee.emails.exceptions import InvalidEmailUrlScheme

from ..mixins import CallArgsMixin
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


class TestEmailServiceUrlParser(CallArgsMixin):
    def test_it_raises_error_if_url_scheme_is_invalid(self) -> None:
        url = 'stmp://username:password@localhost:587'
        with pytest.raises(InvalidEmailUrlScheme):
            email_service.parse_email_url(url)

    @staticmethod
    def assert_parsed_email(url: str) -> None:
        parsed_email = email_service.parse_email_url(url)

        assert parsed_email['username'] is None
        assert parsed_email['password'] is None
        assert parsed_email['host'] == 'localhost'
        assert parsed_email['port'] == 25
        assert parsed_email['use_tls'] is False
        assert parsed_email['use_ssl'] is False

    def test_it_parses_email_url_without_port(self) -> None:
        url = 'smtp://localhost'
        self.assert_parsed_email(url)

    def test_it_parses_email_url_without_authentication(self) -> None:
        url = 'smtp://localhost:25'
        self.assert_parsed_email(url)

    def test_it_parses_email_url(self) -> None:
        url = 'smtp://test@example.com:12345678@localhost:25'

        parsed_email = email_service.parse_email_url(url)

        assert parsed_email['username'] == 'test@example.com'
        assert parsed_email['password'] == '12345678'
        assert parsed_email['host'] == 'localhost'
        assert parsed_email['port'] == 25
        assert parsed_email['use_tls'] is False
        assert parsed_email['use_ssl'] is False

    def test_it_parses_email_url_with_tls(self) -> None:
        url = 'smtp://test@example.com:12345678@localhost:587?tls=True'

        parsed_email = email_service.parse_email_url(url)

        assert parsed_email['username'] == 'test@example.com'
        assert parsed_email['password'] == '12345678'
        assert parsed_email['host'] == 'localhost'
        assert parsed_email['port'] == 587
        assert parsed_email['use_tls'] is True
        assert parsed_email['use_ssl'] is False

    def test_it_parses_email_url_with_ssl(self) -> None:
        url = 'smtp://test@example.com:12345678@localhost:465?ssl=True'

        parsed_email = email_service.parse_email_url(url)

        assert parsed_email['username'] == 'test@example.com'
        assert parsed_email['password'] == '12345678'
        assert parsed_email['host'] == 'localhost'
        assert parsed_email['port'] == 465
        assert parsed_email['use_tls'] is False
        assert parsed_email['use_ssl'] is True

    def test_it_parses_email_url_with_encoded_password(self) -> None:
        username = "user_name@example.com"
        password = "passwordWith@And&And?"
        encoded_password = quote(password)
        url = f"smtp://{username}:{encoded_password}@localhost:465?ssl=True"

        parsed_email = email_service.parse_email_url(url)

        assert parsed_email['username'] == username
        assert parsed_email['password'] == password
        assert parsed_email['host'] == 'localhost'
        assert parsed_email['port'] == 465
        assert parsed_email['use_tls'] is False
        assert parsed_email['use_ssl'] is True


class TestEmailServiceSend(CallArgsMixin):
    email_data = {
        'expiration_delay': '3 seconds',
        'username': 'test',
        'password_reset_url': 'http://localhost/password-reset?token=xxx',
        'operating_system': 'Linux',
        'browser_name': 'Firefox',
        'fittrackee_url': 'http://localhost',
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
        assert smtp.login.call_count == 1
        smtp.starttls.assert_not_called()
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
        assert smtp.login.call_count == 1
        smtp.starttls.assert_not_called()
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
        assert smtp.login.call_count == 1
        assert smtp.starttls.call_count == 1
        self.assert_smtp(smtp)

    @patch('smtplib.SMTP_SSL')
    @patch('smtplib.SMTP')
    def test_it_sends_message_without_authentication(
        self, mock_smtp: Mock, mock_smtp_ssl: Mock, app_wo_email_auth: Flask
    ) -> None:
        email_service.send(
            template='password_reset_request',
            lang='en',
            recipient='test@test.com',
            data=self.email_data,
        )

        smtp = mock_smtp.return_value.__enter__.return_value
        smtp.login.assert_not_called()
        smtp.starttls.assert_not_called()
        self.assert_smtp(smtp)
