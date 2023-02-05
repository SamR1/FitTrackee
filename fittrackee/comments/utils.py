import re
from typing import TYPE_CHECKING, Set, Tuple

from fittrackee.federation.utils.user import get_user_from_username_if_exists

if TYPE_CHECKING:
    from fittrackee.federation.models import Actor

MENTION_REGEX = r'(@[\w_\-\.]+)(@[\w_\-\.]+\.[a-z]{2,})?'
LINK_TEMPLATE = (
    '<a href="{url}" target="_blank" rel="noopener noreferrer">{username}</a>'
)


def handle_mentions(text: str) -> Tuple[str, Set['Actor']]:
    mentioned_actors: set['Actor'] = set()
    for username, domain in re.findall(re.compile(MENTION_REGEX), text):
        mention = f"{username}{domain}"
        user = get_user_from_username_if_exists(
            username.lstrip('@'), domain.lstrip('@')
        )
        if user:
            name_to_display = mention if user.is_remote else username
            mentioned_actors.add(user.actor)
            text = text.replace(
                mention,
                LINK_TEMPLATE.format(
                    url=user.actor.profile_url, username=name_to_display
                ),
            )
    return text, mentioned_actors
