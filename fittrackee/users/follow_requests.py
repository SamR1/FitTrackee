from typing import Dict, Union

from flask import Blueprint, request

from fittrackee import appLog
from fittrackee.federation.exceptions import (
    ActorNotFoundException,
    DomainNotFoundException,
)
from fittrackee.federation.utils_user import get_user_from_username
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    UserNotFoundErrorResponse,
)

from .decorators import authenticate
from .exceptions import (
    FollowRequestAlreadyProcessedError,
    NotExistingFollowRequestError,
    UserNotFoundException,
)
from .models import FollowRequest, User

follow_requests_blueprint = Blueprint('follow_requests', __name__)

FOLLOW_REQUESTS_PER_PAGE = 10
MAX_FOLLOW_REQUESTS_PER_PAGE = 50


@follow_requests_blueprint.route('/follow_requests', methods=['GET'])
@authenticate
def get_follow_requests(auth_user: User) -> Dict:
    params = request.args.copy()
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', FOLLOW_REQUESTS_PER_PAGE))
    order = params.get('order', 'asc')
    if per_page > MAX_FOLLOW_REQUESTS_PER_PAGE:
        per_page = MAX_FOLLOW_REQUESTS_PER_PAGE
    follow_requests_pagination = (
        FollowRequest.query.filter_by(
            followed_user_id=auth_user.id,
            updated_at=None,
        )
        .order_by(
            FollowRequest.created_at.asc() if order == 'asc' else True,
            FollowRequest.created_at.desc() if order == 'desc' else True,
        )
        .paginate(page, per_page, False)
    )
    follow_requests = follow_requests_pagination.items
    return {
        'status': 'success',
        'data': {
            'follow_requests': [
                follow_request.serialize()['from_user']
                for follow_request in follow_requests
            ]
        },
        'pagination': {
            'has_next': follow_requests_pagination.has_next,
            'has_prev': follow_requests_pagination.has_prev,
            'page': follow_requests_pagination.page,
            'pages': follow_requests_pagination.pages,
            'total': follow_requests_pagination.total,
        },
    }


def process_follow_request(
    auth_user: User, user_name: str, action: str
) -> Union[Dict, HttpResponse]:
    try:
        from_user = get_user_from_username(user_name)
    except (
        ActorNotFoundException,
        DomainNotFoundException,
        UserNotFoundException,
    ) as e:
        appLog.error(f'Error when accepting follow request: {e}')
        return UserNotFoundErrorResponse()

    try:
        if action == 'accept':
            auth_user.approves_follow_request_from(from_user)
        else:  # action == 'reject'
            auth_user.rejects_follow_request_from(from_user)
    except NotExistingFollowRequestError:
        return NotFoundErrorResponse(message='Follow request does not exist.')
    except FollowRequestAlreadyProcessedError:
        return InvalidPayloadErrorResponse(
            message=(
                f"Follow request from user '{user_name}' already {action}ed."
            )
        )

    return {
        'status': 'success',
        'message': f"Follow request from user '{user_name}' is {action}ed.",
    }


@follow_requests_blueprint.route(
    '/follow_requests/<user_name>/accept', methods=['POST']
)
@authenticate
def accept_follow_request(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    return process_follow_request(auth_user, user_name, 'accept')


@follow_requests_blueprint.route(
    '/follow_requests/<user_name>/reject', methods=['POST']
)
@authenticate
def reject_follow_request(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    return process_follow_request(auth_user, user_name, 'reject')
