from typing import Optional, Union
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    created_at: Optional[datetime] = datetime.now(timezone.utc)
    updated_at: Optional[datetime] = datetime.now(timezone.utc)
    is_delete: Optional[bool] = False


class UserModel(UserBase):
    password: str  # Hashed
    confirm_password: str


class UserResponseModel(BaseModel):
    message: str
    status: bool
    data: UserBase

class UserLoginModel(BaseModel):
    username_or_email: Union[str, EmailStr]
    password: str

class UserLoginResponse(BaseModel):
    message: str
    status: bool
    token: str
    type: Optional[str] = "Bearer"

class UserUpdateModel(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    confirm_password: Optional[str]
    
