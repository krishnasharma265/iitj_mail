from pydantic import BaseModel 


class Token_Response(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str

