from fastapi import status
from core.settings.base_exception import AppException


class DatasetNotFound(AppException):
    def __init__(self, message: str = "Dataset not found"):
        super().__init__(
            message,
            status.HTTP_404_NOT_FOUND,
        )
