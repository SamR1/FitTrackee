import os
import re
from typing import Dict, Tuple

import requests
from flask import current_app

from fittrackee import db
from fittrackee.federation.exceptions import RemoteActorException
from fittrackee.federation.models import MEDIA_TYPES, Actor, Domain
from fittrackee.federation.remote_actor import (
    fetch_remote_actor,
    get_remote_actor,
)
from fittrackee.files import get_absolute_file_path
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User

from .exceptions import ActorNotFoundException, DomainNotFoundException

FULL_NAME_REGEX = r'^@?([\w_\-\.]+)@([\w_\-\.]+\.[a-z]{2,})$'
MEDIA_EXTENSIONS = {value: key for (key, value) in MEDIA_TYPES.items()}


def get_username_and_domain(full_name: str) -> Tuple:
    result = re.match(FULL_NAME_REGEX, full_name)
    if result is None:
        return None, None
    return result.groups()  # type: ignore


def store_or_delete_user_picture(
    remote_actor_object: Dict, user: User
) -> None:
    if remote_actor_object.get('icon', {}).get('type') == 'Image':
        media_type = remote_actor_object['icon'].get('mediaType', '')
        file_extension = MEDIA_EXTENSIONS.get(media_type)
        if not file_extension:
            return

        picture_url = remote_actor_object['icon']['url']
        response = requests.get(picture_url)
        if response.status_code >= 400:
            return

        dirpath = os.path.join(
            current_app.config['UPLOAD_FOLDER'], 'pictures', str(user.id)
        )
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        filename = f'{user.username}.{file_extension}'
        absolute_picture_path = os.path.join(dirpath, filename)
        relative_picture_path = os.path.join(
            'pictures', str(user.id), filename
        )
        with open(absolute_picture_path, 'wb') as file:
            file.write(response.content)
        user.picture = relative_picture_path

    elif user.picture:
        picture_path = get_absolute_file_path(user.picture)
        if os.path.isfile(picture_path):
            os.remove(picture_path)
        user.picture = None


def create_remote_user(username: str, domain: str) -> User:
    if domain == current_app.config['UI_URL']:
        raise RemoteActorException(
            'the provided account is not a remote account'
        )

    remote_domain = Domain.query.filter_by(name=domain).first()
    if not remote_domain:
        remote_domain = Domain(name=domain)
        db.session.add(remote_domain)
        db.session.flush()

    # get account links via Webfinger
    try:
        webfinger = fetch_remote_actor(username, domain)
    except ActorNotFoundException:
        raise RemoteActorException('can not fetch remote actor')
    remote_actor_url = next(
        (item for item in webfinger.get('links', []) if item['rel'] == 'self'),
        None,
    )
    if not remote_actor_url:
        raise RemoteActorException(
            'invalid data fetched from webfinger endpoint'
        )

    try:
        remote_actor_object = get_remote_actor(remote_actor_url['href'])
    except ActorNotFoundException:
        raise RemoteActorException('can not fetch remote actor')

    # check if actor already exists
    try:
        actor = Actor.query.filter_by(
            preferred_username=remote_actor_object['preferredUsername'],
            domain_id=remote_domain.id,
        ).first()
    except KeyError:
        raise RemoteActorException('invalid remote actor object')

    if not actor:
        try:
            actor = Actor(
                preferred_username=remote_actor_object['preferredUsername'],
                domain_id=remote_domain.id,
                remote_user_data=remote_actor_object,
            )
        except KeyError:
            raise RemoteActorException('invalid remote actor object')
        db.session.add(actor)
        db.session.flush()
        user = User(
            username=remote_actor_object['name'],
            email=None,
            password=None,
            is_remote=True,
        )
        db.session.add(user)
        user.actor_id = actor.id
    else:
        actor.update_remote_data(remote_actor_object)
        actor.user.username = remote_actor_object['name']
    actor.user.manually_approves_followers = remote_actor_object[
        'manuallyApprovesFollowers'
    ]
    store_or_delete_user_picture(remote_actor_object, actor.user)
    db.session.commit()
    return actor.user


def get_user_from_username(
    user_name: str, with_creation: bool = False
) -> User:
    name, domain_name = get_username_and_domain(user_name)
    if domain_name is None:  # local actor
        user = User.query.filter_by(username=user_name).first()
    else:  # remote actor
        actor = None
        domain = Domain.query.filter_by(name=domain_name).first()
        if not domain and not with_creation:
            raise DomainNotFoundException(domain_name)
        if domain:
            actor = Actor.query.filter_by(
                preferred_username=name, domain_id=domain.id
            ).first()
        if not actor:
            if with_creation:
                return create_remote_user(name, domain_name)
            else:
                raise ActorNotFoundException()
        user = actor.user
    if not user:
        raise UserNotFoundException()
    return user
