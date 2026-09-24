from database.database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey,Column,Integer,String

class EMAIL_RECIPIENT(Base):
    __tablename__="email_recipients"
    __allow_unmapped__=True

    id=Column(Integer,primary_key=True)
    email_id=Column(Integer,ForeignKey("emails.id",ondelete="CASCADE"),nullable=False)
    recipient=Column(String(255),nullable=False)
    