from sqlalchemy import Column,Text,Integer,String,ForeignKey
from common.database.database import Base

class MAILBOX(Base):
    __tablename__="mailboxes"
    __allow_unmapped__=True

    id=Column(Integer,primary_key=True,index=True)

    user_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)

    name=Column(String(50),nullable=False)