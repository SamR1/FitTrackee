from typing import Dict, Union
from urllib.parse import urlparse

from flask import Blueprint, request

from fittrackee import db
from fittrackee.federation.exceptions import ActorNotFoundException
from fittrackee.federation.remote_user import get_remote_user
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    UserNotFoundErrorResponse,
)
from fittrackee.users.decorators import authenticate
from fittrackee.users.models import User

from .decorators import federation_required
from .inbox import inbox
from .models import Actor, Domain

ap_federation_blueprint = Blueprint('ap_federation', __name__)


@ap_federation_blueprint.route(
    '/user/<string:preferred_username>', methods=['GET']
)
@federation_required
def get_actor(app_domain: Domain, preferred_username: str) -> HttpResponse:
    """
    Get a local actor

    **Example request**:

    .. sourcecode:: http

      GET /federation/user/admin HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/jrd+json; charset=utf-8

      {
        "@context": [
          "https://www.w3.org/ns/activitystreams",
          "https://w3id.org/security/v1"
        ],
        "id": "https://example.com/federation/user/Sam",
        "type": "Person",
        "preferredUsername": "Sam",
        "name": "Sam",
        "inbox": "https://example.com/federation/user/Sam/inbox",
        "outbox": "https://example.com/federation/user/Sam/outbox",
        "followers": "https://example.com/federation/user/Sam/followers",
        "following": "https://example.com/federation/user/Sam/following",
        "manuallyApprovesFollowers": true,
        "publicKey": {
          "id": "https://example.com/federation/user/Sam#main-key",
          "owner": "https://example.com/federation/user/Sam",
          "publicKeyPem": "-----BEGIN PUBLIC KEY---(...)---END PUBLIC KEY-----"
        },
        "endpoints": {
          "sharedInbox": "https://example.com/federation/inbox"
        }
      }

    :param string preferred_username: actor preferred username

    :statuscode 200: success
    :statuscode 403: error, federation is disabled for this instance
    :statuscode 404: user does not exist

    """
    actor = Actor.query.filter_by(
        preferred_username=preferred_username,
        domain_id=app_domain.id,
    ).first()
    if not actor:
        return UserNotFoundErrorResponse()

    return HttpResponse(
        response=actor.serialize(),
        content_type='application/jrd+json; charset=utf-8',
    )


@ap_federation_blueprint.route('/remote-user', methods=['POST'])
@federation_required
@authenticate
def remote_actor(
    app_domain: Domain, auth_user: User
) -> Union[Dict, HttpResponse]:
    """
    Add a remote actor to local instance if it does not exist.
    Otherwise it updates it.

    **Example request**:

    .. sourcecode:: http

      POST /federation/remote_user HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/jrd+json; charset=utf-8

      {
        "@context": [
          "https://www.w3.org/ns/activitystreams",
          "https://w3id.org/security/v1"
        ],
        "id": "https://remote-instance.social/user/Sam",
        "type": "Person",
        "preferredUsername": "Sam",
        "name": "Sam",
        "inbox": "https://remote-instance.social/user/Sam/inbox",
        "outbox": "https://remote-instance.social/user/Sam/outbox",
        "followers": "https://remote-instance.social/user/Sam/followers",
        "following": "https://remote-instance.social/user/Sam/following",
        "manuallyApprovesFollowers": true,
        "publicKey": {
          "id": "https://remote-instance.social/user/Sam#main-key",
          "owner": "https://remote-instance.social/user/Sam",
          "publicKeyPem": "-----BEGIN PUBLIC KEY---(...)---END PUBLIC KEY-----"
        },
        "endpoints": {
          "sharedInbox": "https://remote-instance.social/inbox"
        }
      }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)

    :<json string actor_url: remote actor activitypub id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 400:
      - invalid payload
      - The provided account is not a remote account.
      - Can not fetch remote actor.
      - Invalid remote actor object.
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403: error, federation is disabled for this instance

    """
    remote_actor_url = (
        request.get_json(silent=True).get('actor_url')  # type: ignore
        if request.get_json(silent=True) is not None
        else None
    )
    if not remote_actor_url:
        return InvalidPayloadErrorResponse()

    # check if domain already exists
    remote_domain_name = urlparse(remote_actor_url).netloc
    remote_domain = Domain.query.filter_by(name=remote_domain_name).first()
    if not remote_domain:
        remote_domain = Domain(name=remote_domain_name)
        db.session.add(remote_domain)
        db.session.flush()

    if not remote_domain.is_remote:
        return InvalidPayloadErrorResponse(
            message='The provided account is not a remote account.'
        )

    try:
        remote_actor_object = get_remote_user(remote_actor_url)
    except ActorNotFoundException:
        return InvalidPayloadErrorResponse(
            message='Can not fetch remote actor.'
        )

    # check if actor already exists
    try:
        actor = Actor.query.filter_by(
            preferred_username=remote_actor_object['preferredUsername'],
            domain_id=remote_domain.id,
        ).first()
    except KeyError:
        return InvalidPayloadErrorResponse(
            message='Invalid remote actor object.'
        )
    if not actor:
        try:
            actor = Actor(
                preferred_username=remote_actor_object['preferredUsername'],
                domain_id=remote_domain.id,
                remote_user_data=remote_actor_object,
            )
        except KeyError:
            return InvalidPayloadErrorResponse(
                message='Invalid remote actor object.'
            )
        db.session.add(actor)
        db.session.flush()
        user = User(
            username=remote_actor_object['name'],
            email=None,
            password=None,
        )
        db.session.add(user)
        user.actor_id = actor.id
    else:
        actor.update_remote_data(remote_actor_object)
        actor.user.username = remote_actor_object['name']
    db.session.commit()

    return HttpResponse(
        response=actor.serialize(),
        content_type='application/jrd+json; charset=utf-8',
    )


@ap_federation_blueprint.route(
    '/user/<string:preferred_username>/inbox', methods=['POST']
)
@federation_required
def user_inbox(
    app_domain: Domain, preferred_username: str
) -> Union[Dict, HttpResponse]:
    """
    Post an activity to user inbox

    **Example request**:

    .. sourcecode:: http

      POST /federation/user/Sam/inbox HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success"
      }

    :param string preferred_username: actor preferred username

    :<json json activity: activity

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 403: error, federation is disabled for this instance
    :statuscode 404: user does not exist

    """
    return inbox(request, app_domain, preferred_username)
