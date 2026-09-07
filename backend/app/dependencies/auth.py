import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from app.services.auth.token_verifier import TokenVerifier

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def get_token_verifier(db: Session = Depends(get_db)) -> TokenVerifier:
    return TokenVerifier(db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    verifier: TokenVerifier = Depends(get_token_verifier),
):
    return verifier.get_current_user_from_token(token)
