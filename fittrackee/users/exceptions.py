class BlockUserException(Exception):
    pass


class FollowRequestAlreadyProcessedError(Exception):
    pass


class FollowRequestAlreadyRejectedError(Exception):
    pass


class InvalidEmailException(Exception):
    pass


class InvalidNotificationTypeException(Exception):
    pass


class InvalidUserRole(Exception):
    def __init__(self) -> None:
        super().__init__("invalid role")


class MissingAdminIdException(Exception):
    pass


class MissingReportIdException(Exception):
    pass


class NotExistingFollowRequestError(Exception):
    pass


class OwnerException(Exception):
    pass


class UserAlreadyReactivatedException(Exception):
    def __init__(self) -> None:
        super().__init__("user account already reactivated")


class UserAlreadySuspendedException(Exception):
    def __init__(self) -> None:
        super().__init__("user account already suspended")


class UserControlsException(Exception):
    pass


class UserCreationException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class UserTaskException(Exception):
    pass


class UserTaskForbiddenException(Exception):
    def __init__(self) -> None:
        super().__init__("you do not have permissions")
