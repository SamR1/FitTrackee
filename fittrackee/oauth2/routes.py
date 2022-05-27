from typing import Dict, Tuple, Union

from flask import Blueprint, Response, request

from fittrackee import db
from fittrackee.responses import HttpResponse, InvalidPayloadErrorResponse
from fittrackee.users.decorators import authenticate
from fittrackee.users.models import User

from .client import create_oauth_client
from .server import authorization_server

oauth_blueprint = Blueprint('oauth', __name__)

EXPECTED_METADATA_KEYS = [
    'client_name',
    'client_uri',
    'redirect_uris',
    'scope',
]


@oauth_blueprint.route('/oauth/apps', methods=['POST'])
@authenticate
def create_client(auth_user: User) -> Union[HttpResponse, Tuple[Dict, int]]:
    client_metadata = request.get_json()
    if not client_metadata:
        return InvalidPayloadErrorResponse(
            message='OAuth client metadata missing'
        )

    missing_keys = [
        key
        for key in EXPECTED_METADATA_KEYS
        if key not in client_metadata.keys()
    ]
    if missing_keys:
        return InvalidPayloadErrorResponse(
            message=(
                'OAuth client metadata missing keys: '
                f'{", ".join(missing_keys)}'
            )
        )

    new_client = create_oauth_client(client_metadata, auth_user)
    db.session.add(new_client)
    db.session.commit()
    return (
        {
            'status': 'created',
            'data': {'client': new_client.serialize()},
        },
        201,
    )


@oauth_blueprint.route('/oauth/authorize', methods=['POST'])
@authenticate
def authorize(auth_user: User) -> Response:
    data = request.form
    if not data or 'client_id' not in data or 'response_type' not in data:
        return InvalidPayloadErrorResponse()

    authorization_server.get_consent_grant(end_user=auth_user)
    return authorization_server.create_authorization_response(
        grant_user=auth_user
    )


@oauth_blueprint.route('/oauth/token', methods=['POST'])
def issue_token() -> Response:
    return authorization_server.create_token_response()
