from fittrackee.exceptions import GenericException


class InvalidDurationException(Exception):
    def __init__(self) -> None:
        super().__init__("invalid duration")


class InvalidGPXException(GenericException):
    pass


class WorkoutExceedingValueException(GenericException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            "invalid",
            "one or more values, entered or calculated, exceed the limits",
        )
        self.detail = detail


class WorkoutException(GenericException):
    pass


class WorkoutFileException(GenericException):
    pass


class WorkoutNoFileException(GenericException):
    def __init__(self) -> None:
        super().__init__("error", "no workout file provided")


class WorkoutGPXException(GenericException):
    pass


class WorkoutForbiddenException(GenericException):
    def __init__(self) -> None:
        super().__init__("error", "you do not have permissions")


class WorkoutRefreshException(GenericException):
    pass
