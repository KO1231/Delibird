from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import event_source, APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from portal_page.link_create import PortalLinkCreatePage
from portal_page.link_list import PortalListPage
from portal_page.link_update import PortalLinkUpdatePage
from util.logger_util import setup_logger, setup_dev_logger
from util.parse_util import parse_domain, parse_request_path
from util.response_util import error_response

logger = setup_logger("admin_portal")
setup_dev_logger()


@event_source(data_class=APIGatewayProxyEvent)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    try:
        # parse domain
        domain: str = parse_domain(event.headers.get("Host", ""))
        # parse path
        request_path: str = parse_request_path(event.path_parameters.get("path", ""))
    except ValueError as e:
        logger.info(f"Get Invalid request: {e}")
        return error_response(HTTPStatus.BAD_REQUEST)
    except Exception:
        logger.exception(f"Failed to parse request.")
        return error_response(HTTPStatus.BAD_REQUEST)

    if request_path:
        logger.info(f"Get Invalid request path: {request_path}")
        return error_response(HTTPStatus.NOT_FOUND)

    match event.http_method:
        case "GET":
            return PortalListPage.perform(domain, event)
        case "POST":
            return PortalLinkCreatePage.perform(domain, event)
        case "PUT":
            return PortalLinkUpdatePage.perform(domain, event)
        case _:
            logger.info(f"Get Invalid HTTP method request: {event.http_method}, domain: {domain}")
            return error_response(HTTPStatus.METHOD_NOT_ALLOWED)
