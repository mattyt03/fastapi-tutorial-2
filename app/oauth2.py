from jose import JWTError, jwt
from pydantic import ValidationError
from datetime import datetime, timedelta
from . import models, schemas
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .database import get_db
from sqlalchemy.orm import Session
from .config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def create_access_token(payload: dict):
    to_encode = payload.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({'exp': expire})
    access_token = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm)
    return access_token


def verify_access_token(token: str):
    try:
        # decode returns the payload as a dictionary
        payload = jwt.decode(token, settings.secret_key,
                             algorithms=[settings.algorithm])
        # we should still validate with a pydantic model
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        # what is the WWW-Authenticate header for?
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid Credentials',
                            headers={"WWW-Authenticate": "Bearer"})
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_access_token(token)
    user = db.query(models.User).filter(
        models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id {id} does not exist')
    return user
