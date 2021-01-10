from flask import Blueprint, current_app, request

from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    UserNotFoundErrorResponse,
)

from .models import Actor

ap_webfinger_blueprint = Blueprint('ap_webfinger', __name__)


@ap_webfinger_blueprint.route('/.well-known/webfinger', methods=['GET'])
def webfinger() -> HttpResponse:
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
        preferred_username=preferred_username, domain=domain
    ).first()
    if not actor:
        return UserNotFoundErrorResponse()

    response = {
        'subject': f'acct:{actor.preferred_username}@{actor.domain}',
        'links': [
            {
                'href': actor.ap_id,
                'rel': 'self',
                'type': 'application/activity+json',
            }
        ],
    }
    return HttpResponse(
        response=response, content_type='application/jrd+json; charset=utf-8'
    )
