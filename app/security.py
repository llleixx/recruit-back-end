from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from sys import stderr
import re

from . import crud
from .dependencies import SessionLocal
from . import models

SECRET_KEY = "28b67870e407fd576bc133670fda5965f6ad1950987c3642650dc28ca7714273" # You should get it by `openssl rand -hex 32`
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
EMAIL_TOKEN_REGEX = re.compile('^\d{6}$')

router= APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(account: str, password: str):
    async with SessionLocal() as db:
        if "@" in account:
            user: models.User = await crud.get_user_by_email(db=db, email=account)
        else:
            user: models.User = await crud.get_user_by_name(db=db, name=account)
    
    if user is None:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if "@" in account and EMAIL_TOKEN_REGEX.match(password):
        async with SessionLocal() as db:
            email_token: models.Confirmation = await crud.get_confirmation(db = db, email=account, option="LOGIN", time_delta=300)
            if email_token and email_token.token == password:
                return user

    if verify_password(password, user.password):
        return user

    return False

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user_base(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = int(payload.get("sub"))
        if id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError as e:
        print(e, file=stderr)
        raise credentials_exception
    async with SessionLocal() as db:
        user = await crud.get_user(db=db, id=id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_strict(token: Annotated[str, Depends(oauth2_scheme)]):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user: models.User = await get_current_user_base(token)

    if user.email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You should bind an email first"
        )
    
    return user

async def get_current_user_loose(token: Annotated[str, Depends(oauth2_scheme)]):
    if token is None:
        return None
    return await get_current_user_base(token)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await get_current_user_base(token)