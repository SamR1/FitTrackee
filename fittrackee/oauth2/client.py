from time import time
from typing import Dict, List
from urllib.parse import urlparse

from werkzeug.security import gen_salt

from fittrackee.users.models import User

from .exceptions import InvalidOAuth2RedirectUris, InvalidOAuth2Scopes
from .models import OAuth2Client

VALID_SCOPES = [
    "application:write",
    "equipments:read",
    "equipments:write",
    "follow:read",
    "follow:write",
    "geocode:read",
    "media:write",
    "notifications:read",
    "notifications:write",
    "profile:read",
    "profile:write",
    "reports:read",
    "reports:write",
    "users:read",
    "users:write",
    "workouts:read",
    "workouts:write",
]
INVALID_SCHEME_ERROR_MESSAGE = (
    "Invalid URI scheme for {invalid_uris}, expected: 'http' or 'https'"
)


def check_scope(scope: str) -> str:
    """
    Verify if provided scope is valid.
    """
    if not isinstance(scope, str) or not scope:
        raise InvalidOAuth2Scopes()

    valid_scopes = []
    scopes = scope.split()
    for value in scopes:
        if value in VALID_SCOPES:
            valid_scopes.append(value)

    if not valid_scopes:
        raise InvalidOAuth2Scopes()

    return " ".join(valid_scopes)


def is_uri_scheme_valid(redirect_uri: str) -> bool:
    parsed_uri = urlparse(redirect_uri)
    return parsed_uri.scheme in ["http", "https"]


def check_uris_scheme(redirect_uris: List[str]) -> None:
    invalid_uris = []
    for uri in redirect_uris:
        if not is_uri_scheme_valid(uri):
            invalid_uris.append(uri)

    if invalid_uris:
        invalid_uris_str = ", ".join(f"'{uri}'" for uri in invalid_uris)
        raise InvalidOAuth2RedirectUris(
            INVALID_SCHEME_ERROR_MESSAGE.format(invalid_uris=invalid_uris_str)
        )


def create_oauth2_client(metadata: Dict, user: User) -> OAuth2Client:
    """
    Create OAuth2 client for 3rd-party applications.

    Only Authorization Code Grant with 'client_secret_post' as method
    is supported.
    Code challenge can be used if provided on authorization.
    """
    check_uris_scheme([metadata["client_uri"], *metadata["redirect_uris"]])

    client_metadata = {
        "client_name": metadata["client_name"],
        "client_description": metadata.get("client_description"),
        "client_uri": metadata["client_uri"],
        "redirect_uris": metadata["redirect_uris"],
        "scope": check_scope(metadata["scope"]),
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "client_secret_post",
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
