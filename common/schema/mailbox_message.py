from pydantic import BaseModel,ConfigDict
from typing import Optional

class CREATEMAILBOX_MESSAGE(BaseModel):
    mailbox_id:int
    email_id:int

class UPDATEMESSAGE_STATUS(BaseModel):
    is_read=Optional[str]=False
    is_deleted=Optional[str]=False

class MESSAGEOUT(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int
    mailbox_id:int
    email_id:int
    is_read:bool
    is_deleted:bool
    


