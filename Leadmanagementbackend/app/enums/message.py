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

class AIDraftStatus(str, Enum):
    GENERATED = "GENERATED"
    EDITED = "EDITED"
    SENT = "SENT"
    DISCARDED = "DISCARDED"


class ScheduledMessageStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"