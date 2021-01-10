from flask import Blueprint, current_app

from fittrackee.responses import HttpResponse, UserNotFoundErrorResponse

from .models import Actor
from .utils import federation_required

ap_federation_blueprint = Blueprint('ap_federation', __name__)


@ap_federation_blueprint.route(
    '/user/<string:preferred_username>', methods=['GET']
)
@federation_required
def get_actor(preferred_username: str) -> HttpResponse:
    actor = Actor.query.filter_by(
        preferred_username=preferred_username,
        domain=current_app.config['AP_DOMAIN'],
    ).first()
    if not actor:
        return UserNotFoundErrorResponse()

    return HttpResponse(
        response=actor.serialize(),
        content_type='application/jrd+json; charset=utf-8',
    )
