from fittrackee.exceptions import GenericException


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
