from typing import Tuple

from Crypto.PublicKey import RSA
from flask import current_app


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
