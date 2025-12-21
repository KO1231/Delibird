import os
from http import HTTPStatus
from typing import Optional

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

from ddb.models.delibird_link import DelibirdLinkTableModel, DelibirdLink
from portal_page.page import AdminPortalPage
from util.date_util import get_jst_datetime_now
from util.logger_util import setup_logger
from util.nonce_util import create_nonce
from util.response_util import error_response, success_response, STATIC_FOOTER
from util.static_resource_util import load_function_html

logger = setup_logger("admin_portal.link_list_page")
_ENVIRONMENT = str(os.environ["DELIBIRD_ENV"])
_LINK_PREFIX = str(os.environ["LINK_PREFIX"])


class PortalListPage(AdminPortalPage):
    @classmethod
    def _get_links_html(cls, domain: str, links: list[DelibirdLink], *, style_nonce: str = None, script_nonce: str = None) -> Optional[str]:
        # アクティブ/非アクティブのカウント
        active_count = sum(1 for link in links if link.check_active()[0])
        inactive_count = len(links) - active_count

        # 現在時刻を取得
        now = get_jst_datetime_now()

        return load_function_html("static/links.html", {
            'domain': domain,
            'delibird_environment': _ENVIRONMENT,
            'link_prefix': _LINK_PREFIX + "/" if _LINK_PREFIX else "",
            'links': links,
            'active_count': active_count,
            'inactive_count': inactive_count,
            'now': now,
            'style_nonce': style_nonce,
            'script_nonce': script_nonce,
            "STATIC_FOOTER": STATIC_FOOTER if STATIC_FOOTER else None
        })

    @classmethod
    def perform(cls, domain: str, event: APIGatewayProxyEvent):
        script_nonce = create_nonce()

        try:
            links = DelibirdLinkTableModel.scan_domain(domain)
            html_content = cls._get_links_html(domain, links, script_nonce=script_nonce)
            if html_content is None:
                raise RuntimeError("Failed to generate HTML content.")
        except Exception:
            logger.exception(f"Failed to scan delibird link data for domain: {domain}")
            return error_response(HTTPStatus.INTERNAL_SERVER_ERROR)

        # HTMLレスポンスを返す
        return success_response(HTTPStatus.OK, html_content,
                                content_type='text/html;charset=utf-8', use_css=True, use_bootstrap=True, use_self_api=True,
                                script_nonce=script_nonce)
