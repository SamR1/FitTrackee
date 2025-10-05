from typing import TYPE_CHECKING, Dict, Union

from flask import Blueprint, request

from fittrackee import appLog
from fittrackee.oauth2.server import require_auth

from ..responses import InternalServerErrorResponse
from .nominatim_service import NominatimService

if TYPE_CHECKING:
    from fittrackee.users.models import User

    from ..responses import HttpResponse


geocode_blueprint = Blueprint("geocode", __name__)

nominatim_service = NominatimService()


@geocode_blueprint.route("/geocode/search", methods=["GET"])
@require_auth(scopes=["geocode:read"])
def get_coordinates_from_city(
    auth_user: "User",
) -> Union[Dict, "HttpResponse"]:
    """
    Return coordinates based on location (city) using Nominatim API.

    **Scope**: ``geocode:read``

    **Example requests**:

    .. sourcecode:: http

      GET /api/geocode/search?city=Paris HTTP/1.1

    **Example responses**:

    - returning at least one location:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "locations": [
              {
                "addresstype": "suburb",
                "coordinates": "48.8588897,2.3200410",
                "display_name": "Paris, Île-de-France, France métropolitaine",
                "name": "Paris",
                "osm_id": "r7444",
              }
            ]
          },
          "status": "success"
        }

    - returning no locations

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
            "data": {
                "locations": []
            },
            "status": "success"
        }

    :query string city: location
    :query string language: preferred language for Nominatim results

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 500:
        - ``error when getting coordinates from location``

    """
    params = request.args.copy()
    city = params.get("city")
    language = params.get("language")

    locations = []
    if city:
        try:
            # search is case-insensitive
            locations = nominatim_service.get_locations_from_city(
                city.lower(), language
            )
        except Exception:
            message = "error when getting coordinates from location"
            appLog.exception(message)
            return InternalServerErrorResponse(message)

    return {"status": "success", "locations": locations}


@geocode_blueprint.route("/geocode/lookup", methods=["GET"])
@require_auth(scopes=["geocode:read"])
def get_location_from_id(auth_user: "User") -> Union[Dict, "HttpResponse"]:
    """
    Return location based on OSM id using Nominatim API.

    **Scope**: ``geocode:read``

    **Example requests**:

    .. sourcecode:: http

      GET /api/geocode/lookup?osm_id=r71525 HTTP/1.1

    **Example responses**:

    - returning location:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "location": {
              "addresstype": "suburb",
              "coordinates": "48.8588897,2.3200410",
              "display_name": "Paris, Île-de-France, France métropolitaine",
              "name": "Paris",
              "osm_id": "r7444",
              }
          },
          "status": "success"
        }

    - returning no location

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
            "data": {
                "location": {}
            },
            "status": "success"
        }

    :query string osm_id: OSM id, prefixed by location type
    :query string language: preferred language for Nominatim results

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 500:
        - ``error when getting location from OSM id``

    """
    params = request.args.copy()
    osm_id = params.get("osm_id")
    language = params.get("language")

    location = {}
    if osm_id:
        try:
            # lookup is case-insensitive
            location = nominatim_service.get_location_from_id(
                osm_id.lower(), language
            )
        except Exception:
            message = "error when getting location from OSM id"
            appLog.exception(message)
            return InternalServerErrorResponse(message)

    return {"status": "success", "location": location}
