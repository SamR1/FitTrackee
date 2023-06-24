from typing import Dict, Optional, Tuple, Union
from urllib.parse import parse_qsl

from flask import Blueprint, Response, request
from urllib3.util import parse_url

from fittrackee import db
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
)
from fittrackee.users.models import User

from .client import create_oauth2_client
from .exceptions import InvalidOAuth2Scopes
from .models import OAuth2Client, OAuth2Token
from .server import authorization_server, require_auth

oauth2_blueprint = Blueprint('oauth2', __name__)

EXPECTED_METADATA_KEYS = [
    'client_name',
    'client_uri',
    'redirect_uris',
    'scope',
]
DEFAULT_PER_PAGE = 5


def is_errored(url: str) -> Optional[str]:
    query = dict(parse_qsl(parse_url(url).query))
    if query.get('error'):
        return query.get('error_description', 'invalid payload')
    return None


@oauth2_blueprint.route('/oauth/apps', methods=['GET'])
@require_auth()
def get_clients(auth_user: User) -> Dict:
    """
    Get OAuth2 clients (apps) for authenticated user with pagination
    (5 clients/page).

    This endpoint is only accessible by FitTrackee client (first-party
    application).

    **Example request**:

    - without parameters:

    .. sourcecode:: http

      GET /api/oauth/apps HTTP/1.1
      Content-Type: application/json

    - with 'page' parameter:

    .. sourcecode:: http

      GET /api/oauth/apps?page=2 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "data": {
          "clients": [
            {
              "client_description": "",
              "client_id": "o22a27s2aBPUoxJbxV3UjDOx",
              "id": 1,
              "issued_at": "Thu, 14 July 2022 06:27:53 GMT",
              "name": "GPX Importer",
              "redirect_uris": [
                " https://example.com/callback"
              ],
              "scope": "profile:read workouts:write",
              "website": "https://example.com"
            }
          ]
        },
        "pagination": {
          "has_next": false,
          "has_prev": false,
          "page": 1,
          "pages": 1,
          "total": 1
        },
        "status": "success"
      }

    :query integer page: page for pagination (default: 1)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    """
    params = request.args.copy()
    page = int(params.get('page', 1))
    per_page = DEFAULT_PER_PAGE
    clients_pagination = (
        OAuth2Client.query.filter_by(user_id=auth_user.id)
        .order_by(OAuth2Client.id.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
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


@oauth2_blueprint.route('/oauth/apps', methods=['POST'])
@require_auth()
def create_client(auth_user: User) -> Union[HttpResponse, Tuple[Dict, int]]:
    """
    Create an OAuth2 client (app) for the authenticated user.

    This endpoint is only accessible by FitTrackee client (first-party
    application).

    **Example request**:

    .. sourcecode:: http

      POST /api/oauth/apps HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "data": {
          "client": {
            "client_description": "",
            "client_id": "o22a27s2aBPUoxJbxV3UjDOx",
            "client_secret": "<CLIENT SECRET>",
            "id": 1,
            "issued_at": "Thu, 14 July 2022 06:27:53 GMT",
            "name": "GPX Importer",
            "redirect_uris": [
              "https://example.com/callback"
            ],
            "scope": "profile:read workouts:write",
            "website": "https://example.com"
          }
        },
        "status": "created"
      }

    :json string client_name: client name
    :json string client_uri: client URL
    :json array  redirect_uri: list of client redirect URLs (string)
    :json string scope: client scopes
    :json string client_description: client description (optional)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400: ``invalid payload``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    """
    client_metadata = request.get_json()
    if not client_metadata:
        return InvalidPayloadErrorResponse(
            message='OAuth2 client metadata missing'
        )

    missing_keys = [
        key
        for key in EXPECTED_METADATA_KEYS
        if key not in client_metadata.keys()
    ]
    if missing_keys:
        return InvalidPayloadErrorResponse(
            message=(
                'OAuth2 client metadata missing keys: '
                f'{", ".join(missing_keys)}'
            )
        )

    try:
        new_client = create_oauth2_client(client_metadata, auth_user)
    except InvalidOAuth2Scopes:
        return InvalidPayloadErrorResponse(
            message='OAuth2 client invalid scopes'
        )

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
        return NotFoundErrorResponse('OAuth2 client not found')

    return {
        'status': 'success',
        'data': {'client': client.serialize(with_secret=False)},
    }


@oauth2_blueprint.route(
    '/oauth/apps/<string:client_client_id>', methods=['GET']
)
@require_auth()
def get_client_by_client_id(
    auth_user: User, client_client_id: str
) -> Union[Dict, HttpResponse]:
    """
    Get an OAuth2 client (app) by 'client_id'.

    This endpoint is only accessible by FitTrackee client (first-party
    application).

    **Example request**:

    .. sourcecode:: http

      GET /api/oauth/apps/o22a27s2aBPUoxJbxV3UjDOx HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - success:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "data": {
          "client": {
            "client_description": "",
            "client_id": "o22a27s2aBPUoxJbxV3UjDOx",
            "id": 1,
            "issued_at": "Thu, 14 July 2022 06:27:53 GMT",
            "name": "GPX Importer",
            "redirect_uris": [
              "https://example.com/callback"
            ],
            "scope": "profile:read workouts:write",
            "website": "https://example.com"
          }
        },
        "status": "success"
      }

    - not found:

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

      {
        "status": "not found",
        "message": "OAuth2 client not found"
      }

    :param string client_client_id: OAuth2 client client_id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``OAuth2 client not found``
    """
    return get_client(
        auth_user, client_id=None, client_client_id=client_client_id
    )


@oauth2_blueprint.route('/oauth/apps/<int:client_id>/by_id', methods=['GET'])
@require_auth()
def get_client_by_id(
    auth_user: User, client_id: int
) -> Union[Dict, HttpResponse]:
    """
    Get an OAuth2 client (app) by id (integer value).

    This endpoint is only accessible by FitTrackee client (first-party
    application).

    **Example request**:

    .. sourcecode:: http

      GET /api/oauth/apps/1/by_id HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - success:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "data": {
          "client": {
            "client_description": "",
            "client_id": "o22a27s2aBPUoxJbxV3UjDOx",
            "id": 1,
            "issued_at": "Thu, 14 July 2022 06:27:53 GMT",
            "name": "GPX Importer",
            "redirect_uris": [
              "https://example.com/callback"
            ],
            "scope": "profile:read workouts:write",
            "website": "https://example.com"
          }
        },
        "status": "success"
      }

    - not found:

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

      {
        "status": "not found",
        "message": "OAuth2 client not found"
      }

    :param integer client_id: OAuth2 client id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``OAuth2 client not found``
    """
    return get_client(auth_user, client_id=client_id, client_client_id=None)


@oauth2_blueprint.route('/oauth/apps/<int:client_id>', methods=['DELETE'])
@require_auth()
def delete_client(
    auth_user: User, client_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Delete an OAuth2 client (app).

    This endpoint is only accessible by FitTrackee client (first-party
    application).

    **Example request**:

    .. sourcecode:: http

      DELETE /api/oauth/apps/1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :param integer client_id: OAuth2 client id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 204: OAuth2 client deleted
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``OAuth2 client not found``
    """
    client = OAuth2Client.query.filter_by(
        id=client_id,
        user_id=auth_user.id,
    ).first()

    if not client:
        return NotFoundErrorResponse('OAuth2 client not found')

    db.session.delete(client)
    db.session.commit()
    return {'status': 'no content'}, 204


@oauth2_blueprint.route('/oauth/apps/<int:client_id>/revoke', methods=['POST'])
@require_auth()
def revoke_client_tokens(
    auth_user: User, client_id: int
) -> Union[Dict, HttpResponse]:
    """
    Revoke all tokens associated to an OAuth2 client (app).

    This endpoint is only accessible by FitTrackee client (first-party
    application).

    **Example request**:

    .. sourcecode:: http

      POST /api/oauth/apps/1/revoke HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "status": "success"
      }

    :param integer client_id: OAuth2 client id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``OAuth2 client not found``
    """
    client = OAuth2Client.query.filter_by(id=client_id).first()

    if not client:
        return NotFoundErrorResponse('OAuth2 client not found')

    OAuth2Token.revoke_client_tokens(client.client_id)
    return {'status': 'success'}


@oauth2_blueprint.route('/oauth/authorize', methods=['POST'])
@require_auth()
def authorize(auth_user: User) -> Union[HttpResponse, Dict]:
    """
    Authorize an OAuth2 client (app).
    If successful, it redirects to the client callback URL with the code to
    issue a token.

    This endpoint is only accessible by FitTrackee client (first-party
    application).

    **Example request**:

    .. sourcecode:: http

      POST /api/oauth/authorize HTTP/1.1
      Content-Type: multipart/form-data

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "status": "success"
      }

    :form string  client_id: OAuth2 client 'client_id'
    :form string  response_type: client response type (only 'code' is supported
                                by FitTrackee)
    :form string  scopes: OAuth2 client scopes
    :form boolean confirm: confirmation (must be ``true``)
    :form string  state: unique value to prevent cross-site request forgery
                         (not mandatory but recommended)
    :form string  code_challenge: string generated from a code verifier
                         (for PKCE, not mandatory but recommended)
    :form string  code_challenge_method: method used to create challenge,
                         for instance "S256" (mandatory if `code_challenge`
                         provided)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid payload``
        - errors returned by Authlib library
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    """
    data = request.form
    if (
        not data
        or 'client_id' not in data
        or 'response_type' not in data
        or data.get('response_type') != 'code'
    ):
        return InvalidPayloadErrorResponse()

    confirm = data.get('confirm', 'false')
    grant_user = auth_user if confirm.lower() == 'true' else None
    response = authorization_server.create_authorization_response(
        grant_user=grant_user
    )
    error_message = is_errored(url=response.location)
    if error_message:
        return InvalidPayloadErrorResponse(error_message)
    return {'redirect_url': response.location}


@oauth2_blueprint.route('/oauth/token', methods=['POST'])
def issue_token() -> Response:
    """
    Issue or refresh token for a given OAuth2 client (app).

    **Example request**:

    .. sourcecode:: http

      POST /api/oauth/token HTTP/1.1
      Content-Type: multipart/form-data

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "access_token": "rOEHv64THCG28WcewZHRnVLUsOdUvw8NVnHKCmL57e",
        "expires_in": 864000,
        "refresh_token": "NuV9cY8VQOnrQKHTZ5pQAq2Zw7mSH0MorNPJr14AmSwD6f6I",
        "scope": ["profile:read", "workouts:write"],
        "token_type": "Bearer",
        "expires_at": 1658660147.0667062
      }

    :form string  client_id: OAuth2 client 'client_id'
    :form string  client_secret: OAuth2 client secret
    :form string  grant_type: OAuth2 client grant type
                         (only 'authorization_code' (for token issue)
                         and 'refresh_token' (for token refresh)
                         are supported by FitTrackee)
    :form string  code: code generated after authorizing the client
                         (for token issue)
    :form string  code_verifier: code verifier
                         (for token issue with PKCE, not mandatory)
    :form string  refresh_token: refresh token (for token refresh)

    :statuscode 200: ``success``
    :statuscode 400: errors returned by Authlib library
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    """
    return authorization_server.create_token_response()


@oauth2_blueprint.route('/oauth/revoke', methods=['POST'])
def revoke_token() -> Response:
    """
    Revoke a token for a given OAuth2 client (app).

    **Example request**:

    .. sourcecode:: http

      POST /api/oauth/revoke HTTP/1.1
      Content-Type: multipart/form-data

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {}

    :form string client_id: OAuth2 client 'client_id'
    :form string client_secret: OAuth2 client secret
    :form string token: access token to revoke

    :statuscode 200: ``success``
    :statuscode 400: errors returned by Authlib library
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    """
    return authorization_server.create_endpoint_response('revocation')
