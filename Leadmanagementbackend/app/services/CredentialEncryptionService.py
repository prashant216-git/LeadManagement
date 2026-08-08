import json
from typing import Any


class CredentialEncryptionService:
    """
    Handles encryption and decryption of provider credentials.

    NOTE:
    Encryption implementation will be added later.
    """

    def encrypt(
        self,
        payload: dict[str, Any],
    ) -> bytes:

        return json.dumps(payload).encode()

    def decrypt(
        self,
        payload: bytes,
    ) -> dict[str, Any]:

        return json.loads(payload.decode())