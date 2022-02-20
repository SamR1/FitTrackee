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


@ap_federation_blueprint.route('/remote-user', methods=['POST'])
@federation_required
@authenticate
def remote_actor(
    app_domain: Domain, auth_user: User
) -> Union[Dict, HttpResponse]:
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
