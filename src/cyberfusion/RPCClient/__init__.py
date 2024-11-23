"""Program."""

import json
from typing import Any


from cyberfusion.RPCClient.containers import RabbitMQCredentials


from cyberfusion.RPCClient._rpc import RPC
from cyberfusion.RPCClient.enums import ContentType


class RPCClient:
    """Developer-friendly RPC client."""

    def __init__(
        self,
        credentials: RabbitMQCredentials,
        *,
        queue_name: str,
        exchange_name: str,
        timeout: int = 5 * 60,
    ) -> None:
        """Set attributes."""
        self.credentials = credentials

        self.queue_name = queue_name
        self.exchange_name = exchange_name

        self.rpc = RPC(
            self.credentials,
            routing_key=queue_name,
            exchange_name=exchange_name,
            timeout=timeout,
        )

    def request(
        self, body: Any, *, content_type: ContentType = ContentType.JSON
    ) -> Any:
        """Publish RPC request.

        If `content_type` is set to `application/json`, `body` will be converted
        to JSON automatically if needed.
        """
        if content_type == ContentType.JSON and not isinstance(body, str):
            body = json.dumps(body)

        return self.rpc.publish(body, content_type=content_type)
