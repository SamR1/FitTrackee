from typing import Dict

import requests

from fittrackee.federation.exceptions import ActorNotFoundException


def get_remote_actor(actor_url: str) -> Dict:
    response = requests.get(
        actor_url,
        headers={'Accept': 'application/activity+json'},
    )
    if response.status_code >= 400:
        raise ActorNotFoundException()

    return response.json()


def fetch_remote_actor(username: str, domain: str) -> Dict:
    response = requests.get(
        f'https://{domain}/.well-known/webfinger?'
        f'resource=acct:{username}@{domain}',
        headers={'Accept': 'application/activity+json'},
    )
    if response.status_code >= 400:
        raise ActorNotFoundException()

    return response.json()
