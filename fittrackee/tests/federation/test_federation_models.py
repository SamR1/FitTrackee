from uuid import uuid4

import pytest
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from flask import Flask

from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.models import Actor, Domain
from fittrackee.federation.utils import get_ap_url


class TestGetApUrl:
    def test_it_raises_error_if_url_type_is_invalid(self, app: Flask) -> None:
        with pytest.raises(Exception, match="Invalid 'url_type'."):
            get_ap_url(username=uuid4().hex, url_type='url')


class TestActivityPubDomainModel:
    def test_it_returns_string_representation(
        self, app_with_federation: Flask
    ) -> None:
        local_domain = Domain.query.filter_by(
            name=app_with_federation.config['AP_DOMAIN']
        ).first()
        assert f"<Domain '{app_with_federation.config['AP_DOMAIN']}'>" == str(
            local_domain
        )

    def test_app_domain_is_local(self, app_with_federation: Flask) -> None:
        local_domain = Domain.query.filter_by(
            name=app_with_federation.config['AP_DOMAIN']
        ).first()
        assert not local_domain.is_remote

    def test_domain_is_remote(
        self, app_with_federation: Flask, remote_domain: Domain
    ) -> None:
        assert remote_domain.is_remote

    def test_it_returns_serialized_object(
        self, app_with_federation: Flask
    ) -> None:
        local_domain = Domain.query.filter_by(
            name=app_with_federation.config['AP_DOMAIN']
        ).first()
        serialized_domain = local_domain.serialize()

        assert serialized_domain['id']
        assert 'created_at' in serialized_domain
        assert (
            serialized_domain['name']
            == app_with_federation.config['AP_DOMAIN']
        )
        assert serialized_domain['is_allowed']
        assert not serialized_domain['is_remote']


class TestActivityPubLocalPersonActorModel:
    def test_it_returns_string_representation(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        assert '<Actor \'test\'>' == str(actor_1)

    def test_actor_is_local(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        assert not actor_1.is_remote

    def test_it_returns_serialized_object(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        serialized_actor = actor_1.serialize()
        ap_url = app_with_federation.config['AP_DOMAIN']
        assert serialized_actor['@context'] == AP_CTX
        assert serialized_actor['id'] == actor_1.activitypub_id
        assert serialized_actor['type'] == 'Person'
        assert (
            serialized_actor['preferredUsername'] == actor_1.preferred_username
        )
        assert serialized_actor['name'] == actor_1.user.username
        assert (
            serialized_actor['inbox']
            == f'{ap_url}/federation/user/{actor_1.preferred_username}/inbox'
        )
        assert (
            serialized_actor['inbox']
            == f'{ap_url}/federation/user/{actor_1.preferred_username}/inbox'
        )
        assert (
            serialized_actor['outbox']
            == f'{ap_url}/federation/user/{actor_1.preferred_username}/outbox'
        )
        assert serialized_actor['followers'] == (
            f'{ap_url}/federation/user/'
            f'{actor_1.preferred_username}/followers'
        )
        assert serialized_actor['following'] == (
            f'{ap_url}/federation/user/'
            f'{actor_1.preferred_username}/following'
        )
        assert serialized_actor['manuallyApprovesFollowers'] is True
        assert (
            serialized_actor['publicKey']['id']
            == f'{actor_1.activitypub_id}#main-key'
        )
        assert serialized_actor['publicKey']['owner'] == actor_1.activitypub_id
        assert 'publicKeyPem' in serialized_actor['publicKey']
        assert (
            serialized_actor['endpoints']['sharedInbox']
            == f'{ap_url}/federation/inbox'
        )

    def test_generated_key_is_valid(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        actor_1.generate_keys()

        signer = pkcs1_15.new(RSA.import_key(actor_1.private_key))
        hashed_message = SHA256.new('test message'.encode())
        # it raises ValueError if signature is invalid
        signer.verify(hashed_message, signer.sign(hashed_message))


class TestActivityPubRemotePersonActorModel:
    def test_actor_is_remote(
        self, app_with_federation: Flask, remote_actor: Actor
    ) -> None:
        assert remote_actor.is_remote

    def test_it_returns_serialized_object(
        self,
        app_with_federation: Flask,
        remote_actor: Actor,
        remote_domain: Domain,
    ) -> None:
        serialized_actor = remote_actor.serialize()
        ap_url = remote_domain.name
        user_url = (
            f'{remote_domain.name}/users/{remote_actor.preferred_username}'
        )
        assert serialized_actor['@context'] == AP_CTX
        assert serialized_actor['id'] == remote_actor.activitypub_id
        assert serialized_actor['type'] == 'Person'
        assert (
            serialized_actor['preferredUsername']
            == remote_actor.preferred_username
        )
        assert serialized_actor['name'] == remote_actor.user.username
        assert serialized_actor['inbox'] == f'{user_url}/inbox'
        assert serialized_actor['inbox'] == f'{user_url}/inbox'
        assert serialized_actor['outbox'] == f'{user_url}/outbox'
        assert serialized_actor['followers'] == f'{user_url}/followers'
        assert serialized_actor['following'] == f'{user_url}/following'
        assert serialized_actor['manuallyApprovesFollowers'] is True
        assert (
            serialized_actor['publicKey']['id']
            == f'{remote_actor.activitypub_id}#main-key'
        )
        assert (
            serialized_actor['publicKey']['owner']
            == remote_actor.activitypub_id
        )
        assert 'publicKeyPem' in serialized_actor['publicKey']
        assert (
            serialized_actor['endpoints']['sharedInbox'] == f'{ap_url}/inbox'
        )


class TestActivityPubActorModel:
    def test_it_returns_actor_empty_name(
        self, app_with_federation: Flask
    ) -> None:
        domain = Domain.query.filter_by(
            name=app_with_federation.config['AP_DOMAIN']
        ).first()
        actor = Actor(username=uuid4().hex, domain_id=domain.id)
        assert actor.name is None
