from flask import Blueprint, current_app, request

from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    UserNotFoundErrorResponse,
)

from .decorators import federation_required
from .models import Actor, Domain

ap_webfinger_blueprint = Blueprint('ap_webfinger', __name__)


@ap_webfinger_blueprint.route('/webfinger', methods=['GET'])
@federation_required
def webfinger(app_domain: Domain) -> HttpResponse:
    """
    Get account links

    **Example request**:

    .. sourcecode:: http

      GET /.well-known/webfinger?resource=acct:Sam@example.com HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/jrd+json; charset=utf-8

      {
        "subject": "acct:Sam@example.com",
        "links": [
          {
            "href": "https://example.com/user/Sam",
            "rel": "http://webfinger.net/rel/profile-page",
            "type": "text/html"
          },
          {
            "href": "https://example.com/federation/user/Sam",
            "rel": "self",
            "type": "application/activity+json"
          }
        ]
      }

    :query string acct: user account


    :statuscode 200: success
    :statuscode 400:
      - Missing resource in request args.
      - Invalid resource.
    :statuscode 403: error, federation is disabled for this instance
    :statuscode 404: user does not exist

    """
    resource = request.args.get('resource')
    if not resource or not resource.startswith('acct:'):
        return InvalidPayloadErrorResponse('Missing resource in request args.')

    try:
        preferred_username, domain = resource.replace('acct:', '').split('@')
    except ValueError:
        return InvalidPayloadErrorResponse('Invalid resource.')

    if domain != current_app.config['AP_DOMAIN']:
        return UserNotFoundErrorResponse()

    actor = Actor.query.filter_by(
        preferred_username=preferred_username, domain_id=app_domain.id
    ).first()
    if not actor:
        return UserNotFoundErrorResponse()

    response = {
        'subject': f'acct:{actor.fullname}',
        'links': [
            {
                'href': f'{actor.profile_url}',
                'rel': 'http://webfinger.net/rel/profile-page',
                'type': 'text/html',
            },
            {
                'href': actor.activitypub_id,
                'rel': 'self',
                'type': 'application/activity+json',
            },
        ],
    }
    return HttpResponse(
        response=response, content_type='application/jrd+json; charset=utf-8'
    )
