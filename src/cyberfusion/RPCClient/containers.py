"""Container classes."""

from dataclasses import dataclass


@dataclass
class RabbitMQCredentials:
    """Class holding RabbitMQ credentials."""

    ssl_enabled: bool
    port: int
    host: str
    username: str
    password: str
    virtual_host_name: str
