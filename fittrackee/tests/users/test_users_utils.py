import pytest
from flask import Flask

from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User
from fittrackee.users.utils import set_admin_rights

from ..utils import random_string


class TestSetAdminRights:
    def test_it_raises_exception_if_user_does_not_exist(
        self, app: Flask
    ) -> None:
        with pytest.raises(UserNotFoundException):
            set_admin_rights(random_string())

    def test_it_sets_admin_right_for_a_given_user(
        self, app: Flask, user_1: User
    ) -> None:
        set_admin_rights(user_1.username)

        assert user_1.admin is True

    def test_it_does_not_raise_exception_when_user_has_already_admin_right(
        self, app: Flask, user_1_admin: User
    ) -> None:
        set_admin_rights(user_1_admin.username)

        assert user_1_admin.admin is True
