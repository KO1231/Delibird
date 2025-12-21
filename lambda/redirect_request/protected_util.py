import os
from datetime import timedelta
from http import HTTPStatus

from models.delibird_nonce import DelibirdNonceTableModel
from util.date_util import get_jst_datetime_now
from util.nonce_util import create_nonce
from util.response_util import success_response, STATIC_FOOTER
from util.static_resource_util import load_function_html

NONCE_QUERY_KEY = "n"
CHALLENGE_QUERY_KEY = "c"

_NONCE_LIFETIME_SECONDS = int(os.environ["NONCE_LIFETIME_SECONDS"])


def protected_response(domain: str, slug: str, error_message: str = ""):
    script_nonce = create_nonce()
    request_nonce = _create_protected_request_nonce(domain, slug)

    html_content = load_function_html("static/protected.html", {
        "default_error_message": error_message,

        "challenge_query_key": CHALLENGE_QUERY_KEY,
        "nonce_query_key": NONCE_QUERY_KEY,
        "script_nonce": script_nonce,
        "request_nonce": request_nonce,
        "STATIC_FOOTER": STATIC_FOOTER if STATIC_FOOTER else None
    })

    return success_response(HTTPStatus.UNAUTHORIZED, html_content,
                            content_type='text/html;charset=utf-8', use_css=True, use_bootstrap_icons=True,
                            script_nonce=script_nonce)


def _create_protected_request_nonce(domain: str, slug: str) -> str:
    nonce = create_nonce()

    model = DelibirdNonceTableModel(nonce)
    model.domain = domain
    model.slug = slug
    model.expired_timestamp = int((get_jst_datetime_now() + timedelta(seconds=_NONCE_LIFETIME_SECONDS)).timestamp())
    model.save(condition=DelibirdNonceTableModel.nonce.does_not_exist())

    return nonce
