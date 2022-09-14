from typing import Dict, Union

from flask import Blueprint, current_app, request
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from fittrackee import db
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.users.decorators import authenticate_as_admin
from fittrackee.users.models import User
from fittrackee.users.utils.controls import is_valid_email

from .models import AppConfig
from .utils import update_app_config_from_database, verify_app_config

config_blueprint = Blueprint('config', __name__)


@config_blueprint.route('/config', methods=['GET'])
def get_application_config() -> Union[Dict, HttpResponse]:
    """
    Get Application config

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
          "admin_contact": "admin@example.com",
          "gpx_limit_import": 10,
          "is_email_sending_enabled": true,
          "is_registration_enabled": false,
          "max_single_file_size": 1048576,
          "max_users": 0,
          "max_zip_file_size": 10485760,
          "map_attribution": "&copy; <a href=http://www.openstreetmap.org/copyright>OpenStreetMap</a> contributors"
          "version": "0.6.12"
        },
        "status": "success"
      }

    :statuscode 200: success
    :statuscode 500: error on getting configuration
    """

    try:
        config = AppConfig.query.one()
        return {'status': 'success', 'data': config.serialize()}
    except (MultipleResultsFound, NoResultFound) as e:
        return handle_error_and_return_response(
            e, message='error on getting configuration'
        )


@config_blueprint.route('/config', methods=['PATCH'])
@authenticate_as_admin
def update_application_config(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Update Application config

    Authenticated user must be an admin

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
          "admin_contact": "admin@example.com",
          "gpx_limit_import": 10,
          "is_email_sending_enabled": true,
          "is_registration_enabled": false,
          "max_single_file_size": 1048576,
          "max_users": 10,
          "max_zip_file_size": 10485760,
          "map_attribution": "&copy; <a href=http://www.openstreetmap.org/copyright>OpenStreetMap</a> contributors"
          "version": "0.6.12"
        },
        "status": "success"
      }

    :<json string admin_contact: email to contact the administrator
    :<json integer gpx_limit_import: max number of files in zip archive
    :<json boolean is_registration_enabled: is registration enabled ?
    :<json integer max_single_file_size: max size of a single file
    :<json integer max_users: max users allowed to register on instance
    :<json integer max_zip_file_size: max size of a zip archive

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
        - valid email must be provided for admin contact
    :statuscode 403: you do not have permissions
    :statuscode 500: error when updating configuration
    """
    config_data = request.get_json()
    if not config_data:
        return InvalidPayloadErrorResponse()

    ret = verify_app_config(config_data)
    admin_contact = config_data.get('admin_contact')
    if admin_contact and not is_valid_email(admin_contact):
        ret.append('valid email must be provided for admin contact')
    if ret:
        return InvalidPayloadErrorResponse(message=ret)

    try:
        config = AppConfig.query.one()
        if 'gpx_limit_import' in config_data:
            config.gpx_limit_import = config_data.get('gpx_limit_import')
        if 'max_single_file_size' in config_data:
            config.max_single_file_size = config_data.get(
                'max_single_file_size'
            )
        if 'max_zip_file_size' in config_data:
            config.max_zip_file_size = config_data.get('max_zip_file_size')
        if 'max_users' in config_data:
            config.max_users = config_data.get('max_users')
        if 'admin_contact' in config_data:
            config.admin_contact = admin_contact if admin_contact else None

        if config.max_zip_file_size < config.max_single_file_size:
            return InvalidPayloadErrorResponse(
                'Max. size of zip archive must be equal or greater than '
                'max. size of uploaded files'
            )
        db.session.commit()
        update_app_config_from_database(current_app, config)
        return {'status': 'success', 'data': config.serialize()}

    except Exception as e:
        return handle_error_and_return_response(
            e, message='error when updating configuration'
        )


@config_blueprint.route('/ping', methods=['GET'])
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

    :statuscode 200: success

    """
    return {'status': 'success', 'message': 'pong!'}
