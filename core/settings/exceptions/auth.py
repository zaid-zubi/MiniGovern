from fastapi import status

from core.settings.base_exception import AppException
from core.settings.constants import Error


class UserNotFound(AppException):
    def __init__(self, message: str | None = None):
        super().__init__(
            message or Error.USER_NOT_FOUND,
            status.HTTP_404_NOT_FOUND,
        )


class IncorrectEmailOrPassword(AppException):
    def __init__(self, message: str | None = None):
        super().__init__(
            message or Error.INCORRECT_EMAIL_OR_PASSWORD,
            status.HTTP_401_UNAUTHORIZED,
        )


class UserAlreadyExists(AppException):
    def __init__(self, message: str | None = None):
        super().__init__(
            message or "Email already registered",
            status.HTTP_409_CONFLICT,
        )


class InactiveUser(AppException):
    def __init__(self, message: str | None = None):
        super().__init__(
            message or "User is inactive",
            status.HTTP_403_FORBIDDEN,
        )
