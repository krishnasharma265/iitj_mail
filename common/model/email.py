from common.database.database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy import Text,DateTime,Column,Integer,String
from datetime import datetime

class EMAIL(Base):
    __tablename__="emails"
    __allow_unmapped__=True

    id=Column(Integer,primary_key=True)
    sender=Column(String(255),nullable=False)
    subject=Column(Text)
    body=Column(Text)
    created_at=Column(DateTime,default=datetime.utcnow)

