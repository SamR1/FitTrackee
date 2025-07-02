import re
from typing import TYPE_CHECKING, Optional, Set, Tuple

from sqlalchemy import func

from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.utils import decode_short_id
from fittrackee.visibility_levels import can_view

from .models import Comment

if TYPE_CHECKING:
    from fittrackee.users.models import User

MENTION_REGEX = r"(?<!\/)(@(<span\s*.*>)?([\w_\-\.]+))(<\/span>)?"
LINK_TEMPLATE = (
    '<a href="{url}" target="_blank" rel="noopener noreferrer">'
    "@<span>{username}</span></a>"
)


def handle_mentions(text: str) -> Tuple[str, Set["User"]]:
    from fittrackee.users.models import User

    mentioned_users: Set["User"] = set()
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


def get_comment(comment_short_id: str, auth_user: Optional["User"]) -> Comment:
    workout_comment_uuid = decode_short_id(comment_short_id)
    filters = [Comment.uuid == workout_comment_uuid]
    if auth_user:
        filters.append(
            Comment.user_id.not_in(
                auth_user.get_blocked_user_ids()
                + auth_user.get_blocked_by_user_ids()
            )
        )
    comment = Comment.query.filter(*filters).first()
    if not comment or not can_view(comment, "text_visibility", auth_user):
        raise CommentForbiddenException()
    return comment
