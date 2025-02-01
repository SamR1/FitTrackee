from fittrackee.exceptions import GenericException


class CommentForbiddenException(GenericException):
    def __init__(self) -> None:
        super().__init__("error", "you do not have permissions")
