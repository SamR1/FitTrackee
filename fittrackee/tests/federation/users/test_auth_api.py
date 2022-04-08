import json

from flask import Flask

from fittrackee.users.models import User


def assert_actor_is_created(app: Flask) -> None:
    client = app.test_client()
    username = 'justatest'

    client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username=username,
                email='test@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )

    user = User.query.filter_by(username=username).first()
    assert user.actor.preferred_username == username
    assert user.actor.public_key is not None
    assert user.actor.private_key is not None


class TestUserRegistration:
    def test_it_creates_actor_on_user_registration(
        self, app_with_federation: Flask
    ) -> None:
        assert_actor_is_created(app=app_with_federation)

    def test_local_user_can_register_if_remote_user_exists_with_same_username(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        client = app_with_federation.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=remote_user.username,
                    email='test@test.com',
                    password='12345678',
                    password_conf='12345678',
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 200
        created_user = User.query.filter(
            User.username == remote_user.username,
            User.is_remote == False,  # noqa
        ).first()
        assert created_user.id != remote_user.id
