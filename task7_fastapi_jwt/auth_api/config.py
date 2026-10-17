import os
from datetime import timedelta
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ALGORITHM = "RS256"
ACCESS_TOKEN_TTL = timedelta(minutes=int(os.getenv("JWT_ACCESS_TTL_MINUTES", "15")))
REFRESH_TOKEN_TTL = timedelta(days=int(os.getenv("JWT_REFRESH_TTL_DAYS", "7")))


def _load_private_key() -> rsa.RSAPrivateKey:
    path = os.getenv("JWT_PRIVATE_KEY_FILE")
    if path is None:
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key = serialization.load_pem_private_key(Path(path).read_bytes(), password=None)
    if not isinstance(key, rsa.RSAPrivateKey):
        raise RuntimeError("JWT_PRIVATE_KEY_FILE должен содержать RSA-ключ")
    return key


PRIVATE_KEY = _load_private_key()
PUBLIC_KEY = PRIVATE_KEY.public_key()
