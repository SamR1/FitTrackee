from typing import Optional
from uuid import uuid4

import pytest
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from flask import Flask

from fittrackee import VERSION
from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.models import Actor, Domain, RemoteActorStats
from fittrackee.federation.utils import get_ap_url
from fittrackee.users.models import User

from ...utils import random_actor_url


class TestGetApUrl:
    def test_it_raises_error_if_url_type_is_invalid(self, app: Flask) -> None:
        with pytest.raises(Exception, match="Invalid 'url_type'."):
            get_ap_url(username=uuid4().hex, url_type="url")

    def test_it_returns_user_url(self, app: Flask) -> None:
        username = uuid4().hex

        user_url = get_ap_url(username=username, url_type="user_url")

        assert (
            user_url
            == f"https://{app.config['AP_DOMAIN']}/federation/user/{username}"
        )

    @pytest.mark.parametrize(
        "input_url_type", ["inbox", "outbox", "following", "followers"]
    )
    def test_it_returns_expected_url(
        self, app: Flask, input_url_type: str
    ) -> None:
        username = uuid4().hex

        url = get_ap_url(username=username, url_type=input_url_type)

        assert url == (
            f"https://{app.config['AP_DOMAIN']}/federation/"
            f"user/{username}/{input_url_type}"
        )

    def test_it_returns_user_profile_url(self, app: Flask) -> None:
        username = uuid4().hex

        user_url = get_ap_url(username=username, url_type="profile_url")

        assert user_url == f"{app.config['UI_URL']}/users/{username}"

    def test_it_returns_shared_inbox(self, app: Flask) -> None:
        shared_inbox = get_ap_url(
            username=uuid4().hex, url_type="shared_inbox"
        )

        assert shared_inbox == (
            f"https://{app.config['AP_DOMAIN']}/federation/inbox"
        )


class TestActivityPubDomainModel:
    def test_it_returns_string_representation(
        self, app_with_federation: Flask
    ) -> None:
        local_domain = Domain.query.filter_by(
            name=app_with_federation.config["AP_DOMAIN"]
        ).one()

        assert f"<Domain '{app_with_federation.config['AP_DOMAIN']}'>" == str(
            local_domain
        )

    def test_app_domain_is_local(self, app_with_federation: Flask) -> None:
        local_domain = Domain.query.filter_by(
            name=app_with_federation.config["AP_DOMAIN"]
        ).one()

        assert not local_domain.is_remote

    def test_domain_is_remote(
        self, app_with_federation: Flask, remote_domain: Domain
    ) -> None:
        assert remote_domain.is_remote

    def test_it_returns_current_version_when_local(
        self, app_with_federation: Flask
    ) -> None:
        local_domain = Domain.query.filter_by(
            name=app_with_federation.config["AP_DOMAIN"]
        ).one()

        assert local_domain.software_version is None
        assert local_domain.software_current_version == VERSION

    @pytest.mark.parametrize(
        "input_software_version,",
        [
            (None,),
            (uuid4().hex,),
        ],
    )
    def test_it_returns_current_version_when_remote(
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        input_software_version: Optional[str],
    ) -> None:
        remote_domain.software_version = input_software_version

        assert remote_domain.software_current_version == input_software_version

    def test_it_returns_serialized_object(
        self, app_with_federation: Flask
    ) -> None:
        local_domain = Domain.query.filter_by(
            name=app_with_federation.config["AP_DOMAIN"]
        ).one()

        serialized_domain = local_domain.serialize()

        assert serialized_domain["id"]
        assert "created_at" in serialized_domain
        assert (
            serialized_domain["name"]
            == app_with_federation.config["AP_DOMAIN"]
        )
        assert serialized_domain["is_allowed"]
        assert not serialized_domain["is_remote"]
        assert serialized_domain["software_name"] == local_domain.software_name
        assert (
            serialized_domain["software_version"]
            == local_domain.software_current_version
        )


