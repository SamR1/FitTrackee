from typing import Dict

import requests

from fittrackee.federation.exceptions import ActorNotFoundException


def get_remote_user(actor_url: str) -> Dict:
    response = requests.get(
        actor_url,
        headers={'Accept': 'application/activity+json'},
    )
    if response.status_code >= 400:
        raise ActorNotFoundException()

    return response.json()
