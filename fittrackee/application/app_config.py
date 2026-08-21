from datetime import datetime, timezone
from typing import Dict, Optional, Union

from flask import Blueprint, current_app, request
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from fittrackee import db
from fittrackee.constants import DEFAULT_TILE_PROVIDER
from fittrackee.database import PSQL_INTEGER_LIMIT
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    HttpResponse,
    InvalidConfigValueErrorResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.models import User
from fittrackee.users.roles import UserRole
from fittrackee.users.utils.controls import is_valid_email
from fittrackee.utils import clean_input

from .models import AppConfig
from .utils import update_app_config_from_database, verify_app_config

config_blueprint = Blueprint("config", __name__)

MAX_GLOBAL_MAP_WORKOUTS = 50000  # limitation on browser side


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
          "elevation_services":	{
            "open_elevation": false,
            "valhalla": false
          },
          "enable_heatmap": false,
          "file_sync_limit_import": 10,
          "file_limit_import": 10,
          "global_map_workouts_limit": 10000,
          "is_email_sending_enabled": true,
          "is_registration_enabled": false,
          "max_image_size": 5242880,
          "max_single_file_size": 1048576,
          "max_users": 0,
          "max_zip_file_size": 10485760,
          "map_attribution": "&copy; <a href=http://www.openstreetmap.org/copyright>OpenStreetMap</a> contributors",
          "privacy_policy": null,
          "privacy_policy_date": null,
          "stats_workouts_limit": 10000,
          "version": "1.3.4",
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
          "elevation_services":	{
            "open_elevation": false,
            "valhalla": false
          },
          "enable_heatmap": false,
          "file_sync_limit_import": 10,
          "file_limit_import": 10,
          "global_map_workouts_limit": 10000,
          "is_email_sending_enabled": true,
          "is_registration_enabled": false,
          "max_image_size": 5242880,
          "max_single_file_size": 1048576,
          "max_users": 10,
          "max_zip_file_size": 10485760,
          "map_attribution": "&copy; <a href=http://www.openstreetmap.org/copyright>OpenStreetMap</a> contributors",
          "privacy_policy": null,
          "privacy_policy_date": null,
          "stats_workouts_limit": 10000,
          "version": "1.3.4",
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
    :<json integer global_map_workouts_limit: max number of workouts displayed
                   on global map
    :<json boolean is_registration_enabled: is registration enabled?
    :<json integer max_image_size: max size of an image
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
        - ``'max_image_size' must be less than 2147483647``
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
            "max_image_size",
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
                clean_input(config_data["about"])
                if config_data.get("about")
                else None
            )
        if "privacy_policy" in config_data:
            privacy_policy = config_data.get("privacy_policy")
            config.privacy_policy = (
                clean_input(privacy_policy) if privacy_policy else None
            )
            config.privacy_policy_date = (
                datetime.now(timezone.utc) if privacy_policy else None
            )
        if "global_map_workouts_limit" in config_data:
            if (
                config_data["global_map_workouts_limit"]
                > MAX_GLOBAL_MAP_WORKOUTS
            ):
                return InvalidPayloadErrorResponse(
                    f"'global_map_workouts_limit' must be less "
                    f"than {MAX_GLOBAL_MAP_WORKOUTS}"
                )
            config.global_map_workouts_limit = config_data[
                "global_map_workouts_limit"
            ]

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


