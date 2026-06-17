from fastapi import status

from core.settings.base_exception import AppException
from core.settings.constants import Error


class DatasourceNotFound(AppException):
    def __init__(self, message: str = "Datasource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class DatasourceConnectionFailed(AppException):
    def __init__(self, message: str = Error.DATABASE_CONNECTION_FAILUER):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)
