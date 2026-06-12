from cryptography.fernet import Fernet, InvalidToken

from core.config import settings


def encrypt_value(value: str) -> str:
    return Fernet(settings.encryption_key.encode()).encrypt(value.encode()).decode()


def decrypt_value(value: str) -> str:
    try:
        return Fernet(settings.encryption_key.encode()).decrypt(value.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt value") from exc
