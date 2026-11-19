from sqlalchemy.orm import Session
from database import SessionLocal
import models

def add_user(db:Session, email,password_hash):
    user = models.User(email=email,password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id

def get_conversation(db:Session,conversation_id, user_id):
    return (
        db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id,
            models.Conversation.user_id == user_id
        ).first()
    )
def add_message(db:Session, user_id, role,content,conversation_id = None,tokens_used = 0):
    if conversation_id is None:
        conversation = models.Conversation(user_id= user_id,title = "New conversation")
        db.add(conversation)
        db.flush()
    else:
        conversation = get_conversation(db,conversation_id,user_id)
        if conversation is None:
            raise LookupError('Conversation not Found')
    message = models.Message(
            conversation_id= conversation.id,
            role = role,
            content = content,
            tokens_used = tokens_used
        )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message.id
def get_messages(db:Session, conversation_id, user_id):
    return (
        db.query(models.Message).join(models.Conversation).filter(
            models.Conversation.id == conversation_id,
            models.Conversation.user_id == user_id
        )
        .order_by(models.Message.id)
        .all()
    )
if __name__ == "__main__":
    print(add_user(SessionLocal(),"ex@example.com","123456"))