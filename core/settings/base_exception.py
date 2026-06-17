from fastapi import status


class AppException(Exception):
    """
    Base application exception (not HTTP-aware)
    """

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
