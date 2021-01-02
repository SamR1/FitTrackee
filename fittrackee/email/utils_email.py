from typing import Dict

from urllib3.util import parse_url


class InvalidEmailUrlScheme(Exception):
    ...


def parse_email_url(email_url: str) -> Dict:
    parsed_url = parse_url(email_url)
    if parsed_url.scheme != 'smtp':
        raise InvalidEmailUrlScheme()
    credentials = parsed_url.auth.split(':')
    return {
        'host': parsed_url.host,
        'port': parsed_url.port,
        'use_tls': True if parsed_url.query == 'tls=True' else False,
        'use_ssl': True if parsed_url.query == 'ssl=True' else False,
        'username': credentials[0],
        'password': credentials[1],
    }
