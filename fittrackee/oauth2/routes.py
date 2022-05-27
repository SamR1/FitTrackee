from typing import Dict, Tuple, Union

from flask import Blueprint, request

from fittrackee import db
from fittrackee.responses import HttpResponse, InvalidPayloadErrorResponse
from fittrackee.users.decorators import authenticate
from fittrackee.users.models import User

from .client import create_oauth_client

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
