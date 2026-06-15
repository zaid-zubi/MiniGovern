from fastapi import Query
from enum import Enum


class Language(str, Enum):
    EN = "en"
    AR = "ar"