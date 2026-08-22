from enum import Enum


class MessageDirection(str, Enum):

    INBOUND = "INBOUND"

    OUTBOUND = "OUTBOUND"


class MessageType(str, Enum):

    TEXT = "TEXT"

    IMAGE = "IMAGE"

    VIDEO = "VIDEO"

    DOCUMENT = "DOCUMENT"

    AUDIO = "AUDIO"