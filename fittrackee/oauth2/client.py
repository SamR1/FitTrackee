from time import time
from typing import Dict

from werkzeug.security import gen_salt

from fittrackee.oauth2.models import OAuth2Client
from fittrackee.users.models import User

DEFAULT_SCOPE = 'read'
VALID_SCOPES = ['read', 'write']


def check_scope(scope: str) -> str:
    """
    Verify if provided scope is valid.
    If not, it returns the default scope ('read').
    """
    valid_scopes = []
    if not isinstance(scope, str) or not scope:
        return DEFAULT_SCOPE

    scopes = scope.split()
    for value in scopes:
        if value in VALID_SCOPES:
            valid_scopes.append(value)
    if len(valid_scopes) == 0:
        valid_scopes.append(DEFAULT_SCOPE)

    return ' '.join(valid_scopes)


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
        'scope': check_scope(metadata['scope']),
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
