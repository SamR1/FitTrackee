class InvalidReportActionAppealException(Exception):
    pass


class InvalidReportActionAppealUserException(Exception):
    pass


class InvalidReportActionException(Exception):
    pass


class InvalidReportException(Exception):
    pass


class InvalidReporterException(Exception):
    pass


class ReportActionAppealForbiddenException(Exception):
    pass


class ReportActionForbiddenException(Exception):
    pass


class ReportCommentForbiddenException(Exception):
    pass


class ReportForbiddenException(Exception):
    pass


class ReportNotFoundException(Exception):
    pass


class SuspendedObjectException(Exception):
    def __init__(self, object_type: str) -> None:
        super().__init__(f"{object_type} already suspended")
        self.object_type = object_type


class UserWarningExistsException(Exception):
    pass
