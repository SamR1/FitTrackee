import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from .utils_email import parse_email_url

email_log = logging.getLogger('fittrackee_api_email')
email_log.setLevel(logging.DEBUG)


class EmailMessage:
    def __init__(self, sender, recipient, subject, html, text):
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.html = html
        self.text = text

    def generate_message(self):
        message = MIMEMultipart('alternative')
        message['Subject'] = self.subject
        message['From'] = self.sender
        message['To'] = self.recipient
        part1 = MIMEText(self.text, 'plain')
        part2 = MIMEText(self.html, 'html')
        message.attach(part1)
        message.attach(part2)
        return message


class EmailTemplate:
    def __init__(self, template_directory):
        self._env = Environment(loader=FileSystemLoader(template_directory))

    def get_content(self, template, lang, part, data):
        template = self._env.get_template(f'{template}/{lang}/{part}')
        return template.render(data)

    def get_all_contents(self, template, lang, data):
        output = {}
        for part in ['subject.txt', 'body.txt', 'body.html']:
            output[part] = self.get_content(template, lang, part, data)
        return output

    def get_message(self, template, lang, sender, recipient, data):
        output = self.get_all_contents(template, lang, data)
        message = EmailMessage(
            sender,
            recipient,
            output['subject.txt'],
            output['body.html'],
            output['body.txt'],
        )
        return message.generate_message()


class Email:
    def __init__(self, app=None):
        self.host = 'localhost'
        self.port = 1025
        self.use_tls = False
        self.use_ssl = False
        self.username = None
        self.password = None
        self.sender_email = 'no-reply@example.com'
        self.email_template = None
        if app is not None:
            self.init_email(app)

    def init_email(self, app):
        parsed_url = parse_email_url(app.config.get('EMAIL_URL'))
        self.host = parsed_url['host']
        self.port = parsed_url['port']
        self.use_tls = parsed_url['use_tls']
        self.use_ssl = parsed_url['use_ssl']
        self.username = parsed_url['username']
        self.password = parsed_url['password']
        self.sender_email = app.config.get('SENDER_EMAIL')
        self.email_template = EmailTemplate(app.config.get('TEMPLATES_FOLDER'))

    @property
    def smtp(self):
        return smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP

    def send(self, template, lang, recipient, data):
        message = self.email_template.get_message(
            template, lang, self.sender_email, recipient, data
        )
        connection_params = {}
        if self.use_ssl or self.use_tls:
            context = ssl.create_default_context()
        if self.use_ssl:
            connection_params.update({'context': context})
        with self.smtp(self.host, self.port, **connection_params) as smtp:
            smtp.login(self.username, self.password)
            if self.use_tls:
                smtp.starttls(context=context)
            smtp.sendmail(self.sender_email, recipient, message.as_string())
            smtp.quit()
