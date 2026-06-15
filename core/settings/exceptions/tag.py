from fastapi import status
from core.settings.base_exception import AppException


class TagNotFound(AppException):
    def __init__(self, message: str = "Tag not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class TagAlreadyExists(AppException):
    def __init__(self, message: str = "Tag already exists"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class TagAlreadyAssigned(AppException):
    def __init__(self, message: str = "Tag already assigned"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class TagNotAssigned(AppException):
    def __init__(self, message: str = "Tag is not assigned"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)