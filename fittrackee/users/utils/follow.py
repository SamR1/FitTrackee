from ..exceptions import FollowRequestAlreadyRejectedError
from ..models import FollowRequest, User


def create_follow_request(follower_user_id: int, followed_user: User) -> None:
    existing_follow_request = FollowRequest.query.filter_by(
        follower_user_id=follower_user_id, followed_user_id=followed_user.id
    ).first()
    if existing_follow_request:
        if existing_follow_request.is_rejected():
            raise FollowRequestAlreadyRejectedError()
        return

    auth_user = User.query.filter_by(id=follower_user_id).first()
    auth_user.send_follow_request_to(followed_user)
