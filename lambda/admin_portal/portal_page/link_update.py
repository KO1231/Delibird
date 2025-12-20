import json
from datetime import datetime
from http import HTTPStatus
from typing import Optional

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

from ddb.models.delibird_link import DelibirdLinkTableModel, DelibirdLink
from portal_page.page import AdminPortalPage
from util.date_util import as_jst
from util.logger_util import setup_logger
from util.response_util import error_response, success_response

logger = setup_logger("admin_portal.link_update_page")


class PortalLinkUpdatePage(AdminPortalPage):
    @classmethod
    def _parse_request_data(cls, domain: str, _body: str) -> Optional[DelibirdLink]:
        try:
            body = json.loads(_body)
        except json.decoder.JSONDecodeError as e:
            logger.info(f"Invalid JSON body: {_body}", exc_info=e)
            return None

        try:
            link = DelibirdLink(
                _model=None,
                domain=domain,
                link_slug=str(body["link_slug"]),
                link_origin=str(body["link_origin"]),
                status=HTTPStatus(int(body["status"])),
                disabled=bool(body["disabled"]),

                memo=str(body["memo"]) if "memo" in body else "",
                tag=set(body["tag"]) if "tag" in body else None,
                expiration_date=as_jst(datetime.fromisoformat(str(body["expiration_date"]))) if "expiration_date" in body else None,
                expired_origin=str(body["expired_origin"]) if "expired_origin" in body else None,
                _passphrase=str(body["passphrase"]) if "passphrase" in body else None,
                query_omit=bool(body["query_omit"]),
                query_whitelist=set(body["query_whitelist"]) if "query_whitelist" in body else None,
                max_uses=int(body["max_uses"]) if "max_uses" in body else None,
            )
            if not link.status.is_redirection:
                raise ValueError("status is not redirection: {link.status}")
            if link.query_omit and link.query_whitelist:
                raise ValueError("both query_omit and query_whitelist are set.")
            if link.expiration_date and link.expiration_date.tzinfo is None:
                raise ValueError("expiration_date is not timezone-aware.")
        except Exception as e:
            logger.info(f"Failed to parse DelibirdLink from body, error: {e}")
            return None

        return link

    @classmethod
    def perform(cls, domain: str, event: APIGatewayProxyEvent):
        link_data = cls._parse_request_data(domain, event.body)
        if link_data is None:
            logger.info(f"Get Invalid link create request data for domain: {domain}")
            return error_response(HTTPStatus.BAD_REQUEST, force_json=True)

        try:
            model = DelibirdLinkTableModel.get(domain, link_data.link_slug)
        except DelibirdLinkTableModel.DoesNotExist:
            logger.info(f"Link not found for domain: {domain}, slug: {link_data.link_slug}")
            return error_response(HTTPStatus.NOT_FOUND, force_json=True)
        except Exception as e:
            logger.exception(f"Failed to check existing link for domain: {domain}, slug: {link_data.link_slug}")
            return error_response(HTTPStatus.INTERNAL_SERVER_ERROR)

        try:
            model.update(actions=[
                DelibirdLinkTableModel.origin.set(link_data.link_origin),
                DelibirdLinkTableModel.status.set(int(link_data.status)),
                DelibirdLinkTableModel.disabled.set(link_data.disabled),
                DelibirdLinkTableModel.memo.set(link_data.memo),
                DelibirdLinkTableModel.tag.set(link_data.tag),
                DelibirdLinkTableModel.expiration_date.set(link_data.expiration_date),
                DelibirdLinkTableModel.expired_origin.set(link_data.expired_origin),
                DelibirdLinkTableModel.passphrase.set(link_data._passphrase),  # allow read private field
                DelibirdLinkTableModel.query_omit.set(link_data.query_omit),
                DelibirdLinkTableModel.query_whitelist.set(link_data.query_whitelist),
                DelibirdLinkTableModel.max_uses.set(link_data.max_uses),
            ])
        except Exception:
            logger.exception(f"Failed to create DelibirdLinkTableModel for domain: {domain}, slug: {link_data.link_slug}")
            return error_response(HTTPStatus.INTERNAL_SERVER_ERROR)

        return success_response(HTTPStatus.OK, {"status": "updated"})
