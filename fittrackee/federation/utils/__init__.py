import re
from typing import Dict, Tuple

# B413:blacklist error on bandit scan
# related pyCrypto and not pycryptodome
# https://bandit.readthedocs.io/en/1.7.4/blacklists/blacklist_imports.html#b413-import-pycrypto  # noqa
# see issue https://github.com/PyCQA/bandit/issues/614
from Crypto.PublicKey import RSA  # nosec B413
from flask import current_app

from fittrackee.privacy_levels import PrivacyLevel

from ..enums import ActivityType


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
    Return ActivityPub URLs for local actor.

    Supported URL types:
    - 'user_url'
    - 'inbox'
    - 'outbox'
    - 'following'
    - 'followers'
    - 'shared_inbox'
    - 'profile_url'
    """
    ap_url = f"https://{current_app.config['AP_DOMAIN']}/federation/"
    ap_url_user = f'{ap_url}user/{username}'
    if url_type == 'user_url':
        return ap_url_user
    if url_type in ['inbox', 'outbox', 'following', 'followers']:
        return f'{ap_url_user}/{url_type}'
    if url_type == 'shared_inbox':
        return f'{ap_url}inbox'
    if url_type == 'profile_url':
        return f"{current_app.config['UI_URL']}/users/{username}"
    raise Exception('Invalid \'url_type\'.')


def remove_url_scheme(url: str) -> str:
    return re.sub(r'https?://', '', url)


def is_invalid_activity_data(activity_data: Dict) -> bool:
    return (
        'type' not in activity_data
        or 'object' not in activity_data
        or activity_data['type'] not in [a.value for a in ActivityType]
    )


def sending_activities_allowed(visibility: PrivacyLevel) -> bool:
    return current_app.config['federation_enabled'] and visibility in (
        PrivacyLevel.PUBLIC,
        PrivacyLevel.FOLLOWERS_AND_REMOTE,
    )
