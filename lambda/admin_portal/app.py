from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import event_source, APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from util.response_util import success_response


@event_source(data_class=APIGatewayProxyEvent)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    return success_response(HTTPStatus.OK, {"result": "success"})
