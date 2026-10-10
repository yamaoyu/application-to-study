import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from app.services.auth.token_verifier import TokenVerifier
from app.error_codes import NotAuthorizedCode
from app.exceptions import Forbidden, NotAuthorized
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login",
    auto_error=False,
)


def get_access_token(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> str:
    """
        OAuth2PasswordBearerでは{ "Authorization": "Bearer xxx" }の形式でないと
        ライブラリが例外を上げるため、トークンが返ってこない
        その場合でもエラー形式を統一させる役目
    """
    if token is None:
        raise NotAuthorized(
            code=NotAuthorizedCode.NOT_AUTHORIZED,
        )
    return token


def get_token_verifier(db: Session = Depends(get_db)) -> TokenVerifier:
    return TokenVerifier(db)


def get_current_user(
    token: str = Depends(get_access_token),
    verifier: TokenVerifier = Depends(get_token_verifier),
):
    user_info = verifier.get_current_user_from_token(token)
    return user_info


def get_current_active_user(
    token: str = Depends(get_access_token),
    verifier: TokenVerifier = Depends(get_token_verifier),
):
    user_info = verifier.get_current_user_from_token(token)
    if user_info["status"] != "active":
        raise Forbidden(code=NotAuthorizedCode.USER_SUSPENDED)
    return user_info


def authenticated_user(
    token: str = Depends(get_access_token),
    verifier: TokenVerifier = Depends(get_token_verifier)
):
    return verifier.authenticate_user(token)
