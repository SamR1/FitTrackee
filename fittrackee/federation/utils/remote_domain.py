from typing import Dict

import requests

from fittrackee.federation.exceptions import RemoteServerException


def get_remote_server_node_info_url(domain_name: str) -> str:
    response = requests.get(
        f'https://{domain_name}/.well-known/nodeinfo',
    )
    if response.status_code >= 400:
        raise RemoteServerException(
            f"Error when getting node_info url for server '{domain_name}'"
        )

    node_info_url = response.json().get('links', [{}])[0].get('href')
    if not node_info_url:
        raise RemoteServerException(
            f"Invalid node_info url for server '{domain_name}'"
        )

    return node_info_url


def get_remote_server_node_info_data(node_info_url: str) -> Dict:
    response = requests.get(node_info_url)
    if response.status_code >= 400:
        raise RemoteServerException(
            f"Error when getting node_info data from '{node_info_url}'"
        )
    return response.json()
