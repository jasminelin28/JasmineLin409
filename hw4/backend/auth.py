"""password hashing and json web token helpers."""
import datetime as dt
import hashlib
import hmac
import secrets

import jwt

import config

_ALGO_TAG = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    """return a `pbkdf2_sha256$salt$hash` string matching the seeded users' format."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), config.pbkdf2_iterations
    ).hex()
    return f"{_ALGO_TAG}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    """check a password against a stored `pbkdf2_sha256$salt$hash` value.

    the stored format does not embed the iteration count, so we accept any of the
    supported presets in `config.pbkdf2_accept_iterations` (like a real password
    hasher that supports several cost settings). new accounts are always written
    with the primary `config.pbkdf2_iterations`.
    """
    try:
        algo, salt, digest = stored.split("$")
    except ValueError:
        return False
    if algo != _ALGO_TAG:
        return False
    for iterations in config.pbkdf2_accept_iterations:
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), iterations
        ).hex()
        if hmac.compare_digest(candidate, digest):
            return True
    return False


def create_token(user_id: int, email: str) -> str:
    """mint a signed jwt for a logged-in shopper."""
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": now,
        "exp": now + dt.timedelta(hours=config.jwt_ttl_hours),
    }
    return jwt.encode(payload, config.jwt_secret, algorithm=config.jwt_algorithm)


def decode_token(token: str) -> dict:
    """decode and validate a jwt, raising jwt errors on failure."""
    return jwt.decode(token, config.jwt_secret, algorithms=[config.jwt_algorithm])
