from fittrackee_api import appLog, db
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from ..users.utils import authenticate_as_admin
from .models import AppConfig
from .utils import update_app_config_from_database

config_blueprint = Blueprint('config', __name__)


@config_blueprint.route('/config', methods=['GET'])
def get_application_config():
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
          "gpx_limit_import": 10,
          "is_registration_enabled": false,
          "max_single_file_size": 1048576,
          "max_zip_file_size": 10485760,
          "max_users": 0
        },
        "status": "success"
      }

    :statuscode 200: success
    :statuscode 500: Error on getting configuration.
    """

    try:
        config = AppConfig.query.one()
        response_object = {'status': 'success', 'data': config.serialize()}
        return jsonify(response_object), 200
    except (MultipleResultsFound, NoResultFound) as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error on getting configuration.',
        }
        return jsonify(response_object), 500


@config_blueprint.route('/config', methods=['PATCH'])
@authenticate_as_admin
def update_application_config(auth_user_id):
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
          "gpx_limit_import": 10,
          "is_registration_enabled": true,
          "max_single_file_size": 1048576,
          "max_zip_file_size": 10485760,
          "max_users": 10
        },
        "status": "success"
      }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)

    :<json integrer gpx_limit_import: max number of files in zip archive
    :<json boolean is_registration_enabled: is registration enabled ?
    :<json integrer max_single_file_size: max size of a single file
    :<json integrer max_zip_file_size: max size of a zip archive
    :<json integrer max_users: max users allowed to register on instance

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 403: You do not have permissions.
    :statuscode 500: Error on updating configuration.
    """
    config_data = request.get_json()
    if not config_data:
        response_object = {'status': 'error', 'message': 'Invalid payload.'}
        return jsonify(response_object), 400

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

        db.session.commit()
        update_app_config_from_database(current_app, config)

        response_object = {'status': 'success', 'data': config.serialize()}
        code = 200

    except Exception as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error on updating configuration.',
        }
        code = 500
    return jsonify(response_object), code


@config_blueprint.route('/ping', methods=['GET'])
def health_check():
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
    return jsonify({'status': 'success', 'message': 'pong!'})
