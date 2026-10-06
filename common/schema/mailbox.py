from pydantic import BaseModel,Field
from typing import Optional

class CREATEMAILBOX(BaseModel):
    user_id:int
    name:str

class UPDATEMAILBOX(BaseModel):
    name:Optional[str]=None