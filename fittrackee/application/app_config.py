from datetime import datetime, timezone
from typing import Dict, Union

from flask import Blueprint, current_app, request
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from fittrackee import db
from fittrackee.database import PSQL_INTEGER_LIMIT
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    HttpResponse,
    InvalidConfigValueErrorResponse,
    InvalidPayloadErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import User
from fittrackee.users.roles import UserRole
from fittrackee.users.utils.controls import is_valid_email

from .models import AppConfig
from .utils import update_app_config_from_database, verify_app_config

config_blueprint = Blueprint("config", __name__)


@config_blueprint.route("/config", methods=["GET"])
def get_application_config() -> Union[Dict, HttpResponse]:
    """
    Get Application configuration.

    **Example request**:

    .. sourcecode:: http

      GET /api/config HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "about": null,
          "admin_contact": "admin@example.com",
          "file_sync_limit_import": 10,
          "file_limit_import": 10,
          "is_email_sending_enabled": true,
          "is_registration_enabled": false,
          "max_single_file_size": 1048576,
          "max_users": 0,
          "max_zip_file_size": 10485760,
          "map_attribution": "&copy; <a href=http://www.openstreetmap.org/copyright>OpenStreetMap</a> contributors",
          "privacy_policy": null,
          "privacy_policy_date": null,
          "stats_workouts_limit": 10000,
          "version": "0.12.2",
          "weather_provider": null
        },
        "status": "success"
      }

    :statuscode 200: ``success``
    :statuscode 500: ``error on getting configuration``
    """

    try:
        config = AppConfig.query.one()
        return {"status": "success", "data": config.serialize()}
    except (MultipleResultsFound, NoResultFound) as e:
        return handle_error_and_return_response(
            e, message="error on getting configuration"
        )


@config_blueprint.route("/config", methods=["PATCH"])
@require_auth(scopes=["application:write"], role=UserRole.ADMIN)
def update_application_config(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Update Application configuration.

    **Scope**: ``application:write``

    **Minimum role**: Administrator

    **Example request**:

    .. sourcecode:: http

      GET /api/config HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "about": null,
          "admin_contact": "admin@example.com",
          "file_sync_limit_import": 10,
          "file_limit_import": 10,
          "is_email_sending_enabled": true,
          "is_registration_enabled": false,
          "max_single_file_size": 1048576,
          "max_users": 10,
          "max_zip_file_size": 10485760,
          "map_attribution": "&copy; <a href=http://www.openstreetmap.org/copyright>OpenStreetMap</a> contributors",
          "privacy_policy": null,
          "privacy_policy_date": null,
          "stats_workouts_limit": 10000,
          "version": "0.12.2",
          "weather_provider": null
        },
        "status": "success"
      }

    :<json string about: instance information
    :<json string admin_contact: email to contact the administrator
    :<json integer file_sync_limit_import: max number of files in zip archive,
                   processed synchronously (it must not exceed
                   ``file_limit_import``)
    :<json integer file_limit_import: max number of files in zip archive
    :<json boolean is_registration_enabled: is registration enabled?
    :<json integer max_single_file_size: max size of a single file
    :<json integer max_users: max users allowed to register on instance
    :<json integer max_zip_file_size: max size of a zip archive
    :<json string privacy_policy: instance privacy policy
    :<json integer stats_workouts_limit: max number of workouts for sport
                   statistics

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid payload``
        - ``max size of zip archive must be greater than 0``
        - ``max size of zip archive must be equal or greater than max size of uploaded files``
        - ``max size of uploaded files must be greater than 0``
        - ``max files in a zip archive must be greater than 0``
        - ``max files in a zip archive processed synchronously must be greater than 0``
        - ``max files in a zip archive must be equal or greater than max files in a zip archive processed synchronously``
        - ``max users must be greater than or equal to 0``
        - ``max number of workouts for statistics must be greater than or equal to 0``
        - ``valid email must be provided for admin contact``
        - ``'file_sync_limit_import' must be less than 2147483647``
        - ``'file_limit_import' must be less than 2147483647``
        - ``'max_single_file_size' must be less than 2147483647``
        - ``'max_zip_file_size' must be less than 2147483647``
        - ``'max_users' must be less than 2147483647``
        - ``'stats_workouts_limit' must be less than 2147483647``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
        - ``valid email must be provided for admin contact``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 500: ``error when updating configuration``
    """
    config_data = request.get_json()
    if not config_data:
        return InvalidPayloadErrorResponse()

    ret = verify_app_config(config_data)
    admin_contact = config_data.get("admin_contact")
    if admin_contact and not is_valid_email(admin_contact):
        ret.append("valid email must be provided for admin contact")
    if ret:
        return InvalidPayloadErrorResponse(message=ret)

    try:
        config = AppConfig.query.one()

        for param in [
            "file_sync_limit_import",
            "file_limit_import",
            "max_single_file_size",
            "max_zip_file_size",
            "max_users",
            "stats_workouts_limit",
        ]:
            if param in config_data:
                if (
                    isinstance(config_data[param], int)
                    and config_data[param] > PSQL_INTEGER_LIMIT
                ):
                    return InvalidConfigValueErrorResponse(
                        param, PSQL_INTEGER_LIMIT + 1
                    )
                setattr(config, param, config_data[param])
        if "admin_contact" in config_data:
            config.admin_contact = admin_contact if admin_contact else None
        if "about" in config_data:
            config.about = (
                config_data.get("about") if config_data.get("about") else None
            )
        if "privacy_policy" in config_data:
            privacy_policy = config_data.get("privacy_policy")
            config.privacy_policy = privacy_policy if privacy_policy else None
            config.privacy_policy_date = (
                datetime.now(timezone.utc) if privacy_policy else None
            )

        if config.max_zip_file_size < config.max_single_file_size:
            return InvalidPayloadErrorResponse(
                "max size of zip archive must be equal or greater than "
                "max size of uploaded files"
            )
        if config.file_limit_import < config.file_sync_limit_import:
            return InvalidPayloadErrorResponse(
                "max files in a zip archive must be equal or greater than "
                "max files in a zip archive processed synchronously"
            )
        db.session.commit()
        update_app_config_from_database(current_app, config)
        return {"status": "success", "data": config.serialize()}

    except Exception as e:
        return handle_error_and_return_response(
            e, message="error when updating configuration"
        )


@config_blueprint.route("/ping", methods=["GET"])
def health_check() -> Union[Dict, HttpResponse]:
    """health check endpoint

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
