from common.database.database import Base
from sqlalchemy.orm import Mapped,relationship
from sqlalchemy import DateTime,Column,Integer,String
from datetime import datetime

class USER(Base):
    __tablename__="users"
    __allow_unmapped__=True

    id=Column(Integer,primary_key=True,autoincrement=True,index=True)
    username=Column(String(255),nullable=False)
    email=Column(String(255),nullable=False,unique=True)
    password_hash=Column(String,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow)

    mailboxes=relationship("MAILBOX",back_populates="user",cascade="all, delete-orphan",)