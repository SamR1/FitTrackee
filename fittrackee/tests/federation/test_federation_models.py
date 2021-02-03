from datetime import datetime
from uuid import uuid4

import pytest
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from flask import Flask

from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.exceptions import (
    FollowRequestAlreadyProcessedError,
    NotExistingFollowRequestError,
)
from fittrackee.federation.models import Actor, Domain, FollowRequest
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


class TestActivityPubPersonActorModel:
    def test_it_returns_string_representation(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        assert '<Actor \'test\'>' == str(actor_1)

    def test_actor_is_local_is_local(
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


class TestActivityPubActorFollowingModel:
    def test_actor_2_sends_follow_requests_to_actor_1(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
    ) -> None:
        follow_request = actor_2.send_follow_request_to(actor_1)

        assert follow_request in actor_2.sent_follow_requests.all()

    def test_actor_1_receives_follow_requests_from_actor_2(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
    ) -> None:
        follow_request = actor_2.send_follow_request_to(actor_1)

        assert follow_request in actor_1.received_follow_requests.all()

    def test_actor_has_pending_follow_request(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        follow_request_from_actor_2_to_actor_1: FollowRequest,
    ) -> None:
        assert (
            follow_request_from_actor_2_to_actor_1
            in actor_1.pending_follow_requests
        )

    def test_actor_has_no_pending_follow_request(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        follow_request_from_actor_2_to_actor_1: FollowRequest,
    ) -> None:
        follow_request_from_actor_2_to_actor_1.updated_at = datetime.now()
        assert actor_1.pending_follow_requests == []

    def test_actor_approves_follow_request(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_actor_2_to_actor_1: FollowRequest,
        follow_request_from_actor_3_to_actor_1: FollowRequest,
    ) -> None:
        follow_request = actor_1.approves_follow_request_from(actor_2)

        assert follow_request.is_approved
        assert actor_1.pending_follow_requests == [
            follow_request_from_actor_3_to_actor_1
        ]

    def test_actor_refuses_follow_request(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_actor_2_to_actor_1: FollowRequest,
    ) -> None:
        follow_request = actor_1.refuses_follow_request_from(actor_2)

        assert not follow_request.is_approved
        assert actor_1.pending_follow_requests == []

    def test_it_raises_error_if_follow_request_does_not_exists(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
    ) -> None:
        with pytest.raises(NotExistingFollowRequestError):
            actor_1.approves_follow_request_from(actor_2)

    def test_it_raises_error_if_actor_approves_follow_request_already_processed(  # noqa
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_actor_2_to_actor_1: FollowRequest,
    ) -> None:
        follow_request_from_actor_2_to_actor_1.updated_at = datetime.now()

        with pytest.raises(FollowRequestAlreadyProcessedError):
            actor_1.approves_follow_request_from(actor_2)


class TestActivityPubActorModel:
    def test_it_returns_actor_empty_name(
        self, app_with_federation: Flask
    ) -> None:
        domain = Domain.query.filter_by(
            name=app_with_federation.config['AP_DOMAIN']
        ).first()
        actor = Actor(username=uuid4().hex, domain_id=domain.id)
        assert actor.name is None
