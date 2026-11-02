import os
import secrets
import string

import bcrypt

from lib.log_conf import logger

PEPPER = os.getenv("PEPPER")
ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))


def verify_password(plain_password, hashed_password) -> bool:
    pw = (plain_password + PEPPER).encode("utf-8")
    try:
        return bcrypt.checkpw(pw, hashed_password.encode("utf-8"))
    except (ValueError, TypeError) as e:
        logger.error(f"パスワードの検証に失敗しました{e!s}")
        return False


def get_password_hash(password) -> str:
    pw = (password + PEPPER).encode("utf-8")
    hashed = bcrypt.hashpw(pw, bcrypt.gensalt(rounds=ROUNDS))
    return hashed.decode("utf-8")


def generate_random_password(length: int = 16) -> str:
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(characters) for _ in range(length))
