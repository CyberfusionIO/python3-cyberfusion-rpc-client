import os
import requests
import xprocess
from typing import Generator
import sys
import pytest

from cyberfusion.RPCClient import RabbitMQCredentials
from _pytest.config.argparsing import Parser
from xprocess import ProcessStarter


def pytest_addoption(parser: Parser) -> None:
    parser.addoption("--rabbitmq-ssl", action="store_true", default=False)
    parser.addoption("--rabbitmq-host", action="store", default="localhost")
    parser.addoption("--rabbitmq-port", action="store", type=int, default=9195)
    parser.addoption(
        "--rabbitmq-management-port", action="store", type=int, default=16148
    )
    parser.addoption("--rabbitmq-username", action="store", default="guest")
    parser.addoption("--rabbitmq-password", action="store", default="guest")
    parser.addoption("--rabbitmq-virtual-host-name", action="store", default="/")


@pytest.fixture(scope="session")
def rabbitmq_ssl(request: pytest.FixtureRequest) -> bool:
    return request.config.getoption("--rabbitmq-ssl")


@pytest.fixture(scope="session")
def rabbitmq_host(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--rabbitmq-host")


@pytest.fixture(scope="session")
def rabbitmq_port(request: pytest.FixtureRequest) -> int:
    return request.config.getoption("--rabbitmq-port")


@pytest.fixture(scope="session")
def rabbitmq_username(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--rabbitmq-username")


@pytest.fixture(scope="session")
def rabbitmq_password(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--rabbitmq-password")


@pytest.fixture(scope="session")
def rabbitmq_virtual_host_name(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--rabbitmq-virtual-host-name")


@pytest.fixture(scope="session")
def rabbitmq_management_port(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--rabbitmq-management-port")


@pytest.fixture(scope="session")
def rabbitmq_credentials(
    rabbitmq_ssl: bool,
    rabbitmq_host: str,
    rabbitmq_port: int,
    rabbitmq_username: str,
    rabbitmq_password: str,
    rabbitmq_virtual_host_name: str,
) -> RabbitMQCredentials:
    return RabbitMQCredentials(
        ssl_enabled=rabbitmq_ssl,
        host=rabbitmq_host,
        port=rabbitmq_port,
        username=rabbitmq_username,
        password=rabbitmq_password,
        virtual_host_name=rabbitmq_virtual_host_name,
    )


@pytest.fixture(scope="session")
def exchange_name() -> str:
    return "example"


@pytest.fixture(scope="session")
def queue_name() -> str:
    return "example"


@pytest.fixture
def rabbitmq_consumer(
    xprocess: xprocess.xprocess.XProcess,
    rabbitmq_credentials: RabbitMQCredentials,
    queue_name: str,
    exchange_name: str,
) -> None:
    NAME_PROCESS = "rabbitmq_consumer"

    def get_command() -> list[str]:
        current_python_binary_path = sys.executable
        script_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)))

        command = [
            current_python_binary_path,
            "-u",  # See https://pytest-xprocess.readthedocs.io/en/latest/starter/#an-important-note-regarding-stream-buffering
            os.path.join(script_directory, "consumer.py"),
            "--rabbitmq-host",
            rabbitmq_credentials.host,
            "--rabbitmq-port",
            rabbitmq_credentials.port,
            "--rabbitmq-username",
            rabbitmq_credentials.username,
            "--rabbitmq-password",
            rabbitmq_credentials.password,
            "--rabbitmq-virtual-host-name",
            rabbitmq_credentials.virtual_host_name,
            "--rabbitmq-queue-name",
            queue_name,
            "--rabbitmq-exchange-name",
            exchange_name,
        ]

        if rabbitmq_credentials.ssl_enabled:
            command.append("--rabbitmq-ssl")

        return command

    class Starter(ProcessStarter):
        pattern = "^Starting consuming$"
        timeout = 10
        args = get_command()

    xprocess.ensure(NAME_PROCESS, Starter)

    yield

    xprocess.getinfo(NAME_PROCESS).terminate()


@pytest.fixture(autouse=True)
def delete_rabbitmq_objects(
    rabbitmq_credentials: RabbitMQCredentials, rabbitmq_management_port: str
) -> Generator[None, None, None]:
    """Delete RabbitMQ objects."""
    yield

    http_auth = (rabbitmq_credentials.username, rabbitmq_credentials.password)

    if rabbitmq_credentials.ssl_enabled:
        url = "https://"
    else:
        url = "http://"

    url += rabbitmq_credentials.host + ":" + str(rabbitmq_management_port)

    users_request = requests.get(url + "/api/users", auth=http_auth)
    users_request.raise_for_status()

    vhosts_request = requests.get(url + "/api/vhosts", auth=http_auth)
    vhosts_request.raise_for_status()

    users = users_request.json()
    vhosts = vhosts_request.json()

    for user in users:
        if user["name"] == rabbitmq_credentials.username:
            continue

        requests.delete(
            url + "/api/users/" + user["name"], auth=http_auth
        ).raise_for_status()

    for vhost in vhosts:
        if vhost["name"] == "/":
            continue

        requests.delete(
            url + "/api/vhosts/" + vhost["name"], auth=http_auth
        ).raise_for_status()
