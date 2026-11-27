from sqlalchemy.orm import Session
from backend.app.services.db.database import SessionLocal
from backend.app.services.db import models

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
def get_all_cnv(db:Session,user_id):
    return db.query(models.Conversation).filter(
        models.Conversation.user_id == user_id
    ).all()
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
    return message.id,conversation.id
def update_title(db:Session,user_id,convesation_id,new_title):
    conversation = get_conversation(db,conversation_id=convesation_id,user_id=user_id)
    if conversation is None:
        raise LookupError("Conversation not found")
    conversation.title = new_title
    db.commit()
    db.refresh(conversation)
    return conversation
def get_messages(db:Session, conversation_id, user_id,limit = None):
    query = (
        db.query(models.Message).join(models.Conversation).filter(
            models.Conversation.id == conversation_id,
            models.Conversation.user_id == user_id
        )
        .order_by(models.Message.id)
    )
    if limit is None:
        return query.all()
    rows = query.order_by(models.Message.id.desc()).limit(limit).all()
    return list(reversed(rows))
def get_quizz(db:Session,quiz_id,user_id):
    return db.query(models.Quizz).filter(
        models.Quizz.id == quiz_id,
        models.Quizz.user_id == user_id
    ).first()

def get_all_quizzes(db: Session, user_id):
    return db.query(models.Quizz).filter(
        models.Quizz.user_id == user_id
    ).all()

def add_quiz(db:Session,user_id,topic):
    quiz = models.Quizz(
        user_id = user_id,
        topic = topic
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz.id
def add_question(db:Session,user_id,quiz_id,question,option,correct_answer):
    if get_quizz(db,quiz_id,user_id) is None:
        raise LookupError("Quiz ID not found")
    question = models.QuizzQuestion(
        quizz_id = quiz_id,
        question = question,
        options = option,
        correct_index =  correct_answer
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question.id
def get_questions(db:Session,quiz_id,user_id):
    if get_quizz(db,quiz_id,user_id) is None:
        raise LookupError("Quiz ID not found")
    return db.query(models.QuizzQuestion).filter(
        models.QuizzQuestion.quizz_id == quiz_id
    ).all()

def get_flashcard_deck(db: Session, deck_id, user_id):
    return db.query(models.FlashCardDeck).filter(
        models.FlashCardDeck.id == deck_id,
        models.FlashCardDeck.user_id == user_id
    ).first()

def get_all_flashcard_decks(db: Session, user_id):
    return db.query(models.FlashCardDeck).filter(
        models.FlashCardDeck.user_id == user_id
    ).all()

def add_deck(db: Session, user_id, title):
    deck = models.FlashCardDeck(
        user_id=user_id,
        title=title
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck.id

def add_flashcard(db: Session, user_id, deck_id, front, back):
    if get_flashcard_deck(db, deck_id, user_id) is None:
        raise LookupError("FlashCard deck ID not found")
    flashcard = models.FlashCard(
        deck_id=deck_id,
        front=front,
        back=back
    )
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)
    return flashcard.id

def get_flashcards(db: Session, deck_id, user_id):
    if get_flashcard_deck(db, deck_id, user_id) is None:
        raise LookupError("FlashCard deck ID not found")
    return db.query(models.FlashCard).filter(
        models.FlashCard.deck_id == deck_id
    ).all()

def get_deck(db: Session, deck_id, user_id):
    return get_flashcard_deck(db, deck_id, user_id)

def add_flashcard_deck(db: Session, user_id, title):
    return add_deck(db, user_id, title)

def add_card(db: Session, user_id, deck_id, front, back):
    return add_flashcard(db, user_id, deck_id, front, back)
def lookup_by_email(db:Session,email):
    return db.query(models.User).filter(models.User.email == email).first()
def delete_conversation(db:Session,conversation_id,user_id):
    conversation = get_conversation(db,conversation_id,user_id)
    if conversation is None:
        raise LookupError("Conversation Not found")
    db.query(models.Message).filter(
        models.Message.conversation_id == conversation.id
    ).delete()
    db.delete(conversation)
    db.commit()
    return True
def delete_user(db:Session,user_id):
    user = db.get(models.User,user_id)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True
    
if __name__ == "__main__":
    print(add_user(SessionLocal(),"ex@example.com","123456"))