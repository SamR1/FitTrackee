from typing import Optional

from fittrackee.exceptions import GenericException


class ActorNotFoundException(GenericException):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            status='error',
            message=f'Actor not found{ f": {message}" if message else ""}.',
        )


class FederationDisabledException(GenericException):
    def __init__(self) -> None:
        super().__init__(
            status='error',
            message='Can not create activity, federation is disabled.',
        )


class InvalidSignatureException(GenericException):
    def __init__(self) -> None:
        super().__init__(
            status='error',
            message='Invalid signature.',
        )


class SenderNotFoundException(GenericException):
    def __init__(self) -> None:
        super().__init__(
            status='error',
            message='Sender not found.',
        )


class UnsupportedActivityException(GenericException):
    def __init__(self, activity_type: str) -> None:
        super().__init__(
            status='error',
            message=f"Unsupported activity '{activity_type}'.",
        )
