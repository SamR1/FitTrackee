from json import dumps

from fittrackee import appLog
from flask import Response


def get_empty_data_for_datatype(data_type):
    return '' if data_type in ['gpx', 'chart_data'] else []


class HttpResponse(Response):
    def __init__(
        self,
        response=None,
        status_code=None,
        content_type=None,
    ):
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
    def __init__(self, status_code, message, status=None):
        response = {
            'status': 'error' if status is None else status,
            'message': message,
        }
        super().__init__(
            response=response,
            status_code=status_code,
        )


class InvalidPayloadErrorResponse(GenericErrorResponse):
    def __init__(self, message=None, status=None):
        message = 'Invalid payload.' if message is None else message
        super().__init__(status_code=400, message=message, status=status)


class DataInvalidPayloadErrorResponse(HttpResponse):
    def __init__(self, data_type, status=None):
        response = {
            'status': 'error' if status is None else status,
            'data': {data_type: get_empty_data_for_datatype(data_type)},
        }
        super().__init__(response=response, status_code=400)


class UnauthorizedErrorResponse(GenericErrorResponse):
    def __init__(self, message=None):
        message = (
            'Invalid token. Please request a new token.'
            if message is None
            else message
        )
        super().__init__(status_code=401, message=message)


class ForbiddenErrorResponse(GenericErrorResponse):
    def __init__(self, message=None):
        message = (
            'You do not have permissions.' if message is None else message
        )
        super().__init__(status_code=403, message=message)


class NotFoundErrorResponse(GenericErrorResponse):
    def __init__(self, message):
        super().__init__(status_code=404, message=message, status='not found')


class UserNotFoundErrorResponse(NotFoundErrorResponse):
    def __init__(self):
        super().__init__(message='User does not exist.')


class DataNotFoundErrorResponse(HttpResponse):
    def __init__(self, data_type, message=None):
        response = {
            'status': 'not found',
            'data': {data_type: get_empty_data_for_datatype(data_type)},
        }
        if message:
            response['message'] = message
        super().__init__(response=response, status_code=404)


class PayloadTooLargeErrorResponse(GenericErrorResponse):
    def __init__(self, message):
        super().__init__(status_code=413, message=message, status='fail')


class InternalServerErrorResponse(GenericErrorResponse):
    def __init__(self, message=None, status=None):
        message = (
            'Error. Please try again or contact the administrator.'
            if message is None
            else message
        )
        super().__init__(status_code=500, message=message, status=status)


def handle_error_and_return_response(
    error, message=None, status=None, db=None
):
    if db is not None:
        db.session.rollback()
    appLog.error(error)
    return InternalServerErrorResponse(message=message, status=status)
