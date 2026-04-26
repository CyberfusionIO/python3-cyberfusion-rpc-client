import json

import pytest
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import UnroutableError
from pytest_mock import MockerFixture

from cyberfusion.RPCClient import RabbitMQCredentials, RPCClient
from cyberfusion.RPCClient.enums import ContentType
from cyberfusion.RPCClient.exceptions import MessageUnroutable


def test_rpc_client(
    exchange_name: str,
    queue_name: str,
    rabbitmq_credentials: RabbitMQCredentials,
    rabbitmq_consumer: None,
) -> None:
    body = json.dumps(["example"])
    content_type = ContentType.JSON

    result = RPCClient(
        rabbitmq_credentials, exchange_name=exchange_name, queue_name=queue_name
    ).request(body, content_type=content_type)

    assert result == b"This is a response!"


def test_rpc_client_message_unroutable(
    exchange_name: str,
    queue_name: str,
    rabbitmq_credentials: RabbitMQCredentials,
    rabbitmq_consumer: None,
    mocker: MockerFixture,
) -> None:
    body = json.dumps(["example"])
    content_type = ContentType.JSON

    mocker.patch.object(BlockingChannel, "basic_publish", side_effect=UnroutableError([]))

    with pytest.raises(MessageUnroutable):
        RPCClient(
            rabbitmq_credentials, exchange_name=exchange_name, queue_name=queue_name,
        ).request(body, content_type=content_type, mandatory=True)


def test_rpc_client_timeout(
    exchange_name: str,
    queue_name: str,
    rabbitmq_credentials: RabbitMQCredentials,
) -> None:
    body = json.dumps(["example"])
    content_type = ContentType.JSON

    with pytest.raises(TimeoutError):
        RPCClient(
            rabbitmq_credentials,
            exchange_name=exchange_name,
            queue_name=queue_name,
            timeout=1,
        ).request(body, content_type=content_type)
