class FollowRequestAlreadyProcessedError(Exception):
    ...


class FollowRequestAlreadyRejectedError(Exception):
    ...


class InvalidEmailException(Exception):
    ...


class InvalidUserException(Exception):
    ...


class NotExistingFollowRequestError(Exception):
    ...


class UserNotFoundException(Exception):
    ...
