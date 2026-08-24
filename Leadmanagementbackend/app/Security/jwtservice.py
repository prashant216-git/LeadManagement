from jose import JWTError, jwt

from app.core.config import settings


class JWTService:

    def decode_token(
        self,
        token: str,
    ) -> dict:

        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[
                    settings.JWT_ALGORITHM
                ],
            )

        except JWTError:
            raise ValueError(
                "Invalid or expired token."
            )