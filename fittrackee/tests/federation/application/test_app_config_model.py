from flask import Flask

from fittrackee.application.models import AppConfig
from fittrackee.users.models import User


class TestConfigModelWithRemoteUsers:
    def test_it_returns_registration_is_enabled(
        self, app_with_federation: Flask, user_1: User, remote_user: User
    ) -> None:
        config = AppConfig.query.one()
        config.max_users = 2

        assert config.is_registration_enabled

    def test_it_returns_registration_is_disabled(
        self, app_with_federation: Flask, user_1: User, remote_user: User
    ) -> None:
        config = AppConfig.query.one()
        config.max_users = 1

        assert config.is_registration_enabled is False
