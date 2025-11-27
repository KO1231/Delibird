import hashlib


def hash_hex(text: str) -> str:
    """文字列をSHA-256でハッシュ化し、16進数文字列として返す"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
