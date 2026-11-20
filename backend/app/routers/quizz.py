from fastapi import HTTPException,APIRouter,Depends
from .models import QuizzResponse,QuizzRequest,QuizDetailResponse
from backend.app.services.ai import AIServiceError
from backend.app.services.errors import ai_error_http
from backend.app.services.quizz import generate_quizz
from backend.app.services.db.database import get_db
from backend.app.services.db import crud
from sqlalchemy.orm import Session
router = APIRouter(prefix="/quizz",tags=["quizz"])
CURRENT_USER = 1
@router.post('/',response_model=QuizzResponse)
def quizz(request:QuizzRequest,db : Session=Depends(get_db)):
    try:
        subject = request.subject.strip()
        number_questions = request.number_quizzes
        number_options = request.number_options
        response = generate_quizz(subject,number_questions,number_options)
        quiz_id = crud.add_quiz(db,CURRENT_USER,request.subject)
        for question in response.quizz:
            crud.add_question(db,CURRENT_USER,quiz_id,question.question,question.options,correct_answer=question.correct)
    except AIServiceError as error:
        raise ai_error_http(error)
    return response

@router.get("/{quiz_id}", response_model=QuizDetailResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = crud.get_quizz(db, quiz_id, CURRENT_USER)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = crud.get_questions(db, quiz_id, CURRENT_USER)
    return _format_quiz(quiz, questions)

@router.get("/", response_model=list[QuizDetailResponse])
def get_all_quizzes(db: Session = Depends(get_db)):
    quizzes = crud.get_all_quizzes(db, CURRENT_USER)
    return [
        _format_quiz(
            quiz,
            crud.get_questions(db, quiz.id, CURRENT_USER),
        )
        for quiz in quizzes
    ]

def _format_quiz(quiz, questions):
    return {
        "id": quiz.id,
        "topic": quiz.topic,
        "nb_questions": len(questions),
        "quizz": [
            {
                "question": question.question,
                "options": question.options,
                "correct": question.correct_index,
            }
            for question in questions
        ],
    }
