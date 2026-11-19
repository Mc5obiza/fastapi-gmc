from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    email = Column(Text,unique=True,index=True,nullable=False)
    password_hash = Column(Text,nullable=False)
    created_at = Column(DateTime,default=utc_now)
    conversations = relationship('Conversation',back_populates='user')

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False,index = True)
    title = Column(Text,nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now)
    messages = relationship("Message",back_populates='conversation',order_by="Message.id")
    user = relationship("User",back_populates="conversations")

