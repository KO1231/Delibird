from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext

from ddb.models.delibird_link import DelibirdLinkTableModel, DelibirdLinkInactiveStatus
from parser import parse_request_path, parse_origin, parse_domain
from query import queried_origin
from util.logger_util import setup_logger
from util.response_util import redirect_response, error_response

logger = setup_logger("redirect_request")


@event_source(data_class=APIGatewayProxyEvent)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    try:
        # parse domain
        domain: str = parse_domain(event.headers.get("Host", ""))
        # parse path
        request_path: str = parse_request_path(event.path_parameters.get("path", ""))
    except ValueError as e:
        logger.info(f"Get Invalid request: {e}")
        return error_response(HTTPStatus.NOT_FOUND)
    except Exception:
        logger.exception(f"Failed to parse request.")
        return error_response(HTTPStatus.NOT_FOUND)
    logger.info(f"Parsed Domain: {domain}, Parsed Request Path: {request_path}")

    # pathがない場合 "/"にアクセスされた場合は、NOT_FOUNDを返す
    if not request_path:
        logger.info("Empty request path.")
        return error_response(HTTPStatus.NOT_FOUND)

    # pathからリンク情報を取得
    link = DelibirdLinkTableModel.get_from_request(domain, request_path)
    interrupt_origin = None

    ## リンクが存在しない場合
    if link is None:
        logger.info(f"Link(domain: {domain}, slug: {request_path}) does not exist or has been disabled.")
        return error_response(HTTPStatus.NOT_FOUND)

    ## リンクが無効な場合
    active, inactive_reason = link.check_active()
    if not active:
        inactive_status = inactive_reason.status
        if inactive_status is DelibirdLinkInactiveStatus.DISABLED:
            # 明示的に無効化されている場合
            logger.info(f"Link(domain: {domain}, slug: {request_path}) is inactive. Reason: {inactive_reason}")
            return error_response(HTTPStatus.NOT_FOUND)

        elif inactive_status is DelibirdLinkInactiveStatus.EXPIRED:
            # 有効期限切れの場合
            if not link.expired_origin:
                logger.info(f"Link(domain: {domain}, slug: {request_path}) is expired at {link.expiration_date}.")
                return error_response(HTTPStatus.NOT_FOUND)
            # リンク期限切れでexpired_originがあれば、そちらにリダイレクトする
            interrupt_origin = link.expired_origin

        elif inactive_status is DelibirdLinkInactiveStatus.MAX_USES_EXCEEDED:
            # 最大使用回数超過の場合
            logger.info(f"Link(domain: {domain}, slug: {request_path}) has reached max uses: {link.uses} / {link.max_uses}.")
            return error_response(HTTPStatus.NOT_FOUND)

        else:
            logger.error(f"Link(domain: {domain}, slug: {request_path}) is not active. Unknown reason: {inactive_reason}")
            return error_response(HTTPStatus.INTERNAL_SERVER_ERROR)
    logger.info(f"Link(domain: {domain}, slug: {request_path}) is active. Current uses: {link.uses} / Max uses: {link.max_uses or "unlimited"}")

    # ステータスコードがリダイレクト系でない場合はInternal Server Errorを返す
    if not link.status.is_redirection:
        logger.error(f"Link(domain: {domain}, slug: {request_path}) has invalid status code: {link.status}")
        return error_response(HTTPStatus.INTERNAL_SERVER_ERROR)

    # リダイレクト先URLの決定
    origin_candidate = interrupt_origin or link.link_origin
    try:
        # リンク先URLの妥当性確認
        origin = parse_origin(origin_candidate)
    except Exception:
        # 不正なURLがデータベースに保存されている場合はInternal Server Errorを返す
        logger.exception(f"Invalid URL stored in link_origin for domain: {domain}, slug: {request_path}, URL: {origin_candidate}")
        return error_response(HTTPStatus.INTERNAL_SERVER_ERROR)

    # クエリパラメータの付与
    if not link.query_omit:
        logger.info(f"Link(domain: {domain}, slug: {request_path}) has disabled query omission. Appending query parameters.")
        try:
            origin = queried_origin(origin, event.resolved_query_string_parameters, link.query_whitelist)
        except Exception:
            logger.exception(f"Failed to append query parameters for domain: {domain}, slug: {request_path}, URL: {origin}")
            return error_response(HTTPStatus.INTERNAL_SERVER_ERROR)

    # リンクの使用回数をインクリメント
    try:
        link.increment_uses()
    except Exception:
        logger.exception(f"Failed to increment uses for domain: {domain}, slug: {request_path}")
        return error_response(HTTPStatus.INTERNAL_SERVER_ERROR)

    logger.info(f"Redirect to {origin} for domain: {domain}, slug: {request_path} (status: {link.status})")
    return redirect_response(origin, link.status)
