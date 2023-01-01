from typing import Optional

from fittrackee.exceptions import GenericException


class ActivityException(GenericException):
    def __init__(self, message: str) -> None:
        super().__init__(status='error', message=message)


class ActorNotFoundException(GenericException):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            status='error',
            message=f'Actor not found{ f": {message}" if message else ""}.',
        )


class DomainNotFoundException(GenericException):
    def __init__(self, domain: str) -> None:
        super().__init__(
            status='error',
            message=f"Domain '{domain}' not found.",
        )


class FederationDisabledException(GenericException):
    def __init__(self) -> None:
        super().__init__(status='error', message='Federation is disabled.')


class InvalidSignatureException(GenericException):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            status='error',
            message=f'Invalid signature{f": {message}" if message else ""}.',
        )


class InvalidWorkoutException(GenericException):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            status='error',
            message=(
                f'Invalid workout data{f": {message}" if message else ""}.'
            ),
        )


class ObjectNotFoundException(GenericException):
    def __init__(self, object_type: str, activity_type: str) -> None:
        super().__init__(
            status='error',
            message=f"{object_type} not found for {activity_type}.",
        )


class SenderNotFoundException(GenericException):
    def __init__(self) -> None:
        super().__init__(
            status='error',
            message='Sender not found.',
        )


class RemoteActorException(GenericException):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            status='error',
            message=(
                f'Invalid remote actor{ f": {message}" if message else ""}.'
            ),
        )


class RemoteServerException(GenericException):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            status='error',
            message=(message if message else 'Invalid remote server'),
        )


class UnsupportedActivityException(GenericException):
    def __init__(self, activity_type: str) -> None:
        super().__init__(
            status='error',
            message=f"Unsupported activity '{activity_type}'.",
        )
