from enum import Enum


class ChannelStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ConnectionStatus(str, Enum):
    PENDING = "PENDING"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    DISCONNECTED = "DISCONNECTED"
    FAILED = "FAILED"
    SUSPENDED = "SUSPENDED"


class AdminStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    DELETED = "DELETED"


class AuthType(str, Enum):
    OAUTH = "OAUTH"
    API_KEY = "API_KEY"
    INTERNAL = "INTERNAL"


class ChannelCategory(str, Enum):
    MESSAGING = "MESSAGING"
    EMAIL = "EMAIL"
    SOCIAL = "SOCIAL"
    SMS = "SMS"
    VOICE = "VOICE"
    WEBSITE = "WEBSITE"

class CredentialType(str, Enum):
    OAUTH = "OAUTH"
    API_KEY = "API_KEY"
    BOT_TOKEN = "BOT_TOKEN"
    USERNAME_PASSWORD = "USERNAME_PASSWORD"
    JWT = "JWT"
    CERTIFICATE = "CERTIFICATE"
    CUSTOM = "CUSTOM"

class WatchStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    DELETED = "DELETED"
    FAILED = "FAILED"
    SUSPENDED = "SUSPENDED"