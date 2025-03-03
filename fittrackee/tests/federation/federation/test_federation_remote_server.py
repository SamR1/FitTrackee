from unittest.mock import patch

import pytest
import requests

from fittrackee.federation.exceptions import RemoteServerException
from fittrackee.federation.utils.remote_domain import (
    get_remote_server_node_info_data,
    get_remote_server_node_info_url,
)

from ...utils import generate_response, random_domain


class TestGetNodeInfoUrl:
    def test_it_raises_exception_when_requests_returns_error(self) -> None:
        domain_name = random_domain()
        with patch.object(requests, "get") as requests_mock:
            requests_mock.return_value = generate_response(status_code=400)

            with pytest.raises(
                RemoteServerException,
                match=(
                    "Error when getting node_info url "
                    f"for server '{domain_name}'"
                ),
            ):
                get_remote_server_node_info_url(domain_name)

    def test_it_raises_exception_when_node_info_url_is_invalid(self) -> None:
        domain_name = random_domain()
        with patch.object(requests, "get") as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200, content={}
            )

            with pytest.raises(
                RemoteServerException,
                match=f"Invalid node_info url for server '{domain_name}'",
            ):
                get_remote_server_node_info_url(domain_name)

    def test_it_returns_node_info_url(self) -> None:
        domain_name = random_domain()
        expected_node_info_url = f"https://{domain_name}/nodeinfo/2.0"
        node_infos_links = {
            "links": [
                {
                    "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
                    "href": expected_node_info_url,
                }
            ]
        }
        with patch.object(requests, "get") as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200, content=node_infos_links
            )

            node_info_url = get_remote_server_node_info_url(domain_name)

        assert node_info_url == expected_node_info_url


class TestGetNodeInfoData:
    node_info_url = f"https://{random_domain()}/nodeinfo/2.0"

    def test_it_raises_exception_when_requests_returns_error(self) -> None:
        with patch.object(requests, "get") as requests_mock:
            requests_mock.return_value = generate_response(status_code=400)

            with pytest.raises(
                RemoteServerException,
                match=(
                    "Error when getting node_info data from "
                    f"'{self.node_info_url}'"
                ),
            ):
                get_remote_server_node_info_data(self.node_info_url)

    def test_it_returns_node_info_data(self) -> None:
        expected_node_info_data = {
            "protocols": ["activitypub"],
        }
        with patch.object(requests, "get") as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200, content=expected_node_info_data
            )

            node_info_data = get_remote_server_node_info_data(
                self.node_info_url
            )

        assert node_info_data == expected_node_info_data
