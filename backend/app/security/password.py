import os
import bcrypt
from lib.log_conf import logger

PEPPER = os.getenv("PEPPER")
ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))


def verify_password(plain_password, hashed_password) -> bool:
    pw = (plain_password + PEPPER).encode("utf-8")
    try:
        return bcrypt.checkpw(pw, hashed_password.encode("utf-8"))
    except (ValueError, TypeError) as e:
        logger.error(f"パスワードの検証に失敗しました{str(e)}")
        return False


def get_password_hash(password) -> str:
    pw = (password + PEPPER).encode("utf-8")
    hashed = bcrypt.hashpw(pw, bcrypt.gensalt(rounds=ROUNDS))
    return hashed.decode("utf-8")
