from json import dumps
from typing import Dict, List, Optional, Union

from flask import Response
from flask_sqlalchemy import SQLAlchemy

from fittrackee import appLog


def get_empty_data_for_datatype(data_type: str) -> Union[str, List]:
    return '' if data_type in ['gpx', 'chart_data'] else []


def display_readable_file_size(size_in_bytes: Union[float, int]) -> str:
    """
    Return readable file size from size in bytes
    """
    if size_in_bytes == 0:
        return '0 bytes'
    if size_in_bytes == 1:
        return '1 byte'
    for unit in [' bytes', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_in_bytes) < 1024.0:
            return f'{size_in_bytes:3.1f}{unit}'
        size_in_bytes /= 1024.0
    return f'{size_in_bytes} bytes'


class HttpResponse(Response):
    def __init__(
        self,
        response: Optional[Union[str, Dict]] = None,
        status_code: Optional[int] = None,
        content_type: Optional[str] = None,
    ) -> None:
        if isinstance(response, dict):
            response = dumps(response)
            content_type = (
                'application/json' if content_type is None else content_type
            )
        super().__init__(
            response=response,
            status=status_code,
            content_type=content_type,
        )


class GenericErrorResponse(HttpResponse):
    def __init__(
        self,
        status_code: int,
        message: Union[str, List],
        status: Optional[str] = None,
    ) -> None:
        response = {
            'status': 'error' if status is None else status,
            'message': message,
        }
        super().__init__(
            response=response,
            status_code=status_code,
        )


class InvalidPayloadErrorResponse(GenericErrorResponse):
    def __init__(
        self,
        message: Optional[Union[str, List]] = None,
        status: Optional[str] = None,
    ) -> None:
        message = 'invalid payload' if message is None else message
        super().__init__(status_code=400, message=message, status=status)


class DataInvalidPayloadErrorResponse(HttpResponse):
    def __init__(self, data_type: str, status: Optional[str] = None) -> None:
        response = {
            'status': 'error' if status is None else status,
            'data': {data_type: get_empty_data_for_datatype(data_type)},
        }
        super().__init__(response=response, status_code=400)


class UnauthorizedErrorResponse(GenericErrorResponse):
    def __init__(self, message: Optional[str] = None) -> None:
        message = (
            'invalid token, please request a new token'
            if message is None
            else message
        )
        super().__init__(status_code=401, message=message)


class ForbiddenErrorResponse(GenericErrorResponse):
    def __init__(self, message: Optional[str] = None) -> None:
        message = 'you do not have permissions' if message is None else message
        super().__init__(status_code=403, message=message)


class NotFoundErrorResponse(GenericErrorResponse):
    def __init__(self, message: str) -> None:
        super().__init__(status_code=404, message=message, status='not found')


class UserNotFoundErrorResponse(NotFoundErrorResponse):
    def __init__(self) -> None:
        super().__init__(message='user does not exist')


class DataNotFoundErrorResponse(HttpResponse):
    def __init__(self, data_type: str, message: Optional[str] = None) -> None:
        response = {
            'status': 'not found',
            'data': {data_type: get_empty_data_for_datatype(data_type)},
        }
        if message:
            response['message'] = message
        super().__init__(response=response, status_code=404)


class PayloadTooLargeErrorResponse(GenericErrorResponse):
    def __init__(
        self, file_type: str, file_size: Optional[int], max_size: Optional[int]
    ) -> None:
        readable_file_size = (
            f'({display_readable_file_size(file_size)}) ' if file_size else ''
        )
        readable_max_size = (
            display_readable_file_size(max_size) if max_size else 'limit'
        )
        message = (
            f'Error during {file_type} upload, file size {readable_file_size}'
            f'exceeds {readable_max_size}.'
        )
        super().__init__(status_code=413, message=message, status='fail')


class InternalServerErrorResponse(GenericErrorResponse):
    def __init__(
        self, message: Optional[str] = None, status: Optional[str] = None
    ):
        message = (
            'error, please try again or contact the administrator'
            if message is None
            else message
        )
        super().__init__(status_code=500, message=message, status=status)


def handle_error_and_return_response(
    error: Exception,
    message: Optional[str] = None,
    status: Optional[str] = None,
    db: Optional[SQLAlchemy] = None,
) -> HttpResponse:
    if db is not None:
        db.session.rollback()
    appLog.error(error)
    return InternalServerErrorResponse(message=message, status=status)
