from time import time
from typing import Dict

from werkzeug.security import gen_salt

from fittrackee.oauth2.models import OAuth2Client
from fittrackee.users.models import User


def create_oauth_client(metadata: Dict, user: User) -> OAuth2Client:
    """
    Create oauth client for 3rd-party applications.

    Only Authorization Code Grant with 'client_secret_post' as method
    is supported.
    """
    client_metadata = {
        'client_name': metadata['client_name'],
        'client_uri': metadata['client_uri'],
        'redirect_uris': metadata['redirect_uris'],
        'scope': metadata['scope'],
        'grant_types': ['authorization_code', 'refresh_token'],
        'response_types': ['code'],
        'token_endpoint_auth_method': 'client_secret_post',
    }
    client_id = gen_salt(24)
    client_id_issued_at = int(time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=user.id,
    )
    client.set_client_metadata(client_metadata)
    client.client_secret = gen_salt(48)
    return client
