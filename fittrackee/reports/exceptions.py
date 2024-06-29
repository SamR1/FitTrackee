class InvalidReportException(Exception): ...


class InvalidReporterException(Exception): ...


class ReportNotFoundException(Exception): ...


class ReportCommentForbiddenException(Exception): ...


class ReportForbiddenException(Exception): ...


class SuspendedObjectException(Exception):
    def __init__(self, object_type: str) -> None:
        super().__init__(f'{object_type} already suspended')
        self.object_type = object_type
