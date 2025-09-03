from typing import Union

from flask import Blueprint, Response, request
from sqlalchemy import func

from fittrackee.responses import HttpResponse, UserNotFoundErrorResponse
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Workout

from .feeds.workouts_feed_service import UserWorkoutsFeedService

feeds_blueprint = Blueprint("feeds", __name__)

FEED_ITEMS_LIMIT = 5


@feeds_blueprint.route(
    "/users/<string:user_name>/workouts.rss", methods=["GET"]
)
def get_user_public_workouts_rss_feed(
    user_name: str,
) -> Union[Response, HttpResponse]:
    """
    RSS feed with user's last 5 public workouts.

    Note: it does not display workouts when user is suspended.

    **Example requests**:

    - without parameters:

    .. sourcecode:: http

      GET /user/Sam/workouts.rss HTTP/1.1

    - with some query parameters:

    .. sourcecode:: http

      GET /user/Sam/workouts.rss?lang=fr&imperial_units=true  HTTP/1.1

    :query string lang: RSS feed language (two-letter code, ISO 639-1,
           default: 'en'). If provided language is not supported, it falls
           back to English.
    :query boolean imperial_units: display values with imperial units.
           If false, metric system is used instead (default: false).
    :query boolean description: display workout description if true
           (default: false).

    :statuscode 200: ``success``
    :statuscode 404: ``user does not exist``

    """
    try:
        user = User.query.filter(
            func.lower(User.username) == func.lower(user_name),
        ).first()
        if not user:
            return UserNotFoundErrorResponse()
    except (ValueError, UserNotFoundException):
        return UserNotFoundErrorResponse()

    if user.suspended_at:
        latest_public_workouts = []
    else:
        latest_public_workouts = (
            Workout.query.filter(
                Workout.user_id == user.id,
                Workout.workout_visibility == VisibilityLevel.PUBLIC.value,
            )
            .order_by(Workout.workout_date.desc())
            .limit(FEED_ITEMS_LIMIT)
        ).all()

    params = request.args.copy()
    lang = params.get("lang", "en")
    use_imperial_units = (
        params.get("imperial_units", "false").lower() == "true"
    )
    with_description = params.get("description", "false").lower() == "true"

    feed_service = UserWorkoutsFeedService(
        user,
        latest_public_workouts,
        lang,
        use_imperial_units,
        with_description,
    )
    feed = feed_service.generate_user_workouts_feed()
    return Response(feed, mimetype="text/xml")
