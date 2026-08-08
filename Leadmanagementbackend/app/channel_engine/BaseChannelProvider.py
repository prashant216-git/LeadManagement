from abc import ABC, abstractmethod

from app.DTOs.connection.connection_request import ConnectRequest
from app.DTOs.connection.connection_response import ConnectResponse


class BaseChannelProvider(ABC):

    @abstractmethod
    async def connect(self,
        request: ConnectRequest,tenant_id: int
    ) -> ConnectResponse:
        pass

    # @abstractmethod
    # async def disconnect(self):
    #     pass
    #
    # @abstractmethod
    # async def refresh_credentials(self):
    #     pass
    #
    # @abstractmethod
    # async def send_message(self):
    #     pass
    #
    # @abstractmethod
    # async def receive_message(self):
    #     pass
    #
    # @abstractmethod
    # async def sync(self):
    #     pass
    #
    # @abstractmethod
    # async def health_check(self):
    #     pass
    #
    # @abstractmethod
    # async def validate_webhook(self):
    #     pass
    #
    # @abstractmethod
    # async def normalize_webhook(self):
    #     pass