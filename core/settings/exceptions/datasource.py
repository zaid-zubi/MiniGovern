from fastapi import status
from core.settings.base_exception import AppException


class DatasourceNotFound(AppException):
    def __init__(self, message: str = "Datasource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class DatasourceConnectionFailed(AppException):
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)