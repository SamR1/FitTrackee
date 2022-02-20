from unittest.mock import patch

import pytest
import requests

from fittrackee.federation.exceptions import ActorNotFoundException
from fittrackee.federation.remote_user import get_remote_user

from ...utils import RandomActor, generate_response, random_actor_url


class TestGetRemoteUser:
    def test_it_returns_error_if_remote_instance_returns_error(self) -> None:
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(status_code=404)

            with pytest.raises(ActorNotFoundException):
                get_remote_user(random_actor_url())

    def test_it_returns_user_object_if_remote_response_is_successful(
        self, random_actor: RandomActor
    ) -> None:
        remote_user = random_actor.get_remote_user_object()
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200, content=remote_user
            )

            expected_user = get_remote_user(random_actor.activitypub_id)

            assert remote_user == expected_user
