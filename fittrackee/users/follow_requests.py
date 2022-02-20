from typing import Dict

from flask import Blueprint, current_app, request

from .decorators import authenticate
from .models import FollowRequest, User

follow_requests_blueprint = Blueprint('follow_requests', __name__)

FOLLOW_REQUESTS_PER_PAGE = 10
MAX_FOLLOW_REQUESTS_PER_PAGE = 50


@follow_requests_blueprint.route('/follow_requests', methods=['GET'])
@authenticate
def get_users(auth_user: User) -> Dict:
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
    federation_enabled = current_app.config['federation_enabled']
    return {
        'status': 'success',
        'data': {
            'follow_requests': [
                follow_request.serialize(federation_enabled)['from_user']
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