class TestActivityPubLocalPersonActorModel:
    def test_it_returns_string_representation(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        assert "<Actor 'test'>" == str(user_1.actor)

    def test_actor_is_local(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        assert not user_1.actor.is_remote

    def test_it_returns_fullname(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        assert (
            actor_1.fullname
            == f"{actor_1.preferred_username}@{actor_1.domain.name}"
        )

    def test_it_returns_serialized_object(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        serialized_actor = actor_1.serialize()
        ap_url = app_with_federation.config["AP_DOMAIN"]
        assert serialized_actor["@context"] == AP_CTX
        assert serialized_actor["id"] == actor_1.activitypub_id
        assert serialized_actor["type"] == "Person"
        assert (
            serialized_actor["preferredUsername"] == actor_1.preferred_username
        )
        assert serialized_actor["name"] == actor_1.user.username
        assert serialized_actor["url"] == actor_1.profile_url
        assert serialized_actor["inbox"] == (
            f"https://{ap_url}/federation/user/"
            f"{actor_1.preferred_username}/inbox"
        )
        assert serialized_actor["outbox"] == (
            f"https://{ap_url}/federation/user/"
            f"{actor_1.preferred_username}/outbox"
        )
        assert serialized_actor["followers"] == (
            f"https://{ap_url}/federation/user/"
            f"{actor_1.preferred_username}/followers"
        )
        assert serialized_actor["following"] == (
            f"https://{ap_url}/federation/user/"
            f"{actor_1.preferred_username}/following"
        )
        assert serialized_actor["manuallyApprovesFollowers"] is True
        assert (
            serialized_actor["publicKey"]["id"]
            == f"{actor_1.activitypub_id}#main-key"
        )
        assert serialized_actor["publicKey"]["owner"] == actor_1.activitypub_id
        assert "publicKeyPem" in serialized_actor["publicKey"]
        assert (
            serialized_actor["endpoints"]["sharedInbox"]
            == f"https://{ap_url}/federation/inbox"
        )
        assert "icon" not in serialized_actor

    def test_it_returns_icon_if_user_has_picture(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        user_1.picture = "path/image.jpg"
        actor_1 = user_1.actor
        serialized_actor = actor_1.serialize()
        ap_url = app_with_federation.config["AP_DOMAIN"]

        assert serialized_actor["icon"] == {
            "type": "Image",
            "mediaType": "image/jpeg",
            "url": f"https://{ap_url}/api/users/{user_1.username}/picture",
        }

    @pytest.mark.disable_autouse_generate_keys
    def test_generated_key_is_valid(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        actor_1.generate_keys()

        signer = pkcs1_15.new(
            RSA.import_key(
                actor_1.private_key  # type: ignore
            )
        )
        hashed_message = SHA256.new("test message".encode())
        # it raises ValueError if signature is invalid
        signer.verify(hashed_message, signer.sign(hashed_message))

    def test_it_does_not_create_remote_actor_stats(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        assert (
            RemoteActorStats.query.filter_by(actor_id=user_1.actor_id).first()
            is None
        )


class TestActivityPubRemotePersonActorModel:
    def test_actor_is_remote(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        assert remote_user.actor.is_remote

    def test_it_returns_fullname(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        remote_actor = remote_user.actor
        assert (
            remote_actor.fullname
            == f"{remote_actor.preferred_username}@{remote_actor.domain.name}"
        )

    def test_it_returns_ap_id_if_no_profile_url_provided(
        self,
        app_with_federation: Flask,
        remote_user_without_profile_page: User,
    ) -> None:
        remote_actor = remote_user_without_profile_page.actor
        assert remote_actor.profile_url == remote_actor.activitypub_id

    def test_it_returns_serialized_object(
        self,
        app_with_federation: Flask,
        remote_user: User,
        remote_domain: Domain,
    ) -> None:
        remote_actor = remote_user.actor
        serialized_actor = remote_actor.serialize()
        remote_domain_url = f"https://{remote_domain.name}"
        user_url = random_actor_url(
            remote_actor.preferred_username, remote_domain_url
        )
        assert serialized_actor["@context"] == AP_CTX
        assert serialized_actor["id"] == remote_actor.activitypub_id
        assert serialized_actor["type"] == "Person"
        assert (
            serialized_actor["preferredUsername"]
            == remote_actor.preferred_username
        )
        assert serialized_actor["name"] == remote_actor.user.username
        assert serialized_actor["url"] == remote_actor.profile_url
        assert serialized_actor["inbox"] == f"{user_url}/inbox"
        assert serialized_actor["outbox"] == f"{user_url}/outbox"
        assert serialized_actor["followers"] == f"{user_url}/followers"
        assert serialized_actor["following"] == f"{user_url}/following"
        assert serialized_actor["manuallyApprovesFollowers"] is True
        assert (
            serialized_actor["publicKey"]["id"]
            == f"{remote_actor.activitypub_id}#main-key"
        )
        assert (
            serialized_actor["publicKey"]["owner"]
            == remote_actor.activitypub_id
        )
        assert "publicKeyPem" in serialized_actor["publicKey"]
        assert (
            serialized_actor["endpoints"]["sharedInbox"]
            == f"{remote_domain_url}/inbox"
        )

    def test_it_creates_remote_actor_stats(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        stats = RemoteActorStats.query.filter_by(
            actor_id=remote_user.actor_id
        ).one()

        assert stats.items == 0
        assert stats.followers == 0
        assert stats.following == 0


class TestActivityPubActorModel:
    def test_it_returns_actor_empty_name(
        self, app_with_federation: Flask
    ) -> None:
        domain = Domain.query.filter_by(
            name=app_with_federation.config["AP_DOMAIN"]
        ).one()
        actor = Actor(preferred_username=uuid4().hex, domain_id=domain.id)
        assert actor.name is None
