"""Enums."""

from enum import Enum


class ExchangeType(str, Enum):
    """Exchange types."""

    DIRECT = "direct"
    FANOUT = "fanout"
    HEADERS = "headers"
    TOPIC = "topic"


class ContentType(str, Enum):
    """Common content types."""

    JSON = "application/json"
