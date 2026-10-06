from jose import jwt,JWTError,ExpiredSignatureError
from passlib.context import CryptContext
from core.config import settings
from datetime import datetime,timedelta
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.connection import get_db
from models.user import USER
from fastapi import HTTPException, Depends, statu


pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain,hashed):
    return pwd_context.verify(plain,hashed)

def create_token(data:dict):

    ## access token 
    to_encode=data.copy()
    expire=datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp":expire,"type":"access"})
    access_token=jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

    ## refresh token
    refresh_token_encode=data.copy()
    refresh_expire=datetime.utcnow()+timedelta(days=1)
    refresh_token_encode.update({"exp":refresh_expire,"type":"refresh"})
    refresh_token=jwt.encode(refresh_token_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }



def verify_token(token:str,expected_type:str):
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired"
        )
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")


    if payload.get("type")!=expected_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Invalid token type. Expected {expected_type} token.",
            )
        return payload

        
security=HTTPBearer()

def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(security),db:Session=Depends(get_db)):
    token=credentials.credentials
    payload=verify_token(token,"access")
    email=payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Invaid token"
        )

    user =db.query(USER).filter(USER.email==email).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user