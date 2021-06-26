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
