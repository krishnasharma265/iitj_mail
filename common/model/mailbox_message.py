from sqlalchemy import Column,Text,Integer,Boolean,String,ForeignKey
from common.database.database import Base

class MAILBOXMESSAGE(Base):
    __tablename__="mailbox_messages"
    __allow_unmapped__=True

    id=Column(Integer,primary_key=True,index=True)

    mailbox_id=Column(Integer,ForeignKey("mailboxes.id",ondelete="CASCADE"),nullable=False)

    email_id=Column(Integer,ForeignKey("emails.id",ondelete="CASCADE"),nullable=False)

    is_read=Column(Boolean,default=False,nullable=False)

    is_deleted = Column(Boolean, default=False,nullable=False)