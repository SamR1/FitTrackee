from time import time
from typing import Dict, List
from urllib.parse import parse_qsl, urlparse

from urllib3.util import parse_url
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


def check_redirect_uri(redirect_uri: str) -> None:
    parsed_uri = urlparse(redirect_uri)
    if parsed_uri.scheme not in ["http", "https"]:
        raise InvalidOAuth2RedirectUris("Invalid redirect URI scheme")


def check_uris_scheme(redirect_uris: List[str]) -> None:
    for uri in redirect_uris:
        check_redirect_uri(uri)


def check_response_location(url: str) -> None:
    check_redirect_uri(url)

    query = dict(parse_qsl(parse_url(url).query))
    if query.get("error"):
        raise InvalidOAuth2RedirectUris(
            query.get("error_description", "invalid payload")
        )


def create_oauth2_client(metadata: Dict, user: User) -> OAuth2Client:
    """
    Create OAuth2 client for 3rd-party applications.

    Only Authorization Code Grant with 'client_secret_post' as method
    is supported.
    Code challenge can be used if provided on authorization.
    """
    check_uris_scheme([*metadata["redirect_uris"]])

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
