"""Internal RPC tooling."""

import time
import uuid
from functools import cached_property
from typing import Any, NoReturn

from cyberfusion.RPCClient import RabbitMQCredentials
from cyberfusion.RPCClient.enums import ExchangeType
import pika

from cyberfusion.RPCClient._utilities import create_connection_from_credentials


class RPC:
    """Internal RPC class."""

    def __init__(
        self,
        credentials: RabbitMQCredentials,
        *,
        routing_key: str,
        exchange_name: str,
        timeout: int,
    ) -> None:
        """Set attributes."""
        self.credentials = credentials
        self.routing_key = routing_key
        self.exchange_name = exchange_name
        self.timeout = timeout

        self.response = None

        self.connection = create_connection_from_credentials(self.credentials)

        self.channel = self.connection.channel()

        self.callback_queue = self.channel.queue_declare(
            queue="", exclusive=True
        ).method.queue

        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type=ExchangeType.DIRECT,
        )

        self.channel.queue_bind(exchange=self.exchange_name, queue=self.callback_queue)

        self.connection.call_later(timeout, self.handle_timeout)

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.handle_response,
            auto_ack=True,
        )

    def handle_timeout(self) -> NoReturn:
        """Handle timeout (no response in time)."""
        self.connection.close()

        raise TimeoutError

    @cached_property
    def correlation_id(self) -> str:
        """Get randomly generated correlation ID."""
        return str(uuid.uuid4())

    def publish(self, body: Any, *, content_type: str) -> Any:
        """Publish RPC request."""
        self.channel.basic_publish(
            exchange=self.exchange_name,
            body=body,
            properties=pika.BasicProperties(
                content_type=content_type,
                reply_to=self.callback_queue,
                correlation_id=self.correlation_id,
                #
                # $TIMEOUT can be reached in two cases:
                #
                # - When the message isn't acked in $TIMEOUT, e.g. because the
                #   consumer is offline
                # - When the message processing takes $TIMEOUT
                #
                # In either case, an exception is raised in the 'timeout' method.
                # When this happens because of case #1 (message not acked), we want
                # to ensure that the RPC message does not start processing when the
                # consumer is able to process the message. Therefore, the RPC message
                # should expire after $TIMEOUT; this ensures that, once we've returned
                # the definitive state by raising an exception in the `handle_timeout`
                # method, the RPC call will not process in the background unexpectedly.
                #
                expiration=str(self.timeout * 1000),
            ),
            routing_key=self.routing_key,
        )

        while self.response is None:
            self.connection.process_data_events()

            time.sleep(0.5)

        self.connection.close()  # type: ignore[unreachable]

        return self.response

    def handle_response(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: Any,
    ) -> None:
        """Handle response."""
        if self.correlation_id != properties.correlation_id:
            return

        self.response = body
