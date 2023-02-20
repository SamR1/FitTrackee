import re
from typing import TYPE_CHECKING, Dict, Set, Tuple

from flask import current_app

from fittrackee import appLog
from fittrackee.federation.utils.user import get_user_from_username

if TYPE_CHECKING:
    from fittrackee.users.models import User

MENTION_REGEX = (
    r'(@(<span\s*.*>)?([\w_\-\.]+))(@([\w_\-\.]+\.[a-z]{2,}))?(<\/span>)?'
)
LINK_TEMPLATE = (
    '<a href="{url}" target="_blank" rel="noopener noreferrer">'
    '@<span>{username}</span></a>'
)


def handle_mentions(text: str) -> Tuple[str, Dict[str, Set['User']]]:
    mentioned_users: Dict[str, Set['User']] = {"local": set(), "remote": set()}
    for _, _, username, _, domain, _ in re.findall(
        re.compile(MENTION_REGEX), text
    ):
        mention = f"{username}{f'@{domain}' if domain else ''}"
        remote_domain = (
            f"@{domain}"
            if domain and domain != current_app.config['AP_DOMAIN']
            else ''
        )
        try:
            user = get_user_from_username(
                user_name=f"{username}{remote_domain}",
                with_action="creation",
            )
        except Exception as e:
            appLog.error(f"Error when getting mentioned user: {str(e)}")
            user = None
        if user:
            if user.is_remote:
                mentioned_users["remote"].add(user)
            else:
                mentioned_users["local"].add(user)
            text = text.replace(
                f"@{mention}",
                LINK_TEMPLATE.format(
                    url=user.actor.profile_url, username=mention
                ),
            )
    return text, mentioned_users
