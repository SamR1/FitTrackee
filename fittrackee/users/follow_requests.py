from typing import Dict, Union

from flask import Blueprint, request
from sqlalchemy import asc, desc, func

from fittrackee import appLog
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    UserNotFoundErrorResponse,
)

from .exceptions import (
    FollowRequestAlreadyProcessedError,
    NotExistingFollowRequestError,
)
from .models import FollowRequest, User

follow_requests_blueprint = Blueprint("follow_requests", __name__)

FOLLOW_REQUESTS_PER_PAGE = 10
MAX_FOLLOW_REQUESTS_PER_PAGE = 50


@follow_requests_blueprint.route("/follow-requests", methods=["GET"])
@require_auth(scopes=["follow:read"])
def get_follow_requests(auth_user: User) -> Dict:
    """
    Get follow requests to process, received by authenticated user.

    **Scope**: ``follow:read``

    **Example requests**:

    - without parameters

    .. sourcecode:: http

      GET /api/follow-requests/ HTTP/1.1

    - with some query parameters

    .. sourcecode:: http

      GET /api/follow-requests?page=1&order=desc  HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "follow_requests": [
            {
              "admin": false,
              "bio": null,
              "birth_date": null,
              "created_at": "Thu, 02 Dec 2021 17:50:48 GMT",
              "first_name": null,
              "followers": 1,
              "following": 1,
              "last_name": null,
              "location": null,
              "nb_sports": 0,
              "nb_workouts": 0,
              "picture": false,
              "records": [],
              "sports_list": [],
              "total_distance": 0.0,
              "total_duration": "0:00:00",
              "username": "Sam"
            }
          ]
        },
        "pagination": {
          "has_next": false,
          "has_prev": false,
          "page": 1,
          "pages": 1,
          "total": 1
        },
        "status": "success"
      }


    :query integer page: page if using pagination (default: 1)
    :query integer per_page: number of follow requests per page
                             (default: 10, max: 50)
    :query string order: sorting order (default: ``asc``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 500:

    """
    params = request.args.copy()
    page = int(params.get("page", 1))
    per_page = int(params.get("per_page", FOLLOW_REQUESTS_PER_PAGE))
    order = params.get("order", "asc")
    if per_page > MAX_FOLLOW_REQUESTS_PER_PAGE:
        per_page = MAX_FOLLOW_REQUESTS_PER_PAGE
    follow_requests_pagination = (
        FollowRequest.query.filter_by(
            followed_user_id=auth_user.id,
            updated_at=None,
        )
        .order_by(
            asc(FollowRequest.created_at)
            if order == "asc"
            else desc(FollowRequest.created_at)
        )
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    follow_requests = follow_requests_pagination.items
    return {
        "status": "success",
        "data": {
            "follow_requests": [
                follow_request.serialize()["from_user"]
                for follow_request in follow_requests
            ]
        },
        "pagination": {
            "has_next": follow_requests_pagination.has_next,
            "has_prev": follow_requests_pagination.has_prev,
            "page": follow_requests_pagination.page,
            "pages": follow_requests_pagination.pages,
            "total": follow_requests_pagination.total,
        },
    }


def process_follow_request(
    auth_user: User, user_name: str, action: str
) -> Union[Dict, HttpResponse]:
    from_user = User.query.filter(
        func.lower(User.username) == func.lower(user_name),
    ).first()
    if not from_user:
        appLog.error(
            f"Error when accepting follow request: {user_name} does not exist"
        )
        return UserNotFoundErrorResponse()

    try:
        if action == "accept":
            auth_user.approves_follow_request_from(from_user)
        else:  # action == 'reject'
            auth_user.rejects_follow_request_from(from_user)
    except NotExistingFollowRequestError:
        return NotFoundErrorResponse(message="Follow request does not exist.")
    except FollowRequestAlreadyProcessedError:
        return InvalidPayloadErrorResponse(
            message=(
                f"Follow request from user '{user_name}' already {action}ed."
            )
        )

    return {
        "status": "success",
        "message": f"Follow request from user '{user_name}' is {action}ed.",
    }


@follow_requests_blueprint.route(
    "/follow-requests/<user_name>/accept", methods=["POST"]
)
@require_auth(scopes=["follow:write"])
def accept_follow_request(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Accept a follow request from user.

    **Scope**: ``follow:write``

    **Example requests**:

    .. sourcecode:: http

      POST /api/follow-requests/Sam/accept HTTP/1.1

    **Example responses**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success",
        "message": "Follow request from user 'Sam' is accepted.",
      }

    :param string user_name: user name

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 400:
        - ``Follow request from user 'user_name' already accepted.``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``user does not exist``
        - ``Follow request does not exist.``

    """
    return process_follow_request(auth_user, user_name, "accept")


@follow_requests_blueprint.route(
    "/follow-requests/<user_name>/reject", methods=["POST"]
)
@require_auth(scopes=["follow:write"])
def reject_follow_request(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Reject a follow request from user.

    **Scope**: ``follow:write``

    **Example requests**:

    .. sourcecode:: http

      POST /api/follow-requests/Sam/reject HTTP/1.1

    **Example responses**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success",
        "message": "Follow request from user 'Sam' is rejected.",
      }

    :param string user_name: user name

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 400:
        - ``Follow request from user 'user_name' already rejected.``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``user does not exist``
        - ``Follow request does not exist.``

    """
    return process_follow_request(auth_user, user_name, "reject")
