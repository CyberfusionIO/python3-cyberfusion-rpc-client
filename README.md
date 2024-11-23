# python3-cyberfusion-rpc-client

This library provides a developer-friendly interface to do RPC requests (using [Pika](https://github.com/pika/pika)).

The library can be used on the requesting side of [RabbitMQ consumer](https://github.com/CyberfusionIO/python3-cyberfusion-rabbitmq-consumer).

# Install

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc

## PyPI

Run the following command to install the package from PyPI:

    pip3 install python3-cyberfusion-rpc-client

# Configure

No configuration is supported.

# Usage

## Example

```python
from cyberfusion.RPCClient import RPCClient, ContentType
from cyberfusion.RPCClient.containers import RabbitMQCredentials

credentials = RabbitMQCredentials(
    ssl_enabled=True,
    port=5672,
    host='localhost',
    username='guest',
    password='guest',
    virtual_host_name='/',
)

queue_name = 'example.com'
exchange_name = 'dx_order_fruit'

client = RPCClient(credentials, queue_name=queue_name, exchange_name=exchange_name)
response = client.request(body={'amount': 10000, 'type': 'banana'}, content_type=ContentType.JSON)

print(response)
```
