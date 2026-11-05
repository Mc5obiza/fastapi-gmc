from fastapi import HTTPException,APIRouter
from .models import Quizz,QuizzResponse,QuizzRequest

router = APIRouter(prefix="/quizz",tags=["quizz"])
@router.post('/')
def quizz(request:QuizzRequest):
    questions = []
    for index in range(1,request.number_quizzes+1):
        questions.append(
        Quizz(
                question=f"Question {index} about {request.subject}",
                options= [f"Option {index+1}" for index in range(1,request.number_options+1)],
                correct="Option 1"
        )
        )
    return QuizzResponse(
        topic=request.subject,
        nb_questions=request.number_quizzes,
        quizz=questions
    )