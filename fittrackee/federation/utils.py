import re
from typing import Dict, Optional, Tuple
from uuid import uuid4

from Crypto.PublicKey import RSA
from flask import current_app

from .enums import ActivityType


def generate_keys() -> Tuple[str, str]:
    """
    Generate a new RSA key pair and return public and private keys as string
    """
    key_pair = RSA.generate(2048)
    private_key = key_pair.exportKey('PEM').decode('utf-8')
    public_key = key_pair.publickey().exportKey('PEM').decode('utf-8')
    return public_key, private_key


def get_ap_url(username: str, url_type: str) -> str:
    """
    Return ActivityPub URLs.

    Supported URL types:
    - 'user_url'
    - 'inbox'
    - 'outbox'
    - 'following'
    - 'followers'
    - 'shared_inbox'
    """
    ap_url = f"{current_app.config['AP_DOMAIN']}/federation/"
    ap_url_user = f'{ap_url}user/{username}'
    if url_type == 'user_url':
        return ap_url_user
    if url_type in ['inbox', 'outbox', 'following', 'followers']:
        return f'{ap_url_user}/{url_type}'
    if url_type == 'shared_inbox':
        return f'{ap_url}inbox'
    raise Exception('Invalid \'url_type\'.')


def remove_url_scheme(url: str) -> str:
    return re.sub(r'https?://', '', url)


def generate_activity_id() -> str:
    return f"{current_app.config['UI_URL']}/{uuid4()}"


def get_username_and_domain(full_name: str) -> Optional[re.Match]:
    full_name_pattern = r'([\w_\-\.]+)@([\w_\-\.]+\.[a-z]{2,})'
    return re.match(full_name_pattern, full_name)


def is_invalid_activity_data(activity_data: Dict) -> bool:
    return (
        'type' not in activity_data
        or 'object' not in activity_data
        or activity_data['type'] not in [a.value for a in ActivityType]
    )
