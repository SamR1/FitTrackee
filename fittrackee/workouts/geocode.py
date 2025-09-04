from typing import TYPE_CHECKING, Dict

from flask import Blueprint, request

from fittrackee.oauth2.server import require_auth

from .services.geocoding.nomatim_service import NomatimService

if TYPE_CHECKING:
    from fittrackee.users.models import User


geocode_blueprint = Blueprint("geocode", __name__)

nomatim_service = NomatimService()


@geocode_blueprint.route("/geocode/search", methods=["GET"])
@require_auth(scopes=["workouts:read"])
def get_coordinates_from_location(auth_user: "User") -> Dict:
    params = request.args.copy()
    query = params.get("query")

    locations = []
    if query:
        locations = nomatim_service.get_locations_from_query(query)

    return {"status": "success", "locations": locations}
