from datetime import timedelta
from typing import Optional

import humanize
from flask import Request, current_app

from .responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    PayloadTooLargeErrorResponse,
)


def verify_extension_and_size(
    file_type: str, req: Request
) -> Optional[HttpResponse]:
    """
    Return error Response if file is invalid
    """
    if 'file' not in req.files:
        return InvalidPayloadErrorResponse('no file part', 'fail')

    file = req.files['file']
    if not file.filename or file.filename == '':
        return InvalidPayloadErrorResponse('no selected file', 'fail')

    allowed_extensions = (
        'WORKOUT_ALLOWED_EXTENSIONS'
        if file_type == 'workout'
        else 'PICTURE_ALLOWED_EXTENSIONS'
    )

    file_extension = (
        file.filename.rsplit('.', 1)[1].lower()
        if '.' in file.filename
        else None
    )
    max_file_size = current_app.config['max_single_file_size']

    if not (
        file_extension
        and file_extension in current_app.config[allowed_extensions]
    ):
        return InvalidPayloadErrorResponse(
            'file extension not allowed', 'fail'
        )

    if (
        file_extension != 'zip'
        and req.content_length is not None
        and req.content_length > max_file_size
    ):
        return PayloadTooLargeErrorResponse(
            file_type=file_type,
            file_size=req.content_length,
            max_size=max_file_size,
        )

    return None


def get_readable_duration(duration: int, locale: Optional[str] = None) -> str:
    """
    Return readable and localized duration from duration in seconds
    """
    if locale is None:
        locale = 'en'
    if locale != 'en':
        try:
            _t = humanize.i18n.activate(locale)  # noqa
        except FileNotFoundError:
            locale = 'en'
    readable_duration = humanize.naturaldelta(timedelta(seconds=duration))
    if locale != 'en':
        humanize.i18n.deactivate()
    return readable_duration
