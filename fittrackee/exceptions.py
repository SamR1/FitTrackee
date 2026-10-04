from typing import Optional


class GenericException(Exception):
    def __init__(
        self, status: str, message: str, e: Optional[Exception] = None
    ) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.e = e


class TaskException(Exception):
    pass


class EmailConfigException(Exception):
    pass


class FileException(Exception):
    pass


class ImageMaxPixelsException(Exception):
    def __init__(self, max_size: int, file_size: int) -> None:
        super().__init__("image max pixels limit exceeded")
        self.max_size = max_size
        self.file_size = file_size
