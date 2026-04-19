from typing import Dict, Union

from flask import Blueprint
from sqlalchemy.sql import text

from fittrackee import appLog, db
from fittrackee.responses import HttpResponse, InternalServerErrorResponse

health_check_blueprint = Blueprint("health_check", __name__)


@health_check_blueprint.route("/ping", methods=["GET"])
def health_check() -> Dict:
    """
    API health check endpoint

    **Example request**:

    .. sourcecode:: http

      GET /api/ping HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "message": "pong!",
        "status": "success"
      }

    :statuscode 200: ``success``
    """
    return {"status": "success", "message": "pong!"}


@health_check_blueprint.route("/check-db", methods=["GET"])
def db_health_check() -> Union[Dict, HttpResponse]:
    """
    Database health check endpoint

    **Example request**:

    .. sourcecode:: http

      GET /api/check-db HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - when database is available

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "message": "db available",
        "status": "success"
      }

    - when database is not available

    .. sourcecode:: http

      HTTP/1.1 500 Internal Server Error
      Content-Type: application/json

      {
        "message": "db unavailable",
        "status": "error"
      }

    :statuscode 200: ``db available``
    :statuscode 500: ``db unavailable``
    """
    try:
        db.session.execute(text("SELECT 1;"))
    except Exception:
        appLog.exception("db unavailable")
        return InternalServerErrorResponse(message="db unavailable")
    return {"status": "success", "message": "db available"}
