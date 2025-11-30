from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import event_source, APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from portal_page.link_list import PortalListPage
from util.logger_util import setup_logger
from util.parse_util import parse_domain
from util.response_util import error_response

logger = setup_logger("admin_portal")


@event_source(data_class=APIGatewayProxyEvent)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    try:
        # parse domain
        domain: str = parse_domain(event.headers.get("Host", ""))
    except ValueError as e:
        logger.info(f"Get Invalid request: {e}")
        return error_response(HTTPStatus.BAD_REQUEST)
    except Exception:
        logger.exception(f"Failed to parse request.")
        return error_response(HTTPStatus.BAD_REQUEST)

    match event.http_method:
        case "GET":
            return PortalListPage.perform(domain, event)
        case _:
            logger.info(f"Get Invalid HTTP method request: {event.http_method}, domain: {domain}")
            return error_response(HTTPStatus.METHOD_NOT_ALLOWED)
