from datetime import datetime, timezone
from sqlalchemy import Column, Integer, JSON, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.services.db.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    email = Column(Text,unique=True,index=True,nullable=False)
    password_hash = Column(Text,nullable=False)
    created_at = Column(DateTime,default=utc_now)
    conversations = relationship('Conversation',back_populates='user')
    quiz = relationship("Quizz",back_populates="user")
    deck = relationship("FlashCardDeck",back_populates="user")
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False,index = True)
    title = Column(Text,nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now)
    messages = relationship("Message",back_populates='conversation',order_by="Message.id")
    user = relationship("User",back_populates="conversations")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    conversation_id = Column(Integer,ForeignKey("conversations.id"),nullable=False,index = True)
    role = Column(Text,nullable=False)
    content = Column(Text,nullable=False)
    tokens_used = Column(Integer,default=0)
    created_at = Column(DateTime,default=utc_now)
    conversation = relationship('Conversation',back_populates="messages")
class Quizz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False,index=True)
    topic = Column(Text,nullable=False)
    created_at = Column(DateTime,default=utc_now)
    questions = relationship('QuizzQuestion',back_populates="quiz")
    user = relationship('User',back_populates="quiz")
class QuizzQuestion(Base):
    __tablename__ = "quizz_questions"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    quizz_id = Column(Integer,ForeignKey("quizzes.id"),nullable=False,index=True)
    question = Column(Text,nullable=False)
    options = Column(JSON,nullable=False)
    correct_index = Column(Integer,nullable=False)
    quiz = relationship("Quizz",back_populates="questions")
class FlashCardDeck(Base):
    __tablename__ = "flashcard_decks"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False,autoincrement=True)
    title = Column(Text,nullable=False)
    created_at = Column(DateTime,default=utc_now)
    flashcard = relationship("FlashCard",back_populates="deck")
    user = relationship("User",back_populates="deck")
class FlashCard(Base):
    __tablename__ = "flashcards"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    deck_id = Column(Integer,ForeignKey("flashcard_decks.id"),nullable=False,index=True)
    back = Column(Text,nullable=False)
    front = Column(Text,nullable=False)
    deck = relationship("FlashCardDeck",back_populates="flashcard")