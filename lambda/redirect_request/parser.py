from urllib.parse import quote
from urllib.parse import urlparse

# リダイレクト先URLで許可するスキーム
_ALLOWED_REDIRECT_TARGET_SCHEMES = ["http", "https"]


def parse_request_path(path: str) -> str:
    """入力されたパスパラメータをパースして、安全な形式にエンコードして返す。"""
    return quote(path.lstrip("/")) if path else ""


def parse_origin(url: str) -> str:
    """リダイレクト先URLの妥当性を確認して返す。"""
    parsed = urlparse(url)
    if (not parsed.scheme) or (parsed.scheme not in _ALLOWED_REDIRECT_TARGET_SCHEMES):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
    if (not parsed.netloc):
        raise ValueError("URL must have a valid netloc.")
    return parsed.geturl()
