from unittest.mock import patch

from fittrackee.federation.models import Domain
from fittrackee.federation.tasks.remote_server import update_remote_server

from ...utils import random_string

MODULE = 'fittrackee.federation.tasks.remote_server'


class TestUpdateRemoteServer:
    def test_it_update_remote_server(self, remote_domain: Domain) -> None:
        expected_software_name = random_string()
        expected_software_version = random_string()
        node_info_data = {
            'version': '2.0',
            'software': {
                'name': expected_software_name,
                'version': expected_software_version,
            },
        }
        with patch(
            'fittrackee.federation.tasks.remote_server.'
            'get_remote_server_node_info_url'
        ), patch(
            'fittrackee.federation.tasks.remote_server.'
            'get_remote_server_node_info_data',
            return_value=node_info_data,
        ):
            update_remote_server(remote_domain.name)

        assert remote_domain.software_name == expected_software_name
        assert remote_domain.software_version == expected_software_version
        assert (
            remote_domain.software_current_version == expected_software_version
        )
