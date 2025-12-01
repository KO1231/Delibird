import secrets

_NONCE_BYTE_LENGTH = 32


def create_nonce(length: int = None) -> str:
    return secrets.token_hex(length or _NONCE_BYTE_LENGTH)
