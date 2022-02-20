from unittest.mock import patch

import pytest
import requests

from fittrackee.federation.exceptions import ActorNotFoundException
from fittrackee.federation.remote_user import get_remote_user

from ...utils import (
    generate_response,
    get_remote_user_object,
    random_actor_url,
    random_domain_with_scheme,
    random_string,
)


class TestGetRemoteUser:
    def test_it_returns_error_if_remote_instance_returns_error(self) -> None:
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(status_code=404)

            with pytest.raises(ActorNotFoundException):
                get_remote_user(random_actor_url())

    def test_it_returns_user_object_if_remote_response_is_successful(
        self,
    ) -> None:
        username = random_string()
        remote_domain = random_domain_with_scheme()
        remote_user = get_remote_user_object(username, remote_domain)
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200, content=remote_user
            )

            expected_user = get_remote_user(
                random_actor_url(username, remote_domain)
            )

            assert remote_user == expected_user