@config_blueprint.route("/tile-providers", methods=["GET"])
@require_auth(scopes=["application:read"], optional_auth_user=True)
def get_application_tile_providers(
    auth_user: Optional["User"],
) -> Union[Dict, HttpResponse]:
    """
    Get tile providers

    **Example request**:

    .. sourcecode:: http

      GET /api/tile-providers HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - For non admin user:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "tile_providers": [
            {
              "attribution": "<Map Attribution for OpenStreetMap>",
              "default": true,
              "enabled": true,
              "id": "osm",
              "name": "OpenStreetMap",
            },
            {
              "attribution": "<Map Attribution for CyclOSM>",
              "default": false,
              "enabled": true,
              "id": "cyclosm",
              "name": "CyclOSM",
            }
          ]
        },
        "status": "success"
      }

    - For user with admin rights:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "tile_providers": [
            {
              "api_key_is_missing": false,
              "attribution": "<Map Attribution for OpenStreetMap>",
              "default": true,
              "default_for_user": true,
              "enabled": true,
              "id": "osm",
              "name": "OSM",
              "subdomains": "",
              "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            },
            {
              "api_key_is_missing": false,
              "attribution": "<Map Attribution for OpenStreetMap (de)>",
              "default": false,
              "default_for_user": true,
              "enabled": false,
              "id": "osm_de",
              "name": "OSM (de)",
              "subdomains": "",
              "url": "https://tile.openstreetmap.de/{z}/{x}/{y}.png",
            },
            {
              "api_key_is_missing": false,
              "attribution": "<Map Attribution for OpenStreetMap (fr)>",
              "default": false,
              "default_for_user": true,
              "enabled": false,
              "id": "osm_fr",
              "name": "OSM (fr)",
              "subdomains": "",
              "url": "https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
            },
            {
              "api_key_is_missing": false,
              "attribution": "<Map Attribution for CyclOSM>",
              "default": false,
              "default_for_user": true,
              "enabled": true,
              "id": "cyclosm",
              "name": "CyclOSM",
              "subdomains": "a,b,c",
              "url": "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
            },
            {
              "api_key_is_missing": true,
              "attribution": "<Map Attribution for Stadia Alidade Smooth>",
              "default": false,
              "default_for_user": true,
              "enabled": false,
              "id": "stadiamaps_alidade_smooth",
              "name": "Stadia Alidade Smooth",
              "subdomains": "",
              "url": "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}.png?apikey={apikey}",
            },
            {
              "api_key_is_missing": true,
              "attribution": "<Map Attribution for Stadia Alidade Outdoors>",
              "default": false,
              "default_for_user": true,
              "enabled": false,
              "id": "stadiamaps_outdoors",
              "name": "Stadia Outdoors",
              "subdomains": "",
              "url": "https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}.png?apikey={apikey}",
            },
            {
              "api_key_is_missing": true,
              "attribution": "<Map Attribution for Thunderforest Landscape>",
              "default": false,
              "default_for_user": true,
              "enabled": false,
              "id": "thunderforest_landscape",
              "name": "Thunderforest Landscape",
              "subdomains": "",
              "url": "https://api.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey={apikey}",
            },
            {
              "api_key_is_missing": true,
              "attribution": "<Map Attribution for Thunderforest Outdoors>",
              "default": false,
              "default_for_user": true,
              "enabled": false,
              "id": "thunderforest_outdoors",
              "name": "Thunderforest Outdoors",
              "subdomains": "",
              "url": "https://api.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey={apikey}",
            },
          ]
        },
        "status": "success"
      }

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 500: ``error on getting tile providers``
    """

    try:
        config = AppConfig.query.one()
        has_admin_rights = auth_user and auth_user.role >= UserRole.ADMIN.value
        tile_providers = (
            current_app.config["TILE_PROVIDERS"]
            if has_admin_rights
            else config.available_tile_providers
        )
        return {
            "status": "success",
            "data": {
                "tile_providers": [
                    {
                        "attribution": tile_provider_config.attribution,
                        "id": tile_provider,
                        "name": tile_provider_config.name,
                        "default": (
                            tile_provider == config.default_tile_provider
                        ),
                        "default_for_user": (
                            tile_provider == auth_user.default_tile_provider
                            if (
                                auth_user
                                and auth_user.default_tile_provider
                                in current_app.config[
                                    "available_tile_providers"
                                ]
                            )
                            else tile_provider == config.default_tile_provider
                        ),
                        **(
                            {
                                "api_key_is_missing": (
                                    tile_provider_config.api_key_is_missing
                                ),
                                "enabled": (
                                    tile_provider in config.tile_providers
                                    if config.tile_providers
                                    else tile_provider == DEFAULT_TILE_PROVIDER
                                ),
                            }
                            if has_admin_rights
                            else {"enabled": True}
                        ),
                    }
                    for tile_provider, tile_provider_config in tile_providers.items()
                ],
            },
        }
    except (MultipleResultsFound, NoResultFound) as e:
        return handle_error_and_return_response(
            e, message="error on getting tile providers"
        )


@config_blueprint.route(
    "/tile-providers/<string:tile_provider>", methods=["PATCH"]
)
@require_auth(scopes=["application:write"], role=UserRole.ADMIN)
def set_application_tile_providers(
    auth_user: "User", tile_provider: str
) -> Union[Dict, HttpResponse]:
    """
    Update tile provider for the application.

    **Example request**:

    .. sourcecode:: http

      POST /api/tile-providers/default HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success"
      }

    :param string tile_provider: tile provider id

    :<json string default: default status
    :<json string enabled: enabled status

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid payload``
        - ``default tile provider cannot be disabled, please set another provider as default first``
        - ``no api key is not set for this tile provider, please update application config first``
        - ``tile provided 'osm' can not be disabled when it is the only tile provider``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
    :statuscode 404: ``tile provider not found``
    :statuscode 500: ``error on getting tile providers``
    """

    if tile_provider not in current_app.config["TILE_PROVIDERS"]:
        return NotFoundErrorResponse(
            f"tile provider '{tile_provider}' does not exist"
        )

    config_data = request.get_json()
    if (
        not config_data
        or config_data.get("default") is None
        or config_data.get("enabled") is None
    ):
        return InvalidPayloadErrorResponse()

    if config_data["default"] and not config_data["enabled"]:
        return InvalidPayloadErrorResponse(
            "default tile provider cannot be disabled, please set another "
            "provider as default first"
        )

    try:
        config = AppConfig.query.one()

        if config_data["enabled"]:
            config.tile_providers = list(
                {*config.tile_providers, tile_provider}
            )
        else:
            config.tile_providers = [
                enabled_tile_provider
                for enabled_tile_provider in config.tile_providers
                if enabled_tile_provider != tile_provider
            ]

        if config_data["default"]:
            config.default_tile_provider = tile_provider
        elif (
            tile_provider == "osm"
            and config.default_tile_provider == DEFAULT_TILE_PROVIDER
            and config.tile_providers == [DEFAULT_TILE_PROVIDER]
        ):
            db.session.rollback()
            return InvalidPayloadErrorResponse(
                "tile provided 'osm' can not be disabled when it is "
                "the only tile provider"
            )
        elif config.default_tile_provider == tile_provider:
            config.default_tile_provider = DEFAULT_TILE_PROVIDER

        if (
            tile_provider in config.tile_providers
            and current_app.config["TILE_PROVIDERS"][
                tile_provider
            ].api_key_is_missing
        ):
            db.session.rollback()
            return InvalidPayloadErrorResponse(
                "no api key is not set for this tile provider, please update "
                "application config first"
            )

        if not config.tile_providers:
            config.tile_providers = [DEFAULT_TILE_PROVIDER]
            config.default_tile_provider = DEFAULT_TILE_PROVIDER

        db.session.commit()
        update_app_config_from_database(current_app, config)
        return {"status": "success"}
    except (MultipleResultsFound, NoResultFound) as e:
        return handle_error_and_return_response(
            e, message="error on getting tile providers"
        )
