from fittrackee.exceptions import GenericException


class InvalidSignatureException(GenericException):
    def __init__(self) -> None:
        super().__init__(
            status='error',
            message='Invalid signature.',
        )
