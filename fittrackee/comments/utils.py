import re
from typing import TYPE_CHECKING, Set, Tuple

from sqlalchemy import func

if TYPE_CHECKING:
    from fittrackee.users.models import User

MENTION_REGEX = r'(@(<span\s*.*>)?([\w_\-\.]+))(<\/span>)?'
LINK_TEMPLATE = (
    '<a href="{url}" target="_blank" rel="noopener noreferrer">'
    '@<span>{username}</span></a>'
)


def handle_mentions(text: str) -> Tuple[str, Set['User']]:
    from fittrackee.users.models import User

    mentioned_users: Set['User'] = set()
    for _, _, username, _ in re.findall(re.compile(MENTION_REGEX), text):
        user = User.query.filter(
            func.lower(User.username) == func.lower(username),
        ).first()
        if user:
            mentioned_users.add(user)
            text = text.replace(
                f"@{username}",
                LINK_TEMPLATE.format(
                    url=user.get_user_url(), username=username
                ),
            )
    return text, mentioned_users
