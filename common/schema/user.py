from pydantic import BaseModel,ConfigDict,EmailStr
from typing import Optional

class CreateUser(BaseModel):
    username: str

    email:EmailStr
    password:str

class LoginUser(BaseModel):
    email:EmailStr
    password:str

class UserUpdate(BaseModel):
    email:Optional[EmailStr]=None
    password: Optional[str]=None
    username: Optional[str] = None

class USEROUT(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    name:str
    email:EmailStr
    name:str
