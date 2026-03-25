from typing import TYPE_CHECKING, Dict, Tuple, Union

from flask import Blueprint, current_app, request, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge

from fittrackee import appLog, db, limiter
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    ForbiddenErrorResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    PayloadTooLargeErrorResponse,
    get_error_response_if_file_is_invalid,
    handle_error_and_return_response,
)
from fittrackee.utils import decode_short_id

from .exceptions import MediaException
from .media_service import MediaService
from .models import MEDIA_DESCRIPTION_MAX_CHARACTERS, Media

if TYPE_CHECKING:
    from flask import Response

    from fittrackee.users.models import User

    from ..responses import HttpResponse

api_media_blueprint = Blueprint("api_media", __name__)
media_blueprint = Blueprint("media", __name__)

NOT_FOUND_MESSAGE = "media not found"


@media_blueprint.route("/media/<media_file_name>", methods=["GET"])
@limiter.exempt
def create_media(media_file_name: str) -> Union["Response", "HttpResponse"]:
    """
    Get media.

    **Example request**:

    .. sourcecode:: http

      GET /media/c49dbe56b45a41509549bffd4c050438.png HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: image/png

    :param string media_file_name: media file name

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``media not found``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    try:
        media = Media.query.filter_by(file_name=media_file_name).first()
        if not media:
            return NotFoundErrorResponse(NOT_FOUND_MESSAGE)
        return send_from_directory(
            current_app.config["UPLOAD_FOLDER"],
            media.file_path,
        )
    except Exception as e:
        return handle_error_and_return_response(e)


@api_media_blueprint.route("/media", methods=["POST"])
@require_auth(scopes=["media:write"])
def post_media(auth_user: "User") -> Union[Tuple[Dict, int], "HttpResponse"]:
    """
    Post media.

    For now only images are supported.

    **Scope**: ``media:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/media/ HTTP/1.1
      Content-Type: multipart/form-data

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

      {
        'description': None,
        'id': '9376Mad4SnUoopkCszqHB6',
        'url': 'https://example.com/media/c49dbe56b45a41509549bffd4c050438.png'
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: media created
    :statuscode 400:
        - ``no file part``
        - ``no selected file``
        - ``file extension not allowed``
        - ``error when reading media file``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 413: ``error during media upload: file size exceeds 10.0MB``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    try:
        response_object = get_error_response_if_file_is_invalid(
            "media", request
        )
    except RequestEntityTooLarge as e:
        appLog.error(e)
        return PayloadTooLargeErrorResponse(
            file_type="media",
            file_size=request.content_length,
            max_size=current_app.config["MAX_CONTENT_LENGTH"],
        )
    if response_object:
        return response_object

    media_service = MediaService(auth_user, request.files["file"])
    try:
        media = media_service.create_image_media()
    except MediaException as e:
        return InvalidPayloadErrorResponse(e.message, status=e.status)
    return media.serialize(), 201


@api_media_blueprint.route("/media/<string:media_short_id>", methods=["PATCH"])
@require_auth(scopes=["media:write"])
def update_media_description(
    auth_user: "User", media_short_id: str
) -> Union[Tuple[Dict, int], "HttpResponse"]:
    """
    Update media description.

    **Scope**: ``media:write``

    **Example request**:

    .. sourcecode:: http

      PATCH /api/media/9376Mad4SnUoopkCszqHB6 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        'description': 'image description',
        'id': '9376Mad4SnUoopkCszqHB6',
        'url': 'https://example.com/media/c49dbe56b45a41509549bffd4c050438.png'
      }

    :param string media_short_id: media attachment short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: media created
    :statuscode 400: ``invalid payload``
    :statuscode 404: ``media not found``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    data = request.get_json()
    if not data or "description" not in data:
        return InvalidPayloadErrorResponse()

    media = Media.query.filter_by(uuid=decode_short_id(media_short_id)).first()
    if not media:
        return NotFoundErrorResponse(NOT_FOUND_MESSAGE)

    if media.user_id != auth_user.id:
        return ForbiddenErrorResponse()

    media.description = (
        data["description"][:MEDIA_DESCRIPTION_MAX_CHARACTERS]
        if data.get("description")
        else ""
    )
    db.session.commit()
    return media.serialize()


@api_media_blueprint.route(
    "/media/<string:media_short_id>", methods=["DELETE"]
)
@require_auth(scopes=["media:write"])
def delete_media(
    auth_user: "User", media_short_id: str
) -> Union[Tuple[Dict, int], "HttpResponse"]:
    """
    Delete media description.

    **Scope**: ``media:write``

    **Example request**:

    .. sourcecode:: http

      PATCH /api/media/9376Mad4SnUoopkCszqHB6 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT

    :param string media_short_id: media attachment short id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 204: media deleted
    :statuscode 404: ``media not found``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    media = Media.query.filter_by(uuid=decode_short_id(media_short_id)).first()
    if not media:
        return NotFoundErrorResponse(NOT_FOUND_MESSAGE)
    if media.user_id != auth_user.id:
        return ForbiddenErrorResponse()
    db.session.delete(media)
    db.session.commit()
    return {"status": "no content"}, 204
