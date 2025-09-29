import json
import time
from typing import Any

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from paseto.protocol.version4 import create_symmetric_key, decrypt, encrypt


class PasetoBearer(HTTPBearer):
    def __init__(self, key: bytes, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.key = key
        print(self.key)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme")
            if not self.verify_token(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token")
            return credentials.credentials.encode("utf-8")
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code")

    def verify_token(self, token: str) -> bool:
        is_token_valid: bool = False

        try:
            payload = decode(token=token.encode("utf-8"), key=self.key)
        except:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid


def generate_encription_key() -> bytes:
    return create_symmetric_key()


def token_response(token: bytes) -> dict[str, str]:
    return {
        "access_token": token.decode(),
    }


def sign(user: Any, key: bytes) -> dict[str, str]:
    user_name = user.email.split("@")[0]
    payload = {"user_id": user.id, "user_name": user_name, "expires": time.time() + 86400}
    message = bytes(json.dumps(payload), encoding="utf-8")
    token = encrypt(message, key)

    return token_response(token)


def decode(token: bytes, key: bytes) -> dict[str, Any] | None:
    decoded_token = json.loads(decrypt(token, key))
    return decoded_token if decoded_token["expires"] >= time.time() else None
