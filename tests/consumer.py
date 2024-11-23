import argparse
from typing import Any

import pika

from cyberfusion.RPCClient import RabbitMQCredentials
from cyberfusion.RPCClient._utilities import create_connection_from_credentials
from cyberfusion.RPCClient.enums import ExchangeType


def handle_request(
    channel: pika.adapters.blocking_connection.BlockingChannel,
    method: pika.spec.Basic.Deliver,
    properties: pika.spec.BasicProperties,
    body: Any,
) -> None:
    print("Received message")

    channel.basic_publish(
        exchange=method.exchange,
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id,
        ),
        body="This is a response!",
    )
    channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--rabbitmq-ssl",
        action="store_true",
    )
    parser.add_argument("--rabbitmq-host", action="store", required=True)
    parser.add_argument("--rabbitmq-port", action="store", required=True)
    parser.add_argument("--rabbitmq-username", action="store", required=True)
    parser.add_argument("--rabbitmq-password", action="store", required=True)
    parser.add_argument("--rabbitmq-virtual-host-name", action="store", required=True)
    parser.add_argument("--rabbitmq-exchange-name", action="store", required=True)
    parser.add_argument("--rabbitmq-queue-name", action="store", required=True)

    args = parser.parse_args()

    credentials = RabbitMQCredentials(
        ssl_enabled=args.rabbitmq_ssl,
        host=args.rabbitmq_host,
        port=args.rabbitmq_port,
        username=args.rabbitmq_username,
        password=args.rabbitmq_password,
        virtual_host_name=args.rabbitmq_virtual_host_name,
    )

    print("Setting conection")

    connection = create_connection_from_credentials(credentials)

    print("Setting channel")

    channel = connection.channel()

    print("Declaring queue")

    channel.queue_declare(
        queue=args.rabbitmq_queue_name,
        durable=True,
    )

    print("Declaring exchange")

    channel.exchange_declare(
        exchange=args.rabbitmq_exchange_name,
        exchange_type=ExchangeType.DIRECT,
    )

    print("Binding to queue")

    channel.queue_bind(
        exchange=args.rabbitmq_exchange_name, queue=args.rabbitmq_queue_name
    )

    print("Setting QOS")

    channel.basic_qos(prefetch_count=1)

    print("Configuring consume")

    channel.basic_consume(
        queue=args.rabbitmq_queue_name, on_message_callback=handle_request
    )

    print("Starting consuming")

    channel.start_consuming()
