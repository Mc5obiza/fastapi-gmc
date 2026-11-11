import pytest
from pydantic import ValidationError

from backend.app.routers import models as api_models
from backend.app.services import models as service_models


@pytest.mark.parametrize("models", [api_models, service_models])
def test_request_models_accept_boundary_values(models):
    models.ChatRequest(message="x" * 2000)
    models.QuizzRequest(subject="xy" * 50, number_quizzes=10, number_options=6)
    models.SummarizeRequest(text="x" * 5000, max_bullets=10)
    models.FlashCardsRequest(topic="x" * 10, number_flashcards=18)


@pytest.mark.parametrize("models", [api_models, service_models])
@pytest.mark.parametrize(
    ("model_name", "data"),
    [
        ("ChatRequest", {"message": ""}),
        ("ChatRequest", {"message": "x" * 2001}),
        ("ChatRequest", {"message": None}),
        ("QuizzRequest", {"subject": "x"}),
        ("QuizzRequest", {"subject": "x" * 101}),
        ("QuizzRequest", {"subject": "math", "number_quizzes": 2}),
        ("QuizzRequest", {"subject": "math", "number_quizzes": 11}),
        ("QuizzRequest", {"subject": "math", "number_options": 3}),
        ("QuizzRequest", {"subject": "math", "number_options": 7}),
        ("SummarizeRequest", {"text": "x" * 19}),
        ("SummarizeRequest", {"text": "x" * 5001}),
        ("SummarizeRequest", {"text": "x" * 20, "max_bullets": 2}),
        ("SummarizeRequest", {"text": "x" * 20, "max_bullets": 11}),
        ("FlashCardsRequest", {"topic": "xy"}),
        ("FlashCardsRequest", {"topic": "x" * 11}),
        ("FlashCardsRequest", {"topic": "math", "number_flashcards": 6}),
        ("FlashCardsRequest", {"topic": "math", "number_flashcards": 19}),
    ],
)
def test_request_models_reject_invalid_values(models, model_name, data):
    with pytest.raises(ValidationError):
        getattr(models, model_name)(**data)


@pytest.mark.parametrize("models", [api_models, service_models])
def test_response_models_validate_generated_data(models):
    chat = models.ChatResponse(answer="Learn!", model="test-model", tokens_used=12)
    quiz = models.QuizzResponse(
        topic="math",
        nb_questions=1,
        quizz=[
            models.Quizz(
                question="What is 1 + 1?",
                options=["1", "2"],
                correct="2",
            )
        ],
    )
    summary = models.SummarizeResponse(summary=["First point"], word_count=3)
    flashcards = models.FlashCardsResponse(
        topic="math",
        flashcards=[models.FlashCard(front="Question", back="Answer")],
    )

    assert chat.tokens_used == 12
    assert quiz.quizz[0].correct in quiz.quizz[0].options
    assert summary.summary == ["First point"]
    assert flashcards.flashcards[0].back == "Answer"
