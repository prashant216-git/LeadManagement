from pydantic import BaseModel


class CallbackError(BaseModel):
    message: str | None = None
    error: str | None = None
    state: str | None = None


class CallbackException(Exception):
    def __init__(self, error: CallbackError):
        self.error = error
        super().__init__(error.message)
