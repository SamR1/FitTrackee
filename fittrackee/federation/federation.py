from typing import Dict, Union

from flask import Blueprint, request

from fittrackee.responses import HttpResponse, handle_error_and_return_response
from fittrackee.users.models import FollowRequest

from .collections import OrderedCollection, OrderedCollectionPage
from .decorators import (
    federation_required_for_route,
    get_local_actor_from_username,
)
from .inbox import inbox
from .models import Actor, Domain

ap_federation_blueprint = Blueprint('ap_federation', __name__)


USERS_PER_PAGE = 10


@ap_federation_blueprint.route(
    '/user/<string:preferred_username>', methods=['GET']
)
@federation_required_for_route
@get_local_actor_from_username
def get_actor(
    local_actor: Actor, app_domain: Domain, preferred_username: str
) -> HttpResponse:
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
        "url": "https://example.com/users/Sam",
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
    return HttpResponse(
        response=local_actor.serialize(),
        content_type='application/jrd+json; charset=utf-8',
    )


@ap_federation_blueprint.route(
    '/user/<string:preferred_username>/inbox', methods=['POST']
)
@federation_required_for_route
@get_local_actor_from_username
def user_inbox(
    local_actor: Actor, app_domain: Domain, preferred_username: str
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
    return inbox(request)


@ap_federation_blueprint.route('/inbox', methods=['GET', 'POST'])
@federation_required_for_route
def shared_inbox(app_domain: Domain) -> Union[Dict, HttpResponse]:
    """
    Post an activity to shared inbox

    **Example request**:

    .. sourcecode:: http

      POST /federation/inbox HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success"
      }

    :<json json activity: activity

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 403: error, federation is disabled for this instance
    """
    return inbox(request)


def get_relationships(
    local_actor: Actor, relation: str
) -> Union[Dict, HttpResponse]:
    params = request.args.copy()
    page = params.get('page')

    if relation == 'followers':
        relations_object = local_actor.user.followers
        url = local_actor.followers_url
    else:
        relations_object = local_actor.user.following
        url = local_actor.following_url

    if page is None:
        collection = OrderedCollection(url, relations_object)
        return collection.serialize()

    try:
        paginated_relations = relations_object.order_by(
            FollowRequest.updated_at.desc()
        ).paginate(int(page), USERS_PER_PAGE, False)
        collection_page = OrderedCollectionPage(url, paginated_relations)
        return collection_page.serialize()
    except ValueError as e:
        return handle_error_and_return_response(e)


@ap_federation_blueprint.route(
    '/user/<string:preferred_username>/followers', methods=['GET']
)
@federation_required_for_route
@get_local_actor_from_username
def user_followers(
    local_actor: Actor, app_domain: Domain, preferred_username: str
) -> Union[Dict, HttpResponse]:
    """
    Get local actor followers

    - ordered collection

    **Example request**:

    .. sourcecode:: http

      GET /federation/user/sam/followers HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/jrd+json; charset=utf-8

      {
        "@context": "https://www.w3.org/ns/activitystreams",
        "first": "https://example.com/federation/user/Sam/followers?page=1",
        "id": "https://example.com/federation/user/Sam/followers",
        "totalItems": 1,
        "type": "OrderedCollection"
      }

    - ordered collection page

    **Example request**:

    .. sourcecode:: http

      GET /federation/user/sam/followers?page=1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/jrd+json; charset=utf-8

      {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "https://example.com/federation/user/Sam/followers?page=1",
        "orderedItems": [
          "https://another-instance.com/users/admin"
        ],
        "partOf": "https://example.com/federation/user/Sam/followers",
        "totalItems": 1,
        "type": "OrderedCollectionPage"
      }

    :param string preferred_username: actor preferred username

    :query integer page: page if using pagination (default: 1)

    :statuscode 200: success
    :statuscode 403: error, federation is disabled for this instance
    :statuscode 404: user does not exist
    :statuscode 500: error, please try again or contact the administrator

    """
    return get_relationships(local_actor, relation='followers')


@ap_federation_blueprint.route(
    '/user/<string:preferred_username>/following', methods=['GET']
)
@federation_required_for_route
@get_local_actor_from_username
def user_following(
    local_actor: Actor, app_domain: Domain, preferred_username: str
) -> Union[Dict, HttpResponse]:
    """
    Get local actor following

    - ordered collection

    **Example request**:

    .. sourcecode:: http

      GET /federation/user/sam/following HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/jrd+json; charset=utf-8

      {
        "@context": "https://www.w3.org/ns/activitystreams",
        "first": "https://example.com/federation/user/Sam/following?page=1",
        "id": "https://example.com/federation/user/Sam/following",
        "totalItems": 1,
        "type": "OrderedCollection"
      }

    - ordered collection page

    **Example request**:

    .. sourcecode:: http

      GET /federation/user/sam/following?page=1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/jrd+json; charset=utf-8

      {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "https://example.com/federation/user/Sam/following?page=1",
        "orderedItems": [
          "https://another-instance.com/users/admin"
        ],
        "partOf": "https://example.com/federation/user/Sam/following",
        "totalItems": 1,
        "type": "OrderedCollectionPage"
      }

    :param string preferred_username: actor preferred username

    :query integer page: page if using pagination (default: 1)

    :statuscode 200: success
    :statuscode 403: error, federation is disabled for this instance
    :statuscode 404: user does not exist
    :statuscode 500: error, please try again or contact the administrator

    """
    return get_relationships(local_actor, relation='following')
