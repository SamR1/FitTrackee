from typing import Dict, Optional, Tuple, Union

from flask import Blueprint, Response, request

from fittrackee import db
from fittrackee.oauth2.models import OAuth2Client
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
)
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
DEFAULT_PER_PAGE = 5


@oauth_blueprint.route('/oauth/apps', methods=['GET'])
@require_auth()
def get_clients(auth_user: User) -> Dict:
    params = request.args.copy()
    page = int(params.get('page', 1))
    per_page = DEFAULT_PER_PAGE
    clients_pagination = (
        OAuth2Client.query.filter_by(user_id=auth_user.id)
        .order_by(OAuth2Client.id.desc())
        .paginate(page, per_page, False)
    )
    clients = clients_pagination.items
    return {
        'status': 'success',
        'data': {
            'clients': [
                client.serialize(with_secret=False) for client in clients
            ]
        },
        'pagination': {
            'has_next': clients_pagination.has_next,
            'has_prev': clients_pagination.has_prev,
            'page': clients_pagination.page,
            'pages': clients_pagination.pages,
            'total': clients_pagination.total,
        },
    }


@oauth_blueprint.route('/oauth/apps', methods=['POST'])
@require_auth()
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
            'data': {'client': new_client.serialize(with_secret=True)},
        },
        201,
    )


def get_client(
    auth_user: User,
    client_id: Optional[int],
    client_client_id: Optional[str],
) -> Union[Dict, HttpResponse]:
    key = 'id' if client_id else 'client_id'
    value = client_id if client_id else client_client_id
    client = OAuth2Client.query.filter_by(
        **{key: value, 'user_id': auth_user.id}
    ).first()

    if not client:
        return NotFoundErrorResponse('OAuth client not found')

    return {
        'status': 'success',
        'data': {'client': client.serialize(with_secret=False)},
    }


@oauth_blueprint.route('/oauth/apps/<string:client_id>', methods=['GET'])
@require_auth()
def get_client_by_client_id(
    auth_user: User, client_id: str
) -> Union[Dict, HttpResponse]:
    return get_client(auth_user, client_id=None, client_client_id=client_id)


@oauth_blueprint.route('/oauth/apps/<int:client_id>/by_id', methods=['GET'])
@require_auth()
def get_client_by_id(
    auth_user: User, client_id: int
) -> Union[Dict, HttpResponse]:
    return get_client(auth_user, client_id=client_id, client_client_id=None)


@oauth_blueprint.route('/oauth/apps/<string:client_id>', methods=['DELETE'])
@require_auth()
def delete_client(
    auth_user: User, client_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    client = OAuth2Client.query.filter_by(
        id=client_id,
        user_id=auth_user.id,
    ).first()

    if not client:
        return NotFoundErrorResponse('OAuth client not found')

    db.session.delete(client)
    db.session.commit()
    return {'status': 'no content'}, 204


@oauth_blueprint.route('/oauth/authorize', methods=['POST'])
@require_auth()
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


@oauth_blueprint.route('/oauth/revoke', methods=['POST'])
def revoke_token() -> Response:
    return authorization_server.create_endpoint_response('revocation')
