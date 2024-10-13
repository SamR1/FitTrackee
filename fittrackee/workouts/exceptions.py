from fittrackee.exceptions import GenericException


class InvalidGPXException(GenericException):
    pass


class WorkoutException(GenericException):
    pass


class WorkoutGPXException(GenericException):
    pass


class WorkoutForbiddenException(GenericException):
    def __init__(self) -> None:
        super().__init__('error', 'you do not have permissions')
