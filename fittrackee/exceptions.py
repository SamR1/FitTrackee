from typing import Optional


class GenericException(Exception):
    def __init__(
        self, status: str, message: str, e: Optional[Exception] = None
    ) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.e = e
