from fittrackee.exceptions import GenericException


class InvalidEquipmentException(Exception):
    ...


class InvalidGPXException(GenericException):
    ...


class WorkoutException(GenericException):
    ...


class WorkoutGPXException(GenericException):
    ...
