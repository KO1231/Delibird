from abc import ABC, abstractmethod

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent


class AdminPortalPage(ABC):
    @abstractmethod
    def perform(self, domain: str, event: APIGatewayProxyEvent):
        pass
