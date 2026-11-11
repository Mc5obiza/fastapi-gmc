from fastapi import HTTPException,APIRouter
from .models import QuizzResponse,QuizzRequest
from backend.app.services.ai import AIServiceError
from backend.app.services.errors import ai_error_http
from backend.app.services.quizz import generate_quizz
router = APIRouter(prefix="/quizz",tags=["quizz"])
@router.post('/')
def quizz(request:QuizzRequest):
    try:
        subject = request.subject.strip()
        number_questions = request.number_quizzes
        number_options = request.number_options
        response = generate_quizz(subject,number_questions,number_options)
    except AIServiceError as error:
        raise ai_error_http(error)
    return response