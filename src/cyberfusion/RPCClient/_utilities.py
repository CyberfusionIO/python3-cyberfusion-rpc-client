"""Utilities."""

import pika
import ssl
from cyberfusion.RPCClient import RabbitMQCredentials


def create_connection_from_credentials(
    credentials: RabbitMQCredentials,
) -> pika.BlockingConnection:
    """Create RabbitMQ connection from credentials object."""
    ssl_options = None

    if credentials.ssl_enabled:
        ssl_options = pika.SSLOptions(ssl.create_default_context(), credentials.host)

    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=credentials.host,
            port=credentials.port,
            virtual_host=credentials.virtual_host_name,
            credentials=pika.credentials.PlainCredentials(
                credentials.username, credentials.password
            ),
            ssl_options=ssl_options,
        )
    )
