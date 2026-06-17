from fastapi import status

from core.settings.base_exception import AppException


class CategoryNotFound(AppException):
    def __init__(self, message: str = "Category not found"):
        super().__init__(
            message,
            status.HTTP_404_NOT_FOUND,
        )


class CategoryAlreadyExists(AppException):
    def __init__(self, message: str = "Category already exists"):
        super().__init__(
            message,
            status.HTTP_409_CONFLICT,
        )


class CategoryAlreadyAssigned(AppException):
    def __init__(self, message: str = "Category already assigned"):
        super().__init__(
            message,
            status.HTTP_409_CONFLICT,
        )


class CategoryNotAssigned(AppException):
    def __init__(self, message: str = "Category is not assigned"):
        super().__init__(
            message,
            status.HTTP_404_NOT_FOUND,
        )
