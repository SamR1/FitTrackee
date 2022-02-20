from uuid import uuid4

import pytest
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from flask import Flask

from fittrackee.federation.models import Actor
from fittrackee.federation.utils import AP_CTX, get_ap_url


class TestGetApUrl:
    def test_it_raises_error_if_url_type_is_invalid(self, app: Flask) -> None:
        with pytest.raises(Exception, match="Invalid 'url_type'."):
            get_ap_url(username=uuid4().hex, url_type='url')


class TestActivityPubActorModel:
    def test_actor_model(self, app: Flask, actor_1: Actor) -> None:
        assert '<Actor \'test\'>' == str(actor_1)

        serialized_apactor = actor_1.serialize()
        ap_url = app.config['AP_DOMAIN']
        assert serialized_apactor['@context'] == AP_CTX
        assert serialized_apactor['id'] == actor_1.ap_id
        assert serialized_apactor['type'] == 'Person'
        assert (
            serialized_apactor['preferredUsername']
            == actor_1.preferred_username
        )
        assert serialized_apactor['name'] == actor_1.name
        assert (
            serialized_apactor['inbox']
            == f'{ap_url}/federation/user/{actor_1.name}/inbox'
        )
        assert (
            serialized_apactor['inbox']
            == f'{ap_url}/federation/user/{actor_1.name}/inbox'
        )
        assert (
            serialized_apactor['outbox']
            == f'{ap_url}/federation/user/{actor_1.name}/outbox'
        )
        assert (
            serialized_apactor['followers']
            == f'{ap_url}/federation/user/{actor_1.name}/followers'
        )
        assert (
            serialized_apactor['following']
            == f'{ap_url}/federation/user/{actor_1.name}/following'
        )
        assert serialized_apactor['manuallyApprovesFollowers'] is True
        assert (
            serialized_apactor['publicKey']['id']
            == f'{actor_1.ap_id}#main-key'
        )
        assert serialized_apactor['publicKey']['owner'] == actor_1.ap_id
        assert 'publicKeyPem' in serialized_apactor['publicKey']
        assert (
            serialized_apactor['endpoints']['sharedInbox']
            == f'{ap_url}/federation/inbox'
        )

    def test_generated_key_is_valid(self, app: Flask, actor_1: Actor) -> None:
        actor_1.generate_keys()

        signer = pkcs1_15.new(RSA.import_key(actor_1.private_key))
        hashed_message = SHA256.new('test message'.encode())
        # it raises ValueError if signature is invalid
        signer.verify(hashed_message, signer.sign(hashed_message))
