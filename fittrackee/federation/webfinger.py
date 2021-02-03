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
        'subject': f'acct:{actor.preferred_username}@{actor.domain.name}',
        'links': [
            {
                'href': actor.activitypub_id,
                'rel': 'self',
                'type': 'application/activity+json',
            }
        ],
    }
    return HttpResponse(
        response=response, content_type='application/jrd+json; charset=utf-8'
    )
