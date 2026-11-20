import pytest
from pydantic import ValidationError

from backend.app.routers import models as api_models


def test_request_models_accept_boundary_values():
    api_models.ChatRequest(message="x" * 2000)
    api_models.QuizzRequest(subject="xy" * 50, number_quizzes=10, number_options=6)
    api_models.SummarizeRequest(text="x" * 5000, max_bullets=10)
    api_models.FlashCardsRequest(topic="x" * 10, number_flashcards=18)


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
def test_request_models_reject_invalid_values(model_name, data):
    with pytest.raises(ValidationError):
        getattr(api_models, model_name)(**data)


def test_response_models_validate_generated_data():
    chat = api_models.ChatResponse(answer="Learn!", model="test-model", tokens_used=12)
    quiz = api_models.QuizzResponse(
        topic="math",
        nb_questions=1,
        quizz=[
            api_models.Quizz(
                question="What is 1 + 1?",
                options=["1", "2"],
                correct=1,
            )
        ],
    )
    summary = api_models.SummarizeResponse(summary=["First point"], word_count=3)
    flashcards = api_models.FlashCardsResponse(
        topic="math",
        flashcards=[api_models.FlashCard(front="Question", back="Answer")],
    )

    assert chat.tokens_used == 12
    assert quiz.quizz[0].correct == 1
    assert summary.summary == ["First point"]
    assert flashcards.flashcards[0].back == "Answer"
