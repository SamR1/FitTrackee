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


class MissingAdminIdException(Exception):
    pass


class MissingReportIdException(Exception):
    pass


class InvalidUserException(Exception):
    pass


class NotExistingFollowRequestError(Exception):
    pass


class UserAlreadySuspendedException(Exception):
    pass


class UserControlsException(Exception):
    pass


class UserCreationException(Exception):
    pass


class UserNotFoundException(Exception):
    pass
