import json
import os
from http import HTTPStatus

IS_DEV = (os.environ.get("DELIBIRD_ENV") == "dev")


def _generate_response_headers(content_type: str = None) -> dict[str, str]:
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
        "frame-ancestors 'none'",
        "base-uri 'none'",
        "upgrade-insecure-requests"
    ]
    headers["Content-Security-Policy"] = "; ".join(csp)

    if IS_DEV:
        # 開発環境(local)用にCORS許可
        headers["X-Dev"] = "true"
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "OPTIONS, POST"
        headers["Access-Control-Allow-Headers"] = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Dev"
        headers["Access-Control-Allow-Credentials"] = "true"

    return headers


def error_response(status: HTTPStatus):
    return {
        "statusCode": status.value,
        "headers": _generate_response_headers(),
        "body": json.dumps({"message": status.phrase})
    }


def success_response(status: HTTPStatus, body: str | dict, content_type: str = None):
    return {
        "statusCode": status.value,
        "headers": _generate_response_headers(content_type),
        "body": body if isinstance(body, str) else json.dumps(body),
    }


def redirect_response(redirect_url: str):
    headers = _generate_response_headers()
    del headers["Content-Type"]

    return {
        "statusCode": HTTPStatus.FOUND.value,
        "headers": {
            **headers,
            "Location": redirect_url
        },
        "body": ""
    }
