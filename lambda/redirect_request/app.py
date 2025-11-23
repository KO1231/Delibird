from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext
from ddb.models.delibird_link import DelibirdLinkTableModel
from util.logger_util import setup_logger
from util.response_util import redirect_response, error_response

from parser import parse_request_path, parse_origin

logger = setup_logger("redirect_request")


@event_source(data_class=APIGatewayProxyEvent)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    # parse path
    request_path: str = parse_request_path(event.path_parameters.get("path", ""))

    # pathがない場合 "/"にアクセスされた場合は、NOT_FOUNDを返す
    if not request_path:
        logger.info("Empty request path.")
        return error_response(HTTPStatus.NOT_FOUND)

    # pathからリンク情報を取得
    link = DelibirdLinkTableModel.get_by_slug(request_path)
    if not link:
        # リンクが存在しない、または無効化されている場合
        logger.info(f"Link not found or disabled for slug: {request_path}")
        return error_response(HTTPStatus.NOT_FOUND)

    # ステータスコードがリダイレクト系でない場合はInternal Server Errorを返す
    if not link.status.is_redirection:
        logger.error(f"Link(slug: {request_path}) has invalid status code: {link.status}")
        return error_response(HTTPStatus.INTERNAL_SERVER_ERROR)

    try:
        # リンク先URLの妥当性確認
        origin = parse_origin(link.link_origin)
    except Exception as e:
        # 不正なURLがデータベースに保存されている場合はInternal Server Errorを返す
        logger.exception(f"Invalid URL stored in link_origin for slug: {request_path}, URL: {link.link_origin}")
        return error_response(HTTPStatus.INTERNAL_SERVER_ERROR)

    logger.info(f"Redirect to {origin} for slug: {request_path} (status: {link.status})")
    return redirect_response(origin, link.status)
