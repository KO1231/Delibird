import os
from urllib.parse import quote
from urllib.parse import urlparse

# リダイレクト先URLで許可するスキーム
_ALLOWED_REDIRECT_TARGET_SCHEMES = ["http", "https"]
# リクエストの受け先ドメインの許可リスト
_ALLOWED_DOMAIN = set([d.strip().lower() for d in str(os.environ["ALLOWED_DOMAIN"]).split(",")])


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


def parse_domain(domain: str) -> str:
    """リクエストのドメインをパースして返す。"""
    domain = domain.strip().lower()
    if (not domain) or (domain not in _ALLOWED_DOMAIN):
        raise ValueError(f"Invalid or missing domain: {domain}, allowed: {_ALLOWED_DOMAIN}")
    return domain
