import json

from pytest_mock import MockerFixture

from cyberfusion.RPCClient import RabbitMQCredentials, RPCClient
from cyberfusion.RPCClient.enums import ContentType


def test_rpc_client_json_converted(
    mocker: MockerFixture,
    exchange_name: str,
    queue_name: str,
    rabbitmq_credentials: RabbitMQCredentials,
) -> None:
    """Test that when a non-JSON body is specified, but content type is set to JSON, body is auto-converted to JSON."""
    publish_spy = mocker.patch(
        "cyberfusion.RPCClient._rpc.RPC.publish", return_value=None
    )

    body = ["example"]
    content_type = ContentType.JSON

    RPCClient(
        rabbitmq_credentials, exchange_name=exchange_name, queue_name=queue_name
    ).request(body, content_type=content_type)

    assert publish_spy.call_args[0][0] == json.dumps(body)
