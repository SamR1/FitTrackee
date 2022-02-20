from flask import Blueprint

from fittrackee.responses import HttpResponse, UserNotFoundErrorResponse

from .decorators import federation_required
from .models import Actor, Domain

ap_federation_blueprint = Blueprint('ap_federation', __name__)


@ap_federation_blueprint.route(
    '/user/<string:preferred_username>', methods=['GET']
)
@federation_required
def get_actor(app_domain: Domain, preferred_username: str) -> HttpResponse:
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
