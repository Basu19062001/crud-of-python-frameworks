from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status
from jose import jwt, JWTError

from config import JWT

class PasswordHashing:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hashing_password(cls, password: str)->str:
        try:
            hashed_password = cls.pwd_context.hash(password)
            return hashed_password
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password hashing failed: {str(e)}"
            )
        
    @classmethod
    def verify_password(cls, password: str, hashed_password:str )->bool:
        try:
            return cls.pwd_context.verify(password, hashed_password)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Password verification failed: {str(e)}"
            )

class Token:
    JWT_SECRET_KEY = JWT.JWT_SECRET_KEY
    ALGORITHM=JWT.ALGORITHM
    @classmethod
    def generate_token(cls, user_data: dict)->str:
        try:
            expire = datetime.now(timezone.utc) + timedelta(minutes=30)
            payload = {
                "sub":str(user_data.get("_id")),
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "iat":datetime.now(timezone.utc),
                "exp":expire,
                "type":"access"
            }
            return jwt.encode(payload,cls.JWT_SECRET_KEY,algorithm=cls.ALGORITHM)
        except JWTError as je:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token generation failed: {str(je)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )
        

    @classmethod
    def decode_token(cls, token: str):
        try:
            payload = jwt.decode(token, cls.JWT_SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token."
            )