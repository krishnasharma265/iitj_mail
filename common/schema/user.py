from pydantic import BaseModel,Field,EmailStr
from typing import Optional

class CreateUser(BaseModel):
    email:EmailStr
    password:str

class LoginUser(BaseModel):
    email:EmailStr
    password:str

class UserUpdate(BaseModel):
    email:Optional[EmailStr]=None
    password: Optional[str]=None