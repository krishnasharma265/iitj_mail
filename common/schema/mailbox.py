from pydantic import BaseModel,ConfigDict
from typing import Optional

class CREATEMAILBOX(BaseModel):
    user_id:int
    name:str

class UPDATEMAILBOX(BaseModel):
    name:Optional[str]=None

class MAILBOXOUT(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    name:str
    user_id:int