import html
import json
import os
from http import HTTPStatus
from typing import Optional

from util.environment_util import get_env_var
from util.static_resource_util import load_static_html

_IS_DEV = (os.environ.get("DELIBIRD_ENV") == "dev")
_COMMIT_HASH = str(get_env_var("COMMIT_HASH", "")) if _IS_DEV else ""
_STATIC_FOOTER: Optional[str] = html.escape(get_env_var("STATIC_FOOTER", ""))


def _load_error_html(status: HTTPStatus) -> tuple[Optional[str], bool]:
    if not (status.is_client_error or status.is_server_error):
        raise ValueError("Status code must be a client error (4xx) or server error (5xx).")

    # 該当するステータスコードのHTMLを探す
    html_content = load_static_html(
        f"error/{status.value}.html",
        {"STATIC_FOOTER": _STATIC_FOOTER} if _STATIC_FOOTER else None
    )
    return html_content, html_content is not None


def _generate_response_headers(content_type: str = None, use_css: bool = False) -> dict[str, str]:
    headers = {
        "Content-Type": content_type or "application/json;charset=utf-8",
        "Cache-Control": "private, no-cache, no-store, max-age=0, must-revalidate",
        "Pragma": "no-cache",
        "Referrer-Policy": "same-origin",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-Robots-Tag": "noindex, nofollow",
        "Strict-Transport-Security": "max-age=31536000; preload",
    }

    csp = [
        "default-src 'none'",
        "style-src https://static.kazutech.jp/l/css/" if use_css else None,
        "frame-ancestors 'none'",
        "base-uri 'none'",
        "upgrade-insecure-requests"
    ]
    headers["Content-Security-Policy"] = "; ".join(filter(None, csp))

    if _IS_DEV:
        # 開発環境(local)用にCORS許可
        headers["X-Dev"] = "true"
        headers["X-Commit-Hash"] = _COMMIT_HASH
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "OPTIONS, POST"
        headers["Access-Control-Allow-Headers"] = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Dev"
        headers["Access-Control-Allow-Credentials"] = "true"

    return headers


def error_response(status: HTTPStatus):
    _html, load_success = _load_error_html(status)

    headers = _generate_response_headers("text/html;charset=utf-8" if load_success else None, use_css=load_success)
    body = _html if load_success else json.dumps({"message": status.phrase})

    return {
        "statusCode": status.value,
        "headers": headers,
        "body": body
    }


def success_response(status: HTTPStatus, body: str | dict, content_type: str = None):
    return {
        "statusCode": status.value,
        "headers": _generate_response_headers(content_type),
        "body": body if isinstance(body, str) else json.dumps(body),
    }


def redirect_response(redirect_url: str, status: HTTPStatus = HTTPStatus.FOUND):
    if not status.is_redirection:
        raise ValueError(f"Status code {status} is not a redirection status.")
    headers = _generate_response_headers()
    del headers["Content-Type"]

    return {
        "statusCode": status.value,
        "headers": {
            **headers,
            "Location": redirect_url
        },
        "body": ""
    }
